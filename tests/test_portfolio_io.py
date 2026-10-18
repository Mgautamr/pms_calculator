import io
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from app.portfolio_io import DataError, align, infer_periods_per_year, parse_series, rebase
from engine.analytics import summarize

ROOT = Path(__file__).resolve().parents[1]


def csv(text):
    return io.StringIO(text.strip() + "\n")


def test_parses_iso_dates_and_sorts():
    df = parse_series(csv("date,value\n2025-03-31,110\n2025-01-31,100\n2025-02-28,105"))
    assert list(df["date"].dt.date) == [date(2025, 1, 31), date(2025, 2, 28), date(2025, 3, 31)]
    assert list(df["value"]) == [100, 105, 110]


def test_parses_day_first_dates():
    df = parse_series(csv("date,value\n31-01-2025,100\n28-02-2025,105\n31-03-2025,110"))
    assert df["date"].iloc[0].date() == date(2025, 1, 31)


def test_accepts_comma_thousands_and_nav_column_and_messy_headers():
    df = parse_series(csv('Date , NAV \n2025-01-31,"1,000.50"\n2025-02-28,"1,010"\n2025-03-31,"1,020"'))
    assert df["value"].iloc[0] == 1000.5


@pytest.mark.parametrize("text, fragment", [
    ("when,value\n2025-01-31,1\n2025-02-28,2\n2025-03-31,3", "'date' column"),
    ("date,amount\n2025-01-31,1\n2025-02-28,2\n2025-03-31,3", "'value' column"),
    ("date,value\n2025-01-31,100\nsoon,105\n2025-03-31,110", "row(s) [3]"),
    ("date,value\n2025-01-31,100\n2025-02-28,abc\n2025-03-31,110", "row(s) [3]"),
    ("date,value\n2025-01-31,100\n2025-02-28,-5\n2025-03-31,110", "positive"),
    ("date,value\n2025-01-31,100\n2025-01-31,105\n2025-03-31,110", "only once"),
    ("date,value\n2025-01-31,100\n2025-02-28,105", "at least 3"),
    ("", "could not be read"),
])
def test_bad_files_give_a_helpful_error(text, fragment):
    with pytest.raises(DataError) as err:
        parse_series(csv(text))
    assert fragment in str(err.value)


def test_streamlit_style_upload_object_works():
    class FakeUpload:
        def getvalue(self):
            return b"date,value\n2025-01-31,100\n2025-02-28,105\n2025-03-31,110\n"
    df = parse_series(FakeUpload())
    assert len(df) == 3


@pytest.mark.parametrize("dates, expected", [
    (pd.bdate_range("2025-01-01", periods=60), 252),
    (pd.date_range("2025-01-03", periods=20, freq="7D"), 52),
    (pd.date_range("2025-01-31", periods=12, freq="ME"), 12),
    (pd.date_range("2025-03-31", periods=8, freq="QE"), 4),
    (pd.date_range("2020-12-31", periods=5, freq="YE"), 1),
])
def test_infer_periods_per_year(dates, expected):
    assert infer_periods_per_year(dates) == expected


def test_align_keeps_only_shared_dates():
    a = parse_series(csv("date,value\n2025-01-31,100\n2025-02-28,105\n2025-03-31,110\n2025-04-30,112"))
    b = parse_series(csv("date,value\n2025-02-28,50\n2025-03-31,51\n2025-04-30,52\n2025-05-31,53"))
    pa, pb = align(a, b)
    assert list(pa["date"]) == list(pb["date"]) and len(pa) == 3
    assert list(pa["value"]) == [105, 110, 112]


def test_align_needs_three_shared_dates():
    a = parse_series(csv("date,value\n2025-01-31,100\n2025-02-28,105\n2025-03-31,110"))
    b = parse_series(csv("date,value\n2025-03-31,1\n2025-04-30,2\n2025-05-31,3"))
    with pytest.raises(DataError):
        align(a, b)


def test_rebase_starts_at_100():
    assert rebase([50, 55, 25]) == pytest.approx([100, 110, 50])


def test_sample_files_load_and_give_sensible_numbers():
    p = parse_series(ROOT / "data" / "sample_portfolio.csv")
    b = parse_series(ROOT / "data" / "sample_benchmark.csv")
    pa, ba = align(p, b)
    assert len(pa) == 37
    s = summarize([d.date() for d in pa["date"]], list(pa["value"]), 0.06,
                  infer_periods_per_year(pa["date"]))
    assert 0 < s["cagr"] < 0.5 and s["max_drawdown"] < 0 and s["volatility"] > 0
