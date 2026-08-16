import requests

BASE_URL = "http://127.0.0.1:8000"

ADMIN_NAME = "Admin"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin1234"

funding_opportunities = [
    {
        "title": "AI Research Innovation Grant",
        "source": "National Science Foundation",
        "description": "Funding for cutting-edge artificial intelligence and machine learning research projects.",
        "eligibility": "Researcher, Startup Founder",
        "domains": "AI, Machine Learning",
        "deadline": "2026-12-31",
        "amount": "$150,000",
        "link": "https://www.nsf.gov",
    },
    {
        "title": "Blockchain Technology Development Fund",
        "source": "Department of Commerce",
        "description": "Supports research and commercialization of blockchain-based solutions.",
        "eligibility": "Researcher, Startup Founder, Innovation Manager",
        "domains": "Blockchain",
        "deadline": "2026-11-30",
        "amount": "$100,000",
        "link": "https://www.commerce.gov",
    },
    {
        "title": "Emerging Technology Seed Grant",
        "source": "Department of Energy",
        "description": "Early-stage funding for emerging technology areas including AI, data science, and software innovation.",
        "eligibility": "Researcher, Startup Founder",
        "domains": "AI, Blockchain, Machine Learning, Data Science",
        "deadline": "2027-01-15",
        "amount": "$75,000",
        "link": "https://www.energy.gov",
    },
]

print("Step 1: Registering admin account...")
reg_res = requests.post(f"{BASE_URL}/api/v1/auth/register", json={"name": ADMIN_NAME, "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD, "role": "admin"})
if reg_res.status_code == 200:
    print("  Admin registered successfully.")
else:
    print(f"  Register response ({reg_res.status_code}): {reg_res.text} (continuing, may already exist)")

print("Step 2: Logging in as admin...")
login_res = requests.post(f"{BASE_URL}/api/v1/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
login_res.raise_for_status()
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("  Logged in successfully.")

print("Step 3: Adding funding opportunities...")
added = 0
for funding in funding_opportunities:
    res = requests.post(f"{BASE_URL}/api/v1/funding/", json=funding, headers=headers)
    if res.status_code == 200:
        print(f"  Added: {funding['title']}")
        added += 1
    else:
        print(f"  Failed '{funding['title']}': {res.status_code} {res.text}")

print(f"\nDone. {added} of {len(funding_opportunities)} funding opportunities added.")