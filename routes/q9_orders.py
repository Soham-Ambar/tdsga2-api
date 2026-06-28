from fastapi import APIRouter, Header, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import time
import uuid
import base64

router = APIRouter()

TOTAL_ORDERS = 48
RATE_LIMIT = 16
WINDOW_SECONDS = 10

orders_by_key = {}
rate_buckets = {}


class OrderRequest(BaseModel):
    item: Optional[str] = "sample"
    quantity: Optional[int] = 1


def make_cursor(index: int) -> str:
    return base64.urlsafe_b64encode(str(index).encode()).decode()


def read_cursor(cursor: Optional[str]) -> int:
    if not cursor:
        return 0
    try:
        return int(base64.urlsafe_b64decode(cursor.encode()).decode())
    except Exception:
        return 0


def check_rate_limit(client_id: str):
    now = time.time()
    bucket = rate_buckets.setdefault(client_id, [])

    bucket[:] = [t for t in bucket if now - t < WINDOW_SECONDS]

    if len(bucket) >= RATE_LIMIT:
        retry_after = max(1, int(WINDOW_SECONDS - (now - bucket[0])) + 1)
        return False, str(retry_after)

    bucket.append(now)
    return True, None


def rate_limit_response(retry_after: str):
    return JSONResponse(
        status_code=429,
        content={"error": "rate limit exceeded"},
        headers={
            "Retry-After": str(retry_after),
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Expose-Headers": "Retry-After",
        },
    )


@router.options("/orders")
def orders_options():
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Expose-Headers": "Retry-After",
        },
    )


@router.post("/orders")
def create_order(
    payload: OrderRequest,
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    x_client_id: Optional[str] = Header(default="default", alias="X-Client-Id"),
):
    allowed, retry_after = check_rate_limit(x_client_id or "default")

    if not allowed:
        return rate_limit_response(retry_after)

    if not idempotency_key:
        idempotency_key = str(uuid.uuid4())

    if idempotency_key in orders_by_key:
        return JSONResponse(
            content=orders_by_key[idempotency_key],
            headers={"Access-Control-Allow-Origin": "*"},
        )

    order = {
        "id": str(uuid.uuid4()),
        "item": payload.item,
        "quantity": payload.quantity,
    }

    orders_by_key[idempotency_key] = order

    return JSONResponse(
        status_code=201,
        content=order,
        headers={"Access-Control-Allow-Origin": "*"},
    )


@router.get("/orders")
def list_orders(
    limit: int = Query(default=10),
    cursor: Optional[str] = None,
    x_client_id: Optional[str] = Header(default="default", alias="X-Client-Id"),
):
    allowed, retry_after = check_rate_limit(x_client_id or "default")

    if not allowed:
        return rate_limit_response(retry_after)

    limit = max(1, min(limit, TOTAL_ORDERS))

    start = read_cursor(cursor)
    end = min(start + limit, TOTAL_ORDERS)

    items = [
        {"id": i, "name": f"order-{i}"}
        for i in range(start + 1, end + 1)
    ]

    next_cursor = make_cursor(end) if end < TOTAL_ORDERS else None

    return JSONResponse(
        content={
            "items": items,
            "next_cursor": next_cursor,
        },
        headers={"Access-Control-Allow-Origin": "*"},
    )