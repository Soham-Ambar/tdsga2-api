from fastapi import FastAPI
from routes.q1_stats import router as stats_router
from routes.q2_verify import router as verify_router
from routes.q3_config import router as config_router

app = FastAPI(title="TDS GA2 API")

app.include_router(stats_router)
app.include_router(verify_router)
app.include_router(config_router)


@app.get("/")
def home():
    return {"message": "TDS GA2 API is running"}