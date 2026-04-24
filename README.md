# Scheduled Agent Runner

A minimal scheduled multi-agent auto-run system.

## Setup

1. Install dependencies:
   pip install -r requirements.txt

2. Run backend:
   cd backend
   python main.py

3. Run frontend (in another terminal):
   cd frontend
   streamlit run app.py

## Features

- Schedule workflows using cron expressions
- Manual run workflows
- View past results
- Mock agents: research, summary, insight
- Results stored in results.json
- Notifications via console print