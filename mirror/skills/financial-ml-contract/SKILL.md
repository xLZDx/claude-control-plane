---
name: financial-ml-contract
description: Shared evidence and methodology contract for financial-ML work in the trading repository.
---
# Financial ML contract

Treat every method as conditional on the actual prediction target, data-generating process, execution horizon and evaluation design. Do not turn a book/library recipe into a universal rule.

## Evidence hierarchy
1. Current repository data contracts, labels, timestamps and live execution semantics.
2. Reproducible tests/backtests with leakage controls and realistic costs.
3. Primary paper/book/library documentation for the specific method in use.
4. Secondary examples only as orientation, never as ground truth.

## Mandatory checks when relevant
- **Temporal integrity:** every feature is available at decision time; joins/resampling/normalization do not leak future data.
- **Label overlap:** choose a split/purge/embargo design that matches the label horizon and overlap. Do not require Purged K-Fold when ordinary temporal splitting is already valid; do not use random IID splitting when overlap/time dependence makes it invalid.
- **Out-of-sample nesting:** thresholds, feature selection, calibration, meta-model inputs and hyperparameters are learned inside the training portion only.
- **Meta-labeling:** define primary decision, meta target and training data explicitly. Do not assume one canonical side/size formulation if the repository uses another coherent formulation.
- **Stationarity/transforms:** test the actual feature behavior. Fractional differentiation is an option, not a mandatory preprocessing step; raw levels/returns/other transforms may be valid depending on model and target.
- **Event sampling/bars:** CUSUM and information-driven bars are optional hypotheses. Require measured benefit before adding complexity.
- **Metrics:** separate predictive metrics from trading metrics. Include costs/slippage/turnover and uncertainty; do not infer economic edge from accuracy alone.
- **Backtest multiplicity:** call out repeated tuning/selection on the same validation history and selection bias.
- **Reproducibility:** record data window, symbols, seeds where meaningful, code/artifact version and exact evaluation protocol.

## No dogma
Do not prescribe fixed values such as an embargo percentage, ADF threshold, fractional-differencing `d`, truncation tolerance, Kelly sizing or annualization constant unless they are justified by the current experiment and source. Label such values `HYPOTHESIS` until measured/decided.
