"""Display helpers for the Streamlit app."""


def format_inr(amount, decimals=0):
    """Format a number in Indian style with the rupee sign.

    Example: 5000000 -> '₹50,00,000', -1234.5 -> '-₹1,235'.
    """
    sign = "-" if amount < 0 else ""
    text = f"{abs(amount):.{decimals}f}"
    int_part, _, frac = text.partition(".")
    if len(int_part) > 3:
        last3, rest = int_part[-3:], int_part[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        int_part = ",".join(groups + [last3])
    out = f"{sign}₹{int_part}"
    return f"{out}.{frac}" if frac else out


def format_pct(value, decimals=2):
    """0.0725 -> '7.25%'."""
    return f"{value * 100:.{decimals}f}%"
