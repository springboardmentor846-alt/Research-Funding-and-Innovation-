import requests

BASE_URL = "http://127.0.0.1:8000"

EMAIL = "rajupendra439@gmail.com"
PASSWORD = "123456"

real_patents = [
    {
        "title": "Using machine learning to train and use a model to perform automatic interface actions based on video and input datasets",
        "assignee": "OpenAI OpCo LLC",
        "filing_date": "2023-12-19",
        "patent_number": "US11887367B1",
    },
    {
        "title": "Method of validating transactions for recordal in a blockchain",
        "assignee": "Capital One Services, LLC",
        "filing_date": "2024-07-23",
        "patent_number": "US12045830",
    },
    {
        "title": "Block validation using a trusted stamping authority on a blockchain ledger",
        "assignee": "International Business Machines Corporation",
        "filing_date": "2025-03-11",
        "patent_number": "US12250312",
    },
    {
        "title": "Reputation profile propagation on blockchain networks",
        "assignee": "International Business Machines Corporation",
        "filing_date": "2024-10-22",
        "patent_number": "US12126721",
    },
    {
        "title": "Encoding and storing endorsed blockchain storage requests within a data section of a block",
        "assignee": "International Business Machines Corporation",
        "filing_date": "2023-12-05",
        "patent_number": "US11838400",
    },
    {
        "title": "Systems and methods for training a machine-learned model on audio signal data",
        "assignee": "Google LLC",
        "filing_date": "2024-12-10",
        "patent_number": "US12165663",
    },
    {
        "title": "Machine learning transformations for detecting anomalies in financial transactions",
        "assignee": "Google LLC",
        "filing_date": "2025-02-04",
        "patent_number": "US12217306",
    },
]

print("Logging in...")
login_res = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"email": EMAIL, "password": PASSWORD},
)
login_res.raise_for_status()
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("Logged in successfully.")

added = 0
for patent in real_patents:
    res = requests.post(f"{BASE_URL}/api/profile/patents", json=patent, headers=headers)
    if res.status_code == 200:
        print(f"Added: {patent['title'][:60]}...")
        added += 1
    else:
        print(f"Failed to add '{patent['title'][:40]}...': {res.status_code} {res.text}")

print(f"\nDone. {added} of {len(real_patents)} real patents added.")