from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from collections import deque
import time
import uuid

router = APIRouter()

EMAIL = "23f3002902@ds.study.iitm.ac.in"
START_TIME = time.time()

REQUEST_COUNT = 0
LOGS = deque(maxlen=200)


def add_observability_middleware(app):
    @app.middleware("http")
    async def observability_middleware(request: Request, call_next):
        global REQUEST_COUNT

        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        REQUEST_COUNT += 1

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        LOGS.append({
            "level": "info",
            "ts": time.time(),
            "path": request.url.path,
            "request_id": request_id,
        })

        return response


@router.get("/work")
def work(n: int = 1):
    if n < 0:
        n = 0

    total = 0
    for i in range(n):
        total += i

    return {
        "email": EMAIL,
        "done": n,
    }


@router.get("/metrics")
def metrics():
    content = f"""# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total {REQUEST_COUNT}
"""
    return PlainTextResponse(content, media_type="text/plain")


@router.get("/healthz")
def healthz():
    return {
        "status": "ok",
        "uptime_s": time.time() - START_TIME,
    }


@router.get("/logs/tail")
def logs_tail(limit: int = 10):
    if limit < 0:
        limit = 0

    return list(LOGS)[-limit:]