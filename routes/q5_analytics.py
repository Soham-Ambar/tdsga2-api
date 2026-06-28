from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from collections import defaultdict

router = APIRouter()

EMAIL = "23f3002902@ds.study.iitm.ac.in"
API_KEY = "ak_9wfphih2klpmm0itoz4e5jqw8"


class Event(BaseModel):
    user: str
    amount: float
    ts: int


class AnalyticsRequest(BaseModel):
    events: List[Event]


@router.post("/analytics")
def analytics(
    request: AnalyticsRequest,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    if x_api_key != API_KEY:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    total_events = len(request.events)
    unique_users = len(set(event.user for event in request.events))

    revenue = 0.0
    positive_totals = defaultdict(float)

    for event in request.events:
        if event.amount > 0:
            revenue += event.amount
            positive_totals[event.user] += event.amount

    top_user = None
    if positive_totals:
        top_user = max(positive_totals, key=positive_totals.get)

    return {
        "email": EMAIL,
        "total_events": total_events,
        "unique_users": unique_users,
        "revenue": revenue,
        "top_user": top_user,
    }