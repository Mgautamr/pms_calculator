"""Portfolio analytics: CAGR, XIRR, volatility, max drawdown, Sharpe.

Conventions (these match Excel, and the reference workbook):
- Years are counted as days / 365.
- XIRR discounts each cash flow by (days since the first date) / 365.
- Volatility is the sample standard deviation (Excel STDEV.S) of period returns,
  scaled to a year by sqrt(periods per year).
- Sharpe ratio = (annual return - risk-free rate) / annual volatility.
  The risk-free rate is always passed in; nothing is hard-coded.
"""
import math
import statistics


def cagr(start_value, end_value, days):
    """Compound annual growth rate over `days` calendar days."""
    if start_value <= 0 or end_value <= 0:
        raise ValueError("start and end values must be positive")
    if days <= 0:
        raise ValueError("days must be positive")
    return (end_value / start_value) ** (365 / days) - 1


def xirr(cashflows):
    """Annualised return for dated cash flows, [(date, amount), ...].

    Money invested is negative, money received (including the final value) is
    positive. Solved by bisection, so it does not depend on a starting guess.
    """
    flows = sorted(cashflows, key=lambda x: x[0])
    if len(flows) < 2:
        raise ValueError("need at least two cash flows")
    amounts = [a for _, a in flows]
    if not (any(a > 0 for a in amounts) and any(a < 0 for a in amounts)):
        raise ValueError("cash flows need at least one positive and one negative amount")
    start = flows[0][0]
    years = [((d - start).days) / 365 for d, _ in flows]

    def npv(rate):
        return sum(a / (1 + rate) ** t for a, t in zip(amounts, years))

    low, high = -0.999999, 1.0
    while npv(low) * npv(high) > 0 and high < 1e6:
        high *= 2
    if npv(low) * npv(high) > 0:
        raise ValueError("could not find a rate that balances the cash flows")
    for _ in range(300):
        mid = (low + high) / 2
        if npv(low) * npv(mid) <= 0:
            high = mid
        else:
            low = mid
    return (low + high) / 2


def period_returns(values):
    """Simple return for each period: value[t] / value[t-1] - 1."""
    if len(values) < 2:
        raise ValueError("need at least two values")
    return [values[i] / values[i - 1] - 1 for i in range(1, len(values))]


def volatility(returns, periods_per_year):
    """Annualised volatility from period returns (sample standard deviation)."""
    if len(returns) < 2:
        raise ValueError("need at least two returns")
    return statistics.stdev(returns) * math.sqrt(periods_per_year)


def max_drawdown(values):
    """Largest fall from a running peak, as a negative fraction (0 if never below a peak)."""
    if not values:
        raise ValueError("need at least one value")
    peak = values[0]
    worst = 0.0
    for v in values:
        peak = max(peak, v)
        worst = min(worst, v / peak - 1)
    return worst


def sharpe_ratio(annual_return, risk_free_rate, annual_volatility):
    """(annual return - risk-free rate) / annual volatility."""
    if annual_volatility == 0:
        raise ValueError("volatility is zero, Sharpe ratio is undefined")
    return (annual_return - risk_free_rate) / annual_volatility


def summarize(dates, values, risk_free_rate, periods_per_year=12):
    """All the headline numbers for a dated value series."""
    if len(dates) != len(values):
        raise ValueError("dates and values must have the same length")
    days = (dates[-1] - dates[0]).days
    annual_return = cagr(values[0], values[-1], days)
    vol = volatility(period_returns(values), periods_per_year)
    return {
        "years": days / 365,
        "cagr": annual_return,
        "volatility": vol,
        "max_drawdown": max_drawdown(values),
        "sharpe": sharpe_ratio(annual_return, risk_free_rate, vol),
    }
