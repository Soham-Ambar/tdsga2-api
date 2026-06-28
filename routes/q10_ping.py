from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import time
import uuid

router = APIRouter()

EMAIL = "23f3002902@ds.study.iitm.ac.in"

ALLOWED_ORIGINS = {
    "https://app-q70ohb.example.com",
    "https://exam.sanand.workers.dev",
}

RATE_LIMIT = 15
WINDOW_SECONDS = 10
rate_buckets = {}


def cors_headers(origin: str | None):
    headers = {
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Expose-Headers": "X-Request-ID",
    }

    if origin in ALLOWED_ORIGINS:
        headers["Access-Control-Allow-Origin"] = origin

    return headers


def check_rate_limit(client_id: str):
    now = time.time()
    bucket = rate_buckets.setdefault(client_id, [])

    bucket[:] = [t for t in bucket if now - t < WINDOW_SECONDS]

    if len(bucket) >= RATE_LIMIT:
        retry_after = max(1, int(WINDOW_SECONDS - (now - bucket[0])) + 1)
        return False, str(retry_after)

    bucket.append(now)
    return True, None


@router.options("/ping")
def ping_options(request: Request):
    origin = request.headers.get("origin")

    return JSONResponse(
        content={},
        headers=cors_headers(origin),
    )


@router.get("/ping")
def ping(request: Request):
    origin = request.headers.get("origin")
    client_id = request.headers.get("X-Client-Id", "default")

    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

    allowed, retry_after = check_rate_limit(client_id)

    if not allowed:
        headers = cors_headers(origin)
        headers["X-Request-ID"] = request_id
        headers["Retry-After"] = retry_after

        return JSONResponse(
            status_code=429,
            content={
                "error": "rate limit exceeded",
                "request_id": request_id,
            },
            headers=headers,
        )

    headers = cors_headers(origin)
    headers["X-Request-ID"] = request_id

    return JSONResponse(
        content={
            "email": EMAIL,
            "request_id": request_id,
        },
        headers=headers,
    )