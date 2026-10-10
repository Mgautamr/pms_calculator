"""Loading and querying the sourced vehicle comparison data."""
import json
from pathlib import Path

from app.formatting import format_inr

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "vehicles.json"

STATUS_ORDER = ["official", "official_reported", "legal_database", "secondary", "not_verified"]
STATUS_EMOJI = {
    "official": "✅",
    "official_reported": "✅",
    "legal_database": "🟦",
    "secondary": "🟧",
    "not_verified": "⬜",
}
STATUS_SHORT = {
    "official": "Official source",
    "official_reported": "Official document, figure via news report",
    "legal_database": "Act text via tax-law database",
    "secondary": "Secondary source",
    "not_verified": "Not verified",
}


def load_data(path=None):
    with open(path or DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def check_eligibility(data, amount, accredited=False):
    """For each vehicle, say whether an amount meets the stated minimum.

    Uses the min_investment fact (amount_inr, accredited_exempt) of each vehicle.
    """
    results = []
    for vid, vehicle in data["vehicles"].items():
        fact = vehicle["facts"]["min_investment"]
        minimum = fact["amount_inr"]
        if accredited and fact.get("accredited_exempt"):
            verdict = "open"
            detail = "Accredited investors are exempt from the minimum."
        elif amount >= minimum:
            verdict = "open"
            detail = f"Meets the minimum of {format_inr(minimum)}."
        else:
            verdict = "below"
            detail = (f"Short by {format_inr(minimum - amount)} "
                      f"(minimum {format_inr(minimum)}).")
        caution = None
        if vehicle.get("status") == "approved_not_confirmed_in_force":
            caution = "Approved by SEBI's Board on 24 Sep 2026. Not confirmed in force."
        results.append({
            "id": vid,
            "name": vehicle["name"],
            "verdict": verdict,
            "detail": detail,
            "caution": caution,
            "figure_status": fact["status"],
        })
    return results


def large_value_fund_note(data, amount, accredited):
    """Extra line for accredited investors who could access AIF large value funds."""
    fact = data["vehicles"]["aif"]["facts"].get("large_value_fund")
    if not fact or not accredited or amount < fact["amount_inr"]:
        return None
    return (f"As an accredited investor with {format_inr(amount)}, you also meet the "
            f"{format_inr(fact['amount_inr'])} minimum for AIF large value funds.")
