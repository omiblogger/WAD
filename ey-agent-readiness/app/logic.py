"""Small, testable business functions. Read these before asking AI to rewrite them."""

def calculate_emi(principal: float, annual_rate: float, years: int) -> float:
    """Monthly EMI; annual_rate is a percentage, e.g. 8.5, not 0.085."""
    if principal <= 0 or annual_rate < 0 or years <= 0:
        raise ValueError("principal and years must be positive; rate cannot be negative")
    months = years * 12
    monthly_rate = annual_rate / 1200
    if monthly_rate == 0:
        return round(principal / months, 2)
    factor = (1 + monthly_rate) ** months
    return round(principal * monthly_rate * factor / (factor - 1), 2)
