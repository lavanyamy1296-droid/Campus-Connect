# Campus Connect 🎓

A responsive single-college community portal built with React, Vite, FastAPI and SQLite.

## Features
- Campus dashboard with live counts
- Announcements: browse and publish notices
- Events: browse, create and register (registration count updates)
- Community: publish posts and like them
- Lost & Found: publish listings and contact by email
- Responsive desktop and mobile layout
- SQLite persistence (no separate database server required)

## Requirements
- Python 3.10+
- Node.js 18+
- VS Code (recommended)

## Run locally

### 1. Start the backend
Open a terminal in the project root:

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
```
If PowerShell blocks activation, use:
```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

macOS/Linux:
```bash
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at http://127.0.0.1:8000  
API docs: http://127.0.0.1:8000/docs

### 2. Start the frontend
Open a **second terminal** at the project root:

```bash
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite, usually http://localhost:5173.

## Data
The backend creates `backend/campus.db` automatically and inserts sample content on first run. Data remains saved between restarts. Delete that database file to reset the demo data.

## Notes
This is a portfolio/demo starter. The role/profile shown in the UI is illustrative; production deployment needs real authentication, authorization, input moderation, rate limiting, and secure account management before public use.
