# ML Engineer — Reference Material

Loaded on demand from `SKILL.md`. Contains worked code examples, known BUG patterns, BryceMeng cross-references.

## Technique 1 — Triple Barrier Method (AFML Ch. 3)

### Correct implementation

```python
# ATR applied ONCE - barriers scale linearly with volatility
atr = df['high'].rolling(14).max() - df['low'].rolling(14).min()  # vectorized
dynamic_tp = pt_multiplier * atr   # pt=2.5
dynamic_sl = sl_multiplier * atr   # sl=1.5  (asymmetric R/R = 1.67)
```

### BUG-1 — what to REJECT

```python
# WRONG: vol_norm = atr / atr_mean -> dynamic_tp = pt * atr * vol_norm = pt * atr^2 / atr_mean
# In 2x volatile regime: barriers are 4x wider.
# In 0.5x regime: 0.25x (dangerously tight).
```

### Cross-check mandates

- Vectorized, no Python loops. Timing gate: <5s on 10k bars on local hardware.
- BryceMeng Standard Bars notebook: `ml.data_structures_snapshot_tick.get_dollar_bars()` — adopt dollar/volume/tick bar patterns for data ingestion instead of time bars.
- Parameters: `pt_multiplier=2.5, sl_multiplier=1.5, max_bars=12` (NOT 2.0/2.0/24).
- Timeout label=0 → negative class (NOT dropped). See AFML Ch.3.

## Technique 2 — Fractional Differentiation (AFML Ch. 5)

### Correct implementation

```python
from mlfinlab.features.fracdiff import frac_diff_ffd

# d-value must be found per asset via ADF sweep - NOT hardcoded
# Expected range for BTC/ETH: d in [0.35, 0.45]
# Accept d if ADF p-value < 0.05 AND correlation with original series > 0.97
d_optimal = adf_sweep(series, d_range=(0.1, 0.5), step=0.05)
frac_diff_d40 = frac_diff_ffd(close_series, d=d_optimal)
```

### Mandate

- Never hardcode `d=0.40` without running ADF sweep on the actual asset + timeframe.
- The feature `frac_diff_d40` in META_FEATURES must use the per-asset optimal d, validated quarterly.

## Technique 3 — Purged K-Fold with Embargo (AFML Ch. 7)

### Correct implementation

```python
def split(self, X, y=None, groups=None):
    ...
    for fold in folds:
        test_start, test_end = fold
        # PURGE: remove training samples whose label spans into the test window
        train_mask = self.t1.iloc[train_idx].values < test_start
        train_idx = train_idx[train_mask]
        # EMBARGO: remove samples whose bar is within embargo_pct of test_start
        embargo_end = test_start + embargo_td
        train_idx = train_idx[X.index[train_idx] < (test_start - embargo_td)]
        yield train_idx, test_idx
```

### BUG-2 — what to REJECT

```python
# WRONG: self.t1 is accepted in __init__ but NEVER READ in split()
# Result: temporal leakage - walk-forward Sharpe numbers are optimistic
```

### Mandate

- After implementing t1-span purging: run on synthetic dataset (1000 samples, known leakage) and assert `len(train_idx_purged) < len(train_idx_original)`.

## Technique 4 — Meta-Labeling (AFML Ch. 3)

### Unified feature list (23 features — NEVER split between training and inference)

```python
# Must live in src/utils/meta_config.py - both training and inference import from here
META_FEATURES: list[str] = [
    'prob_base', 'prob_trend', 'regime', 'primary_signal',
    'frac_diff_d40', 'volatility_7', 'rsi_14', 'macd_hist', 'bb_pb',
    'ofi_z', 'vwap_dist', 'funding_z', 'funding_positive',
    'liq_proximity', 'kc_width', 'don_pos_20', 'hour', 'day_of_week',
    'taker_buy_ratio', 'atr_pct', 'signal_rsi', 'signal_macd', 'signal_bb',
]
CONFIDENCE_THRESHOLD: float = 0.60  # default; load optimal_threshold from meta JSON at inference
```

### BUG-3 — what to REJECT

- Training: 13 features. Inference: 20 different features. They don't overlap. Silent `except Exception -> PASS` hides the mismatch.

### Correct model pipeline

```python
model = HistGradientBoostingClassifier(class_weight='balanced', ...)
calibrated = CalibratedClassifierCV(model, method='isotonic', cv=purged_kfold)
# Threshold search: sweep [0.40, 0.70] step 0.01 on OOS validation set, maximize Sortino ratio
# Store optimal_threshold in meta JSON alongside model artifact
```

### Mandate

- `primary_signal` must be written as a column (not inferred at runtime).
- `tb_label == 0` rows → `meta_label = 0`, NOT dropped.
- `optimal_threshold` loaded from meta JSON at inference, NOT hardcoded 0.60.

## Technique 5 — Bar Construction (BryceMeng Chapter 2 Patterns)

```python
# Dollar bars (preferred over time bars for ML - reduces volatility clustering)
from mlfinlab.data_structures import get_dollar_bars, get_volume_bars, get_tick_bars

dollar_bars = get_dollar_bars(tick_file, threshold=1_000_000_000, batch_size=1_000_000)
volume_bars = get_volume_bars(tick_file, threshold=28_000, batch_size=1_000_000)

# Futures roll adjustment (BryceMeng Futures Roll.ipynb pattern)
from mlfinlab.multi_product import get_futures_roll_series
# Absolute method: continuous_contract['close'] -= roll_gaps
# Relative method: continuous_contract['close'] /= roll_gaps_relative
```

## Silent Failure correction pattern

Any `except Exception` in ML inference code that returns `('PASS', 0.5)` is a **CRITICAL silent bug** — every inference error silently passes trades through. Required pattern:

```python
except Exception as e:
    logger.error("Meta-labeler inference error: %s", e, exc_info=True)  # ERROR not DEBUG
    return 'BLOCK', 0.0  # fail CLOSED, not open
```

## Optuna CIO Agent integration

Dashboard runs at `http://localhost:8080` after:

```bash
optuna-dashboard sqlite:///data/optuna_orchestrator.db
```

The `src/engine/cio_agent.py` objective function must:

1. Accept `(timeframe, train_window_days, pt_multiplier, sl_multiplier)` as trial parameters.
2. Run walk-forward backtest via the existing pipeline.
3. Gate on `max_dd <= 0.15` (prune trial if breached).
4. Return OOS Sortino ratio (NOT Sharpe — Sortino penalizes downside only).
5. Apply Deflated Sharpe Ratio correction before trusting best trial.

Reference: `<optuna-dashboard source>` for dashboard integration patterns.

## Known bugs (as of 2026-05-13)

| BUG | File | Description |
|---|---|---|
| BUG-1 | `src/analysis/triple_barrier.py` | ATR squaring via vol_norm intermediate |
| BUG-2 | `src/utils/purged_kfold.py` | `self.t1` stored in `__init__` but never read in `split()` |
| BUG-3 | `src/engine/train_meta_labeler.py` / `src/analysis/meta_labeler.py` | 13 features vs 20 features mismatch; silent fail-open |
| BUG-4 | `src/engine/train_meta_labeler.py` | Timeout rows (`tb_label==0`) dropped instead of kept as negative |
