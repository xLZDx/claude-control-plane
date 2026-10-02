def prices_match(posted: float, expected: float, tol: float = 1.0) -> bool:
    return abs(posted - expected) <= tol
