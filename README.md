# 🌟 Fashion Assistant

Welcome to your fashion assistant! File structure:

1. `frontend` - lightweight frontend built using React + Tailwind
2. `api` - microservice with FastAPI + SQLAlchemy
3. `data_processing` - Jupyter Notebooks + additional analysis

## Getting Started

### Pre-Requisites

- Docker (for db)
- npm

### Frontend

```
cd frontend
npm install
npm run dev
```

### API

```
cd api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
