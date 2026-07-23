# 🚀 Research Funding and Innovation Platform

An AI-powered Research Funding and Innovation Platform that helps researchers discover funding opportunities, explore patents, analyze emerging technologies, and gain AI-driven research insights through an interactive dashboard.

---

## 📌 Features

### 🔐 Authentication
- User Registration
- User Login
- JWT Authentication
- Secure Password Hashing

### 📊 Dashboard
- Research Analytics
- Funding Statistics
- Patent Statistics
- Technology Insights
- AI Recommendation Cards

### 📑 Patent Management
- View Patent Repository
- Patent Details
- Citation Count
- Patent Status
- Technology Domain

### 💰 Funding Opportunities
- Latest Funding Calls
- Funding Agencies
- Grant Amount
- Application Deadline

### 💡 Technologies
- Emerging Technologies
- Technology Domains
- Innovation Trends

### 🤖 AI Insights
- AI-based Research Recommendations
- Technology Intelligence
- Research Trend Analysis

### 📈 Analytics
- Patent Analytics
- Funding Analytics
- Research Statistics

---

# 🛠 Tech Stack

## Frontend
- React.js
- Vite
- Tailwind CSS
- Axios
- React Router DOM
- Lucide React

## Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- JWT Authentication
- Passlib

---

# 📂 Project Structure

```
Research-Funding-and-Innovation
│
├── backend
│   ├── app
│   │   ├── auth
│   │   ├── models
│   │   ├── routers
│   │   ├── schemas
│   │   ├── services
│   │   └── main.py
│
├── frontend
│   ├── public
│   ├── src
│   │   ├── assets
│   │   ├── components
│   │   ├── pages
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
│
└── README.md
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/<repository-url>.git
```

---

## Backend Setup

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Backend runs at

```
http://127.0.0.1:8000
```

---

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend runs at

```
http://localhost:5173
```

---

# 📡 API Endpoints

## Authentication

- POST /register
- POST /login

## Research Profile

- GET /profile
- POST /profile

## Patents

- GET /patents

## Funding

- GET /funding

## Technologies

- GET /technologies

## Innovation

- GET /innovation

## Commercialization

- GET /commercialization



# 📄 License

This project is developed for educational and internship purposes.
