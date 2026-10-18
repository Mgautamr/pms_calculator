"""Reading uploaded value series (CSV) for the dashboard."""
import io

import pandas as pd


class DataError(ValueError):
    """An uploaded series cannot be used. The message says how to fix it."""


VALUE_COLUMNS = ("value", "nav", "close", "portfolio_value", "portfolio value", "price")


def _read(source):
    if hasattr(source, "getvalue"):          # Streamlit upload (bytes) or a text buffer (str)
        raw = source.getvalue()
        source = io.StringIO(raw) if isinstance(raw, str) else io.BytesIO(raw)
    try:
        return pd.read_csv(source)
    except Exception as exc:
        raise DataError("The file could not be read as a CSV. Save it as a comma-separated "
                        "(.csv) file with a header row: date,value.") from exc


def parse_series(source):
    """Read a CSV with a date column and a value column into a clean, sorted DataFrame."""
    df = _read(source)
    df.columns = [str(c).strip().lower() for c in df.columns]
    if "date" not in df.columns:
        raise DataError("No 'date' column found. The first row must be the headers: date,value.")
    value_col = next((c for c in VALUE_COLUMNS if c in df.columns), None)
    if value_col is None:
        raise DataError("No 'value' column found. The first row must be the headers: date,value.")

    raw_dates = df["date"].astype(str).str.strip()
    dates = pd.to_datetime(raw_dates, format="ISO8601", errors="coerce")
    if dates.isna().any():
        dates = pd.to_datetime(raw_dates, dayfirst=True, format="mixed", errors="coerce")
    bad = dates.isna()
    if bad.any():
        rows = (df.index[bad][:3] + 2).tolist()
        raise DataError(f"Could not read the date in row(s) {rows}. "
                        "Use YYYY-MM-DD or DD-MM-YYYY.")

    values = pd.to_numeric(df[value_col].astype(str).str.replace(",", "").str.strip(),
                           errors="coerce")
    bad = values.isna() | (values <= 0)
    if bad.any():
        rows = (df.index[bad][:3] + 2).tolist()
        raise DataError(f"Values must be positive numbers. Check row(s) {rows}.")

    out = pd.DataFrame({"date": dates, "value": values.astype(float)})
    if out["date"].duplicated().any():
        raise DataError("Each date can appear only once. Remove or merge the repeated dates.")
    out = out.sort_values("date").reset_index(drop=True)
    if len(out) < 3:
        raise DataError("Need at least 3 rows to calculate risk measures.")
    return out


def infer_periods_per_year(dates):
    """Guess how often the series is observed from the typical gap between dates."""
    gap = pd.Series(pd.to_datetime(list(dates))).diff().dt.days.median()
    if gap <= 4:
        return 252
    if gap <= 10:
        return 52
    if gap <= 45:
        return 12
    if gap <= 120:
        return 4
    return 1


def align(portfolio, benchmark):
    """Keep only the dates both series share, so the comparison is like for like."""
    merged = portfolio.merge(benchmark, on="date", suffixes=("_p", "_b"))
    if len(merged) < 3:
        raise DataError("The portfolio and benchmark share fewer than 3 dates. "
                        "Use the same dates in both files.")
    p = merged[["date", "value_p"]].rename(columns={"value_p": "value"})
    b = merged[["date", "value_b"]].rename(columns={"value_b": "value"})
    return p, b


def rebase(values, base=100.0):
    """Rescale a series so it starts at `base`."""
    first = values[0]
    return [v / first * base for v in values]
