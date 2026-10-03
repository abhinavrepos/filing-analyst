import pytest

from filing_analyst.edgar import REVENUE, get_annual_fact


def make_row(start, end, val, form="10-K", filed="2024-11-01"):
    row = {"end": end, "val": val, "form": form, "filed": filed}
    if start is not None:
        row["start"] = start
    return row


def make_facts(concept, rows):
    return {"facts": {"us-gaap": {concept: {"units": {"USD": rows}}}}}


def test_picks_full_year_and_ignores_the_noise():
    rows = [
        make_row("2022-09-25", "2023-09-30", 383_285_000_000),
        make_row("2023-10-01", "2024-06-29", 296_105_000_000,
                 form="10-Q", filed="2024-08-02"),
        make_row("2024-06-30", "2024-09-28", 94_930_000_000),
        make_row("2023-10-01", "2024-09-28", 391_035_000_000),
    ]
    facts = make_facts(REVENUE, rows)
    assert get_annual_fact(facts, REVENUE, 2024) == 391_035_000_000


def test_quarter_inside_a_10k_is_not_a_full_year():
    rows = [make_row("2024-06-30", "2024-09-28", 94_930_000_000)]
    facts = make_facts(REVENUE, rows)
    with pytest.raises(ValueError):
        get_annual_fact(facts, REVENUE, 2024)


def test_prefers_the_latest_filing_when_duplicated():
    rows = [
        make_row("2023-10-01", "2024-09-28", 391_000_000_000,
                 filed="2024-11-01"),
        make_row("2023-10-01", "2024-09-28", 391_035_000_000,
                 filed="2025-10-31"),
    ]
    facts = make_facts(REVENUE, rows)
    assert get_annual_fact(facts, REVENUE, 2024) == 391_035_000_000


def test_balance_sheet_fact_without_start_date():
    rows = [make_row(None, "2024-09-28", 364_980_000_000)]
    facts = make_facts("Assets", rows)
    assert get_annual_fact(facts, "Assets", 2024) == 364_980_000_000


def test_missing_year_raises_instead_of_guessing():
    rows = [make_row("2023-10-01", "2024-09-28", 391_035_000_000)]
    facts = make_facts(REVENUE, rows)
    with pytest.raises(ValueError):
        get_annual_fact(facts, REVENUE, 2019)