import re

import pytest

from app.vehicles import STATUS_ORDER, check_eligibility, large_value_fund_note, load_data

DATA = load_data()


def all_facts():
    for vid, vehicle in DATA["vehicles"].items():
        for key, fact in vehicle["facts"].items():
            yield vid, key, fact


# ---------- data quality ----------
def test_verified_date_is_iso():
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", DATA["meta"]["last_verified"])


@pytest.mark.parametrize("vid,key,fact", list(all_facts()),
                         ids=lambda x: x if isinstance(x, str) else None)
def test_fact_is_well_formed(vid, key, fact):
    assert fact["status"] in STATUS_ORDER
    assert fact["label"] and fact["value"]
    if fact["status"] == "not_verified":
        assert fact["sources"] == []
    else:
        assert fact["sources"], f"{vid}.{key} has no source"
    for source in fact["sources"]:
        assert source["url"].startswith("https://")
        assert source["supports"]


def test_every_vehicle_has_numeric_minimum():
    for vid, vehicle in DATA["vehicles"].items():
        fact = vehicle["facts"]["min_investment"]
        assert isinstance(fact["amount_inr"], int) and fact["amount_inr"] > 0
        assert isinstance(fact["accredited_exempt"], bool)


def test_official_claims_have_an_official_domain():
    official_hosts = ("sebi.gov.in", "incometaxindia.gov.in")
    for vid, key, fact in all_facts():
        if fact["status"] == "official":
            assert any(h in s["url"] for s in fact["sources"] for h in official_hosts), \
                f"{vid}.{key} is marked official without an official link"


# ---------- eligibility logic ----------
def by_id(results):
    return {r["id"]: r for r in results}


def test_50_lakh_meets_pms_but_not_aif():
    r = by_id(check_eligibility(DATA, 5_000_000))
    assert r["mutual_fund"]["verdict"] == "open"
    assert r["sif"]["verdict"] == "open"
    assert r["pms"]["verdict"] == "open"
    assert r["prim"]["verdict"] == "open"
    assert r["aif"]["verdict"] == "below"
    assert "₹50,00,000" in r["aif"]["detail"]  # short by 50 lakh


def test_small_amount_only_reaches_mutual_funds():
    r = by_id(check_eligibility(DATA, 100_000))
    assert [k for k, v in r.items() if v["verdict"] == "open"] == ["mutual_fund"]


def test_accredited_investor_is_exempt_for_sif_and_aif_only():
    r = by_id(check_eligibility(DATA, 100_000, accredited=True))
    assert r["sif"]["verdict"] == "open"
    assert r["aif"]["verdict"] == "open"
    assert r["pms"]["verdict"] == "below"


def test_prim_carries_a_caution():
    r = by_id(check_eligibility(DATA, 5_000_000))
    assert r["prim"]["caution"]
    assert r["pms"]["caution"] is None


def test_exact_minimum_counts_as_meeting_it():
    r = by_id(check_eligibility(DATA, 10_000_000))
    assert r["aif"]["verdict"] == "open"


def test_large_value_fund_note():
    assert large_value_fund_note(DATA, 250_000_000, accredited=True)
    assert large_value_fund_note(DATA, 249_999_999, accredited=True) is None
    assert large_value_fund_note(DATA, 250_000_000, accredited=False) is None
