# tdsga2-api

FastAPI project for TDS GA2 assignments.

Currently implemented:

- Q1: `GET /stats?values=1,2,3`

## Before deploying Q1

Open `routes/q1_stats.py` and replace:

```python
ALLOWED_ORIGIN = "YOUR_ASSIGNED_ALLOWED_ORIGIN"
```

with the exact allowed origin shown in your exam panel.

Also confirm this email is correct:

```python
EMAIL = "23f3002902@ds.study.iitm.ac.in"
```

## Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Test:

```bash
http://127.0.0.1:8000/stats?values=1,2,3,4,5
```

## Render deployment

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Submit only the base URL for Q1, for example:

```text
https://tdsga2-api.onrender.com
```
