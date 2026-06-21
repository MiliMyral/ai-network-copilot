# AI Network Copilot

A 4-week project to build a network monitoring tool with anomaly detection and dashboard.

## Project Structure

- `api/` - FastAPI backend
- `dashboard/` - Streamlit dashboard
- `schema.sql` - Proposed database schema

## Getting Started

### Backend (API)

1. Install dependencies: `pip install -r api/requirements.txt`
2. Run the API: `uvicorn api.main:app --reload`

### Dashboard

1. Install dependencies: `pip install -r dashboard/requirements.txt`
2. Run the dashboard: `streamlit run dashboard/app.py`

### Docker

- Build and run API: `docker build -t ai-network-api ./api && docker run -p 8000:8000 ai-network-api`
- Build and run Dashboard: `docker build -t ai-network-dashboard ./dashboard && docker run -p 8501:8501 ai-network-dashboard`

## Schema

See `schema.sql` for the proposed database schema.

