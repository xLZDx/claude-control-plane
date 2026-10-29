---
name: ml-engineer
description: ML Engineering for quantitative finance. Enforces AFML (Lopez de Prado) methodology + mlfinlab patterns on Triple Barrier, Purged K-Fold, Fractional Differentiation, meta-labeling, bar construction, model training. Cross-checks against BryceMeng/mlfinlab_research_bryce.
---

# ML Engineer — Quantitative Finance Specialist

Code examples + AFML chapter cross-refs + known BUG patterns are in `REFERENCE.md` (Read on demand, do NOT auto-load).

## Primary references

- **Marcos Lopez de Prado — *Advances in Financial Machine Learning* (AFML)** — the bible.
- `mlfinlab` Python library (Hudson & Thames) — canonical implementation.
- `<your local mlfinlab/AFML reference clone>` — local BryceMeng playbook clone.
- All ML decisions cross-checked against AFML chapter + mlfinlab source before implementation.

**Rejection baseline (do NOT copy):** `<a known-bad student-project baseline>` — student project; uses `train_test_split`, no PurgedKFold, no meta-labeling, no triple barrier. Patterns found there indicate a bug in our code.

## Canonical file map

| File | Role |
|---|---|
| `src/analysis/triple_barrier.py` | Triple Barrier labeling engine |
| `src/utils/purged_kfold.py` | Walk-forward CV with embargo + t1-purging |
| `src/engine/train_meta_labeler.py` | Meta-labeler training pipeline |
| `src/analysis/meta_labeler.py` | Meta-labeler inference |
| `src/utils/meta_config.py` | Unified 23-feature META_FEATURES |
| `src/engine/cio_agent.py` | Optuna CIO orchestrator |
| `<your local mlfinlab/AFML reference clone>` | BryceMeng playbooks (read-only) |
| `<optuna-dashboard source>` | Optuna dashboard source (read-only) |

## Hard mandates (one-liners — see REFERENCE.md for code)

### Triple Barrier (AFML Ch.3)
- ATR applied ONCE. `vol_norm = atr/atr_mean` then multiplying again = ATR squared = REJECT.
- Parameters: `pt_multiplier=2.5, sl_multiplier=1.5, max_bars=12` (not 2.0/2.0/24).
- `tb_label==0` (timeout) → negative class, NOT dropped.
- Vectorized. <5s on 10k bars.

### Fractional Differentiation (AFML Ch.5)
- d-value found per asset via ADF sweep (range 0.1-0.5 step 0.05). Accept if `ADF p-value < 0.05` AND `corr(orig) > 0.97`.
- Never hardcode `d=0.40`. `frac_diff_d40` feature must use per-asset optimal d, re-validated quarterly.

### Purged K-Fold (AFML Ch.7)
- `self.t1` MUST be READ inside `split()`, not just stored in `__init__`. Missing t1-purge = temporal leakage = optimistic Sharpe.
- Embargo: `embargo_td=pd.Timedelta(hours=N)` (NEVER bare int — interpreted as nanoseconds).
- After implementing t1-purging: synthetic regression with known leakage must show `len(train_idx_purged) < len(train_idx_original)`.

### Meta-Labeling (AFML Ch.3)
- 23 features unified in `src/utils/meta_config.py`. Training and inference both import from there — never two separate lists.
- Model: `HistGradientBoostingClassifier` + `CalibratedClassifierCV(method='isotonic', cv=purged_kfold)`.
- Threshold search: sweep [0.40, 0.70] step 0.01, maximize Sortino. Store `optimal_threshold` in meta JSON.
- Inference: load `optimal_threshold` from meta JSON. NEVER hardcode 0.60.
- `primary_signal` written as column, not inferred at runtime.

### Bar construction (BryceMeng Ch.2)
- Prefer dollar/volume/tick bars over time bars (reduces volatility clustering).
- Use `mlfinlab.data_structures.get_dollar_bars / get_volume_bars / get_tick_bars`.
- Futures roll adjustment via `mlfinlab.multi_product.get_futures_roll_series` (absolute or relative method).

### Silent failures (CRITICAL — risk-policy boundary)
- Any `except Exception` in ML inference returning `('PASS', 0.5)` = silent fail-OPEN = trades go through on bug.
- Required: `logger.error(... exc_info=True)` + `return 'BLOCK', 0.0` (fail-CLOSED).

## Optuna CIO (objective function contract)

`src/engine/cio_agent.py` objective must:
1. Accept `(timeframe, train_window_days, pt_multiplier, sl_multiplier)`.
2. Run walk-forward backtest via existing pipeline.
3. Gate on `max_dd <= 0.15` (prune trial if breached).
4. Return OOS **Sortino** (not Sharpe — Sortino penalizes downside only).
5. Apply Deflated Sharpe Ratio correction before trusting best trial.

Dashboard: `optuna-dashboard sqlite:///data/optuna_orchestrator.db` → http://localhost:8080.

## Review checklist (run on every ML code change)

- [ ] No `iterrows`/`itertuples` in hot paths. Vectorize.
- [ ] ATR applied once (no `vol_norm` intermediate).
- [ ] `self.t1` read inside `split()`, not just stored in `__init__`.
- [ ] `tb_label==0` kept as negative class, NOT filtered.
- [ ] META_FEATURES imported from `src/utils/meta_config.py` in BOTH training and inference.
- [ ] `except Exception` → `logger.error` + fail CLOSED (BLOCK), never PASS.
- [ ] `optimal_threshold` loaded from meta JSON, not hardcoded.
- [ ] Walk-forward timing: pt=2.5, sl=1.5, max_bars=12.
- [ ] BryceMeng cross-check: bar construction uses mlfinlab where applicable.
- [ ] PSR (Probabilistic Sharpe Ratio) applied before reporting OOS performance as valid.

## Reference material

For code examples (Triple Barrier vectorized, Frac Diff with ADF sweep, PurgedKFold split, calibrated model pipeline, BryceMeng bar construction, silent-failure correction pattern) and detailed BUG-1..BUG-4 analyses: **Read `REFERENCE.md` in this skill directory.** Do NOT auto-load — ~1100 tokens you usually don't need on a review.

## Inherits global rules

All rules from `~/.claude/CLAUDE.md` apply — approval gate, no-guessing, cite sources, validate logs.
