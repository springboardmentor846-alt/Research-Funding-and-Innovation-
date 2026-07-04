from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Research Funding Platform Backend is running"}