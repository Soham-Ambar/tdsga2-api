from fastapi import FastAPI
from routes.q1_stats import router as stats_router

app = FastAPI(title="TDS GA2 API")

# Q1 endpoint
app.include_router(stats_router)


@app.get("/")
def root():
    return {
        "message": "TDS GA2 API is running",
        "available_endpoints": ["GET /stats?values=1,2,3"]
    }
