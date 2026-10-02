from decimal import Decimal


def with_tax(net: str, rate: float) -> Decimal:
    return Decimal(net) * (1 + Decimal(rate))
