#!/usr/bin/env python3
"""Read-only Cyrillic inventory of committed text in local Git repositories.

The script does not clone, fetch, modify, translate, publish, or delete files.
It reads Git blobs at a pinned HEAD, never the potentially dirty worktree.
Only paths, hashes, classification, and character counts appear in output.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

CYRILLIC = re.compile(r"[\u0400-\u052F]")
TEXT_SUFFIXES = frozenset({
    ".md", ".mdx", ".markdown", ".rst", ".txt", ".html", ".htm",
    ".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".dart",
    ".ps1", ".psm1", ".sh", ".bash", ".bat", ".cmd", ".sql",
    ".yml", ".yaml", ".json", ".jsonl", ".toml", ".xml", ".arb",
    ".css", ".scss", ".vue", ".feature", ".ini", ".cfg", ".properties",
})
DOC_SUFFIXES = frozenset({".md", ".mdx", ".markdown", ".rst", ".txt", ".html", ".htm"})
CODE_SUFFIXES = frozenset({
    ".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".dart", ".ps1",
    ".psm1", ".sh", ".bash", ".bat", ".cmd", ".sql", ".css", ".scss", ".vue",
})


def git(repo: Path, *args: str) -> bytes:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return proc.stdout


def classify(path: str) -> str:
    p = path.replace("\\", "/").lower()
    suffix = Path(p).suffix
    parts = p.split("/")
    if p.startswith(("reports/", "governance/reviews/", "evidence/")) or p.endswith(
        ("decision_log.md", "decisions.md")
    ):
        return "HISTORICAL_OR_EVIDENCE_REVIEW"
    if suffix in (".arb", ".json", ".yaml", ".yml", ".jsonl") and (
        "l10n" in parts or "locales" in parts or "i18n" in parts
        or "assets" in parts or "fixtures" in parts or "testdata" in parts
    ):
        return "LOCALE_OR_STRUCTURED_DATA_PRESERVE"
    if suffix in CODE_SUFFIXES:
        return "CODE_COMMENTS_OR_STRINGS_REVIEW"
    if suffix in DOC_SUFFIXES or suffix == ".feature":
        return "TRANSLATABLE_PROSE_REVIEW"
    return "STRUCTURED_CONTENT_REVIEW"


def decode_text(data: bytes) -> str | None:
    if b"\x00" in data[:4096] and not data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return None
    try:
        if data.startswith((b"\xff\xfe", b"\xfe\xff")):
            return data.decode("utf-16")
        return data.decode("utf-8-sig")
    except UnicodeError:
        return None


def scan(repo: Path, max_bytes: int) -> dict[str, object]:
    head = git(repo, "rev-parse", "HEAD").decode("ascii").strip()
    tree = git(repo, "ls-tree", "-r", "-l", "-z", head)
    candidates: list[tuple[str, str, int]] = []
    skipped_large: list[str] = []
    for entry in tree.split(b"\x00"):
        if not entry or b"\t" not in entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        fields = metadata.split()
        if len(fields) != 4 or fields[1] != b"blob":
            continue
        path = raw_path.decode("utf-8", errors="replace")
        if Path(path).suffix.lower() not in TEXT_SUFFIXES:
            continue
        if fields[3] == b"-":
            continue
        size = int(fields[3])
        if size > max_bytes:
            skipped_large.append(path)
        else:
            candidates.append((path, fields[2].decode("ascii"), size))

    results: list[dict[str, object]] = []
    skipped_decode: list[str] = []
    skipped_lfs: list[str] = []
    if candidates:
        process = subprocess.Popen(
            ["git", "-C", str(repo), "cat-file", "--batch"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        )
        try:
            assert process.stdin is not None and process.stdout is not None
            for path, sha, listed_size in candidates:
                process.stdin.write((sha + "\n").encode("ascii"))
                process.stdin.flush()
                header = process.stdout.readline()
                fields = header.split()
                if len(fields) != 3 or fields[1] != b"blob":
                    raise RuntimeError("GIT_BLOB_READ_FAILED")
                size = int(fields[2])
                if size != listed_size or size > max_bytes:
                    raise RuntimeError("GIT_BLOB_SIZE_CHANGED")
                data = process.stdout.read(size)
                if len(data) != size or process.stdout.read(1) != b"\n":
                    raise RuntimeError("GIT_BLOB_TRUNCATED")
                if data.startswith(b"version https://git-lfs.github.com/spec/v1\n"):
                    # The tracked blob is an LFS pointer, not the actual content.
                    skipped_lfs.append(path)
                    continue
                value = decode_text(data)
                if value is None:
                    skipped_decode.append(path)
                    continue
                matches = len(CYRILLIC.findall(value))
                if matches:
                    results.append({
                        "path": path,
                        "blob_sha": sha,
                        "cyrillic_characters": matches,
                        "classification": classify(path),
                        "bytes": size,
                    })
            process.stdin.close()
            if process.wait(timeout=30) != 0:
                raise RuntimeError("GIT_BATCH_FAILED")
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()

    results.sort(key=lambda item: str(item["path"]))
    return {
        "repository": repo.name,
        "head": head,
        "text_files_scanned": len(candidates),
        "matches": results,
        "match_count": len(results),
        "skipped_too_large": sorted(skipped_large),
        "skipped_non_utf8_or_binary": sorted(skipped_decode),
        "skipped_lfs_pointer": sorted(skipped_lfs),
        "is_complete": not skipped_large and not skipped_decode and not skipped_lfs,
        "warning": (
            "Contains Git-tracked committed blobs at one HEAD only. "
            "Does not audit other branches, Issues, PRs, review threads, or locale semantics. "
            "Cyrillic detection is not proof that text is appropriate to translate."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repositories", metavar="REPO", nargs="+", type=Path)
    parser.add_argument(
        "--max-blob-bytes", type=int, default=750_000,
        help="Maximum file size inspected, default 750000; oversized paths are listed.",
    )
    parser.add_argument(
        "--output", type=Path, default=None,
        help="Optional JSON report path; no source text or credentials are stored.",
    )
    args = parser.parse_args()
    if args.max_blob_bytes <= 0:
        parser.error("--max-blob-bytes must be positive")
    reports: list[dict[str, object]] = []
    for root in args.repositories:
        try:
            reports.append(scan(root.resolve(), args.max_blob_bytes))
        except (OSError, subprocess.CalledProcessError, RuntimeError, ValueError) as exc:
            reports.append({
                "repository": root.name,
                "error_type": type(exc).__name__,
                "is_complete": False,
            })
    summary = {
        "schema_version": 1,
        "reports": reports,
        "all_scans_complete": all(report.get("is_complete") is True for report in reports),
    }
    serialized = json.dumps(summary, ensure_ascii=True, indent=2) + "\n"
    if args.output is None:
        sys.stdout.write(serialized)
    else:
        args.output.write_text(serialized, encoding="utf-8")
        print(f"Inventory saved to {args.output}; no source content included")
    return 0 if summary["all_scans_complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
