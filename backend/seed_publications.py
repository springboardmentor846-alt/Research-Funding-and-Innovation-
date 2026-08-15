import requests

BASE_URL = "http://127.0.0.1:8000"

EMAIL = "rajupendra439@gmail.com"
PASSWORD = "123456"

sample_publications = [
    {
        "title": "Deep Learning Approaches for Predictive Analytics in Research Funding Allocation",
        "authors": "R. Kumar, A. Sharma",
        "year": "2024",
        "source": "International Journal of Artificial Intelligence Research",
    },
    {
        "title": "A Survey on Machine Learning Techniques for Patent Classification and Retrieval",
        "authors": "S. Verma",
        "year": "2023",
        "source": "IEEE Transactions on Knowledge and Data Engineering",
    },
    {
        "title": "Blockchain-Based Frameworks for Transparent Research Funding Management",
        "authors": "P. Singh, R. Kumar",
        "year": "2024",
        "source": "Journal of Emerging Technologies in Computational Science",
    },
    {
        "title": "Innovation Scoring Models Using NLP and Bibliometric Data",
        "authors": "A. Sharma",
        "year": "2025",
        "source": "Springer Conference on AI and Data Science",
    },
]

print("Logging in...")
login_res = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    json={"email": EMAIL, "password": PASSWORD},
)
login_res.raise_for_status()
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("Logged in successfully.")

added = 0
for pub in sample_publications:
    res = requests.post(f"{BASE_URL}/api/v1/profile/publications", json=pub, headers=headers)
    if res.status_code == 200:
        print(f"Added: {pub['title'][:60]}...")
        added += 1
    else:
        print(f"Failed to add '{pub['title'][:40]}...': {res.status_code} {res.text}")

print(f"\nDone. {added} of {len(sample_publications)} sample publications added.")