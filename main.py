from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.q1_stats import router as stats_router
from routes.q2_verify import router as verify_router
from routes.q3_config import router as config_router
from routes.q5_analytics import router as analytics_router
from routes.q6_observability import router as observability_router, add_observability_middleware
from routes.q9_orders import router as orders_router
from routes.q10_ping import router as ping_router

app = FastAPI(title="TDS GA2 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://exam.sanand.workers.dev",
        "https://dash-sw2mlo.example.com",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Retry-After", "X-Request-ID", "X-Process-Time"],
)

add_observability_middleware(app)

app.include_router(stats_router)
app.include_router(verify_router)
app.include_router(config_router)
app.include_router(analytics_router)
app.include_router(observability_router)
app.include_router(orders_router)
app.include_router(ping_router)


@app.get("/")
def home():
    return {"message": "TDS GA2 API is running"}