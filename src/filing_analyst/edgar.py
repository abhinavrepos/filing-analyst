import httpx
from pprint import pprint

def get_submissions(cik:str) -> dict:
    headers = {
        "User-Agent": "filing-analyst/1.0 (Contact: Abhinav Goli; abhinav.me1611@gmail.com)"
    }
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response =  httpx.get(url, headers=headers)
    return response.json()

def get_10ks(response, cik) -> dict:
    form = response["filings"]["recent"]["form"]
    accessionNumber = response["filings"]["recent"]["accessionNumber"]
    primaryDocument = response["filings"]["recent"]["primaryDocument"]
    filing_date  =response["filings"]["recent"]["filingDate"]
    final_accession_numbers=[]
    final_primary_Documents = []

    result_10ks=[]

    for form_number, accessionNumber, primaryDocument, date  in zip (form,accessionNumber,primaryDocument, filing_date):
        if(form_number == "10-K"):
            url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accessionNumber.replace("-", "")}/{primaryDocument}"
            result_10ks.append({"date": date, "accessionNumber": accessionNumber, "primaryDocument": primaryDocument, "url":url }) 

    return result_10ks


if __name__ == "__main__":
    data = get_submissions( cik= "0000320193")
    result_10ks = get_10ks(data, "0000320193" )
    print(result_10ks)