# Commands Guide: Run Backend & Frontend

This document contains all the commands to setup, start, and run the backend and frontend of **AI Manga Studio**.

---

## 1. Quick Start (TL;DR)

Open two separate terminal windows from the project root (`c:\Aditya\vibe coding\projects\manga`):

### Terminal 1: Backend (FastAPI)
```powershell
# 1. Activate virtual environment (Windows)
.\.venv\Scripts\activate

# 2. Navigate to backend
cd backend

# 3. Apply database migrations
python -m alembic upgrade head

# 4. Start FastAPI server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
> **Backend URL:** [http://127.0.0.1:8000](http://127.0.0.1:8000)  
> **Interactive Swagger API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### Terminal 2: Frontend (Vite + React)
```powershell
# 1. Navigate to frontend
cd frontend

# 2. Start Vite development server
npm run dev
```
> **Frontend Studio App:** [http://127.0.0.1:5173](http://127.0.0.1:5173) (or `http://localhost:5173`)

---

## 2. First-Time Setup & Installation

If this is a fresh setup or new environment, execute these steps first:

### Step 1: Environment File
From the project root:
```powershell
# Windows PowerShell
Copy-Item .env.example .env

# Bash / macOS / Linux
cp .env.example .env
```
*(Default settings use SQLite and Zero-Credential Studio Mock fallback, so no API keys are required to test.)*

### Step 2: Python Virtual Environment & Backend Dependencies
From the project root:
```powershell
# Create virtual environment (if not already present)
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\activate
# Windows CMD:
.\.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

### Step 3: Frontend Dependencies
From the project root:
```powershell
cd frontend
npm install
cd ..
```

---

## 3. Running Database Migrations

Whenever you modify models or on initial launch:

```powershell
# From project root
cd backend
python -m alembic upgrade head
cd ..
```

To roll back or inspect migrations:
```powershell
cd backend
python -m alembic current
python -m alembic history
```

---

## 4. Running Backend Without Activating Environment

If you prefer one-liners without activating the virtual environment in your shell:

```powershell
# Windows PowerShell from project root:
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

---

## 5. Running Automated Tests

Run the backend test suite (Authentication, Multi-agent pipeline, PDF export, etc.):

```powershell
# From project root (Windows)
.\.venv\Scripts\python.exe -m pytest backend/tests -v

# Or from inside backend directory:
cd backend
pytest tests -v
```

---

## 6. Frontend Build & Production Preview

To test production bundle build:
```powershell
cd frontend
npm run build
npm run preview
```

---

## 7. Optional: Docker Infrastructure (PostgreSQL & Redis)

If you switch `DATABASE_URL` in `.env` from SQLite to PostgreSQL:
```powershell
# Start PostgreSQL & Redis in background
docker-compose up -d

# Stop services
docker-compose down
```
