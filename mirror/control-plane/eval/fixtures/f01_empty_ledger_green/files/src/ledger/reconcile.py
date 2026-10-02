from decimal import Decimal


def reconcile(expected: list[Decimal], actual: list[Decimal]) -> dict:
    mismatches = [e for e, a in zip(expected, actual) if e != a]
    return {"ok": not mismatches, "checked": len(mismatches)}
