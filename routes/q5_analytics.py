from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from collections import defaultdict

router = APIRouter()

EMAIL = "23f3002902@ds.study.iitm.ac.in"
API_KEY = "ak_9wfpih2klpmm0itoz4e5jqw8"


class Event(BaseModel):
    user: str
    amount: float
    ts: int


class AnalyticsRequest(BaseModel):
    events: List[Event]


@router.post("/analytics")
def analytics(payload: AnalyticsRequest, request: Request):
    received_key = request.headers.get("x-api-key", "").strip()

    if received_key != API_KEY:
        return JSONResponse(status_code=401, content={"valid": False})

    total_events = len(payload.events)
    unique_users = len({event.user for event in payload.events})

    revenue = 0.0
    user_totals = defaultdict(float)

    for event in payload.events:
        if event.amount > 0:
            revenue += event.amount
            user_totals[event.user] += event.amount

    top_user = max(user_totals, key=user_totals.get) if user_totals else ""

    return {
        "email": EMAIL,
        "total_events": total_events,
        "unique_users": unique_users,
        "revenue": revenue,
        "top_user": top_user,
    }