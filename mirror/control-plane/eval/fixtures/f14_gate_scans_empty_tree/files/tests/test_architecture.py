import ast
from pathlib import Path


def test_no_wallclock_outside_clock():
    offenders = []
    for path in Path("src/missing_dir").rglob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr == "now":
                offenders.append(str(path))
    assert offenders == []
