import requests

BASE_URL = "http://127.0.0.1:8000"

NAME = "Upendra"
EMAIL = "upendra80026@gmail.com"
PASSWORD = "123456"
ROLE = "researcher"

profile_data = {
    "research_domains": "AI, Blockchain, Machine Learning",
    "keywords": "deep learning, patent analytics, funding intelligence",
    "technology_areas": "Software, Data Science",
    "organization_name": "Test University",
}

real_patents = [
    {"title": "Using machine learning to train and use a model to perform automatic interface actions based on video and input datasets", "assignee": "OpenAI OpCo LLC", "filing_date": "2023-12-19", "patent_number": "US11887367B1"},
    {"title": "Method of validating transactions for recordal in a blockchain", "assignee": "Capital One Services, LLC", "filing_date": "2024-07-23", "patent_number": "US12045830"},
    {"title": "Block validation using a trusted stamping authority on a blockchain ledger", "assignee": "International Business Machines Corporation", "filing_date": "2025-03-11", "patent_number": "US12250312"},
    {"title": "Reputation profile propagation on blockchain networks", "assignee": "International Business Machines Corporation", "filing_date": "2024-10-22", "patent_number": "US12126721"},
    {"title": "Encoding and storing endorsed blockchain storage requests within a data section of a block", "assignee": "International Business Machines Corporation", "filing_date": "2023-12-05", "patent_number": "US11838400"},
    {"title": "Systems and methods for training a machine-learned model on audio signal data", "assignee": "Google LLC", "filing_date": "2024-12-10", "patent_number": "US12165663"},
    {"title": "Machine learning transformations for detecting anomalies in financial transactions", "assignee": "Google LLC", "filing_date": "2025-02-04", "patent_number": "US12217306"},
]

sample_publications = [
    {"title": "Deep Learning Approaches for Predictive Analytics in Research Funding Allocation", "authors": "R. Kumar, A. Sharma", "year": "2024", "source": "International Journal of Artificial Intelligence Research"},
    {"title": "A Survey on Machine Learning Techniques for Patent Classification and Retrieval", "authors": "S. Verma", "year": "2023", "source": "IEEE Transactions on Knowledge and Data Engineering"},
    {"title": "Blockchain-Based Frameworks for Transparent Research Funding Management", "authors": "P. Singh, R. Kumar", "year": "2024", "source": "Journal of Emerging Technologies in Computational Science"},
    {"title": "Innovation Scoring Models Using NLP and Bibliometric Data", "authors": "A. Sharma", "year": "2025", "source": "Springer Conference on AI and Data Science"},
]

print("Step 1: Registering user...")
reg_res = requests.post(f"{BASE_URL}/api/v1/auth/register", json={"name": NAME, "email": EMAIL, "password": PASSWORD, "role": ROLE})
if reg_res.status_code == 200:
    print("  Registered successfully.")
else:
    print(f"  Register response ({reg_res.status_code}): {reg_res.text} (continuing, may already exist)")

print("Step 2: Logging in...")
login_res = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})
login_res.raise_for_status()
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("  Logged in successfully.")

print("Step 3: Creating research profile...")
profile_res = requests.post(f"{BASE_URL}/api/v1/profile/", json=profile_data, headers=headers)
if profile_res.status_code == 200:
    print("  Profile created successfully.")
else:
    print(f"  Profile response ({profile_res.status_code}): {profile_res.text}")

print("Step 4: Adding patents...")
patent_added = 0
for patent in real_patents:
    res = requests.post(f"{BASE_URL}/api/v1/profile/patents", json=patent, headers=headers)
    if res.status_code == 200:
        patent_added += 1
    else:
        print(f"  Failed patent '{patent['title'][:40]}...': {res.status_code} {res.text}")
print(f"  {patent_added} of {len(real_patents)} patents added.")

print("Step 5: Adding publications...")
pub_added = 0
for pub in sample_publications:
    res = requests.post(f"{BASE_URL}/api/v1/profile/publications", json=pub, headers=headers)
    if res.status_code == 200:
        pub_added += 1
    else:
        print(f"  Failed publication '{pub['title'][:40]}...': {res.status_code} {res.text}")
print(f"  {pub_added} of {len(sample_publications)} publications added.")

print("\nAll done! Login with:")
print(f"  Email: {EMAIL}")
print(f"  Password: {PASSWORD}")