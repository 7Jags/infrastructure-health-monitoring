# Smart Infrastructure Intelligence & I2V Platform

Software-first prototype for monitoring infrastructure, assessing structural
risk, and eventually sending infrastructure-to-vehicle safety messages.

## Current milestone: persistent backend simulation

The backend runs a virtual Smart Node for bridge `BR-001` and exposes its
changing telemetry and structural-health assessment through FastAPI. It stores
telemetry, safety decisions, and UOB packets in SQLite by default, or
PostgreSQL when `DATABASE_URL` is configured.

## Run locally

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000/docs> to use the interactive API documentation.

## First endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Confirms that the API is available. |
| `GET` | `/api/infrastructure/bridges/BR-001/state` | Returns a changing virtual bridge reading and structural-health assessment. |
| `POST` | `/api/infrastructure/simulation/reset` | Restarts the virtual bridge's demo cycle. |
| `GET` | `/api/vehicles/{vehicle_id}/state` | Returns live telemetry for `V-001`, `V-002`, or `V-003`. |
| `GET` | `/api/safety/vehicles/{vehicle_id}/decision` | Combines virtual vehicle and bridge data into a GREEN, AMBER, or RED I2V recommendation. |
| `GET` | `/api/uob/vehicles/{vehicle_id}/latest` | Returns the virtual I2V UOB packet currently broadcast to the chosen vehicle. |
| `GET` | `/api/history/infrastructure/{node_id}` | Returns persisted infrastructure telemetry. |
| `GET` | `/api/history/vehicles/{vehicle_id}` | Returns persisted vehicle telemetry. |
| `GET` | `/api/history/safety/vehicles/{vehicle_id}` | Returns persisted safety decisions. |
| `GET` | `/api/history/uob/vehicles/{vehicle_id}` | Returns persisted I2V UOB packets. |

Copy `.env.example` to `.env` and set `DATABASE_URL` when PostgreSQL is
available. The built-in SQLite database is the default for local development.

## Verify

```bash
cd backend
.venv/bin/python -m pytest -q
```
