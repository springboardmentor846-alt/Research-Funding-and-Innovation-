import requests

BASE_URL = "http://127.0.0.1:8000"

EMAIL = "upendra80026@gmail.com"
PASSWORD = "123456"

ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin1234"

more_publications = [
    {"title": "Advances in Machine Learning for Blockchain-Based Financial Transaction Validation", "authors": "R. Kumar, S. Verma", "year": "2024", "source": "ACM Transactions on Intelligent Systems"},
    {"title": "Machine Learning and Blockchain Integration for Secure Data Networks", "authors": "A. Sharma, P. Singh", "year": "2025", "source": "Elsevier Journal of Computational Intelligence"},
    {"title": "Training Machine Learning Models on Blockchain Transaction Data for Anomaly Detection", "authors": "R. Kumar", "year": "2023", "source": "IEEE Access"},
    {"title": "A Machine Learning Framework for Blockchain Patent Landscape Analysis", "authors": "S. Verma, A. Sharma", "year": "2025", "source": "Journal of Innovation and Technology Management"},
]

extra_funding = {
    "title": "AI and Blockchain Convergence Research Fund",
    "source": "National Innovation Council",
    "description": "Supports interdisciplinary research combining machine learning and blockchain technologies.",
    "eligibility": "Researcher, Startup Founder, Innovation Manager",
    "domains": "AI, Blockchain, Machine Learning, Data Science",
    "deadline": "2027-03-31",
    "amount": "$120,000",
    "link": "https://www.nist.gov",
}

print("Step 1: Logging in as user...")
login_res = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})
login_res.raise_for_status()
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("  Logged in successfully.")

print("Step 2: Adding more publications...")
added = 0
for pub in more_publications:
    res = requests.post(f"{BASE_URL}/api/v1/profile/publications", json=pub, headers=headers)
    if res.status_code == 200:
        added += 1
    else:
        print(f"  Failed '{pub['title'][:40]}...': {res.status_code} {res.text}")
print(f"  {added} of {len(more_publications)} publications added.")

print("Step 3: Logging in as admin...")
admin_login_res = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
admin_login_res.raise_for_status()
admin_token = admin_login_res.json()["access_token"]
admin_headers = {"Authorization": f"Bearer {admin_token}"}
print("  Logged in successfully.")

print("Step 4: Adding one more funding opportunity...")
res = requests.post(f"{BASE_URL}/api/v1/funding/", json=extra_funding, headers=admin_headers)
if res.status_code == 200:
    print("  Funding opportunity added.")
else:
    print(f"  Failed: {res.status_code} {res.text}")

print("\nDone. Refresh your dashboard to see the updated Innovation Score.")