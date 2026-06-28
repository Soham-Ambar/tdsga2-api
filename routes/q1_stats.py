from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse, Response
import time
import uuid

router = APIRouter()

# Replace this only if your logged-in exam email is different.
EMAIL = "23f3002902@ds.study.iitm.ac.in"

# IMPORTANT: Replace this with the exact assigned origin shown in your exam panel.
# Example: ALLOWED_ORIGIN = "https://exam.sanand.workers.dev"
ALLOWED_ORIGIN = "https://dash-sw2mlo.example.com"


def add_required_headers(response: Response, start_time: float) -> None:
    """Add mandatory middleware-like headers to every Q1 response."""
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start_time:.6f}"


def apply_strict_cors(request: Request, response: Response) -> None:
    """Only the assigned allowed origin gets Access-Control-Allow-Origin."""
    origin = request.headers.get("origin")
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
        response.headers["Vary"] = "Origin"


@router.options("/stats")
def stats_preflight(request: Request):
    """Handle browser preflight for /stats."""
    start = time.perf_counter()
    response = Response(status_code=204)

    apply_strict_cors(request, response)

    # Only useful for the allowed origin. Evil origins will not get ACAO.
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"

    add_required_headers(response, start)
    return response


@router.get("/stats")
def stats(request: Request, values: str = Query(...)):
    """
    Example:
    /stats?values=1,2,3,4
    Returns count, sum, min, max, and mean.
    """
    start = time.perf_counter()

    try:
        nums = [int(part.strip()) for part in values.split(",") if part.strip() != ""]
        if not nums:
            raise ValueError("No numbers provided")

        data = {
            "email": EMAIL,
            "count": len(nums),
            "sum": sum(nums),
            "min": min(nums),
            "max": max(nums),
            "mean": sum(nums) / len(nums),
        }
        response = JSONResponse(content=data, status_code=200)

    except Exception:
        response = JSONResponse(
            content={"error": "values must be comma-separated integers"},
            status_code=400,
        )

    apply_strict_cors(request, response)
    add_required_headers(response, start)
    return response
