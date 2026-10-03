import os
from datetime import date

import httpx

HEADERS = {
    "User-Agent": (
        "filing-analyst/1.0 "
        "(Contact: Abhinav Goli; abhinav.me1611@gmail.com)"
    )
}
REVENUE = "RevenueFromContractWithCustomerExcludingAssessedTax"


def get_submissions(cik: str) -> dict:
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response = httpx.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def get_10ks(submissions: dict, cik: str) -> list[dict]:
    recent = submissions["filings"]["recent"]
    filings = []
    for form, accession, document, filed in zip(
        recent["form"],
        recent["accessionNumber"],
        recent["primaryDocument"],
        recent["filingDate"],
    ):
        if form == "10-K":
            folder = accession.replace("-", "")
            url = (
                "https://www.sec.gov/Archives/edgar/data/"
                f"{int(cik)}/{folder}/{document}"
            )
            filings.append({
                "date": filed,
                "accessionNumber": accession,
                "primaryDocument": document,
                "url": url,
            })
    return filings


def save_10ks(filings: list[dict], count: int = 3) -> None:
    folder_path = os.path.join("data", "raw")
    os.makedirs(folder_path, exist_ok=True)
    for filing in filings[:count]:
        try:
            full_path = os.path.join(
                folder_path, filing["primaryDocument"]
            )
            response = httpx.get(filing["url"], headers=HEADERS)
            response.raise_for_status()
            with open(full_path, "w", encoding="utf-8") as file:
                file.write(response.text)
        except httpx.HTTPError as e:
            print("Download failed:", e)


def get_company_facts(cik: str) -> dict:
    url = (
        "https://data.sec.gov/api/xbrl/companyfacts/"
        f"CIK{cik}.json"
    )
    response = httpx.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def get_annual_fact(
    facts: dict, concept: str, fiscal_year: int
) -> float:
    entries = facts["facts"]["us-gaap"][concept]["units"]["USD"]
    matches = []
    for entry in entries:
        if entry["form"] != "10-K":
            continue
        end = date.fromisoformat(entry["end"])
        if end.year != fiscal_year:
            continue
        if "start" in entry:
            start = date.fromisoformat(entry["start"])
            if (end - start).days < 350:
                continue
        matches.append(entry)

    if not matches:
        raise ValueError(
            f"No 10-K value for {concept} in FY{fiscal_year}"
        )
    latest = max(matches, key=lambda entry: entry["filed"])
    return latest["val"]


if __name__ == "__main__":
    APPLE = "0000320193"
    facts = get_company_facts(APPLE)
    revenue = get_annual_fact(facts, REVENUE, 2024)
    print(f"Apple FY2024 revenue: {revenue:,}")