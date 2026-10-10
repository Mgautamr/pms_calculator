from app.formatting import format_inr, format_pct


def test_format_inr_lakhs_and_crores():
    assert format_inr(0) == "₹0"
    assert format_inr(999) == "₹999"
    assert format_inr(1000) == "₹1,000"
    assert format_inr(5_000_000) == "₹50,00,000"
    assert format_inr(123_456_789) == "₹12,34,56,789"


def test_format_inr_negative_and_decimals():
    assert format_inr(-1234.6) == "-₹1,235"
    assert format_inr(1234.5, decimals=2) == "₹1,234.50"


def test_format_pct():
    assert format_pct(0.0725) == "7.25%"
