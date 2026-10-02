from ledger.reconcile import reconcile


def test_reconcile_runs():
    result = reconcile([], [])
    assert result is not None


def test_reconcile_mismatch():
    result = reconcile([1], [2])
    assert result
