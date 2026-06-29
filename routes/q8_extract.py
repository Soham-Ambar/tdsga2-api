from fastapi import APIRouter
from pydantic import BaseModel
import re

router = APIRouter()


class ExtractRequest(BaseModel):
    text: str


class ExtractResponse(BaseModel):
    vendor: str
    amount: float
    currency: str
    date: str


def find_vendor(text: str) -> str:
    patterns = [
        r"vendor[:\s]+([A-Za-z0-9\-\s&.,]+?)(?:\n|,|\.|$)",
        r"from[:\s]+([A-Za-z0-9\-\s&.,]+?)(?:\n|,|\.|$)",
        r"([A-Z][A-Za-z0-9\-]+(?:\s+[A-Za-z0-9\-]+)*\s+(?:Industries Ltd|Ltd\.?|Inc\.?|LLC|Corp\.?|Corporation|Company))",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip(" .,\n")

    return ""


def find_amount(text: str) -> float:
    patterns = [
        r"(?:total|amount|due|payment)[^\d]*(\d+(?:\.\d{1,2})?)",
        r"(?:USD|EUR|GBP)\s*(\d+(?:\.\d{1,2})?)",
        r"(\d+(?:\.\d{1,2})?)\s*(?:USD|EUR|GBP)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))

    return 0.0


def find_currency(text: str) -> str:
    match = re.search(r"\b(USD|EUR|GBP)\b", text, re.IGNORECASE)
    return match.group(1).upper() if match else ""


def find_date(text: str) -> str:
    match = re.search(r"\b(2026-\d{2}-\d{2})\b", text)
    return match.group(1) if match else ""


@router.post("/extract", response_model=ExtractResponse)
def extract_invoice(payload: ExtractRequest):
    text = payload.text or ""

    return {
        "vendor": find_vendor(text),
        "amount": find_amount(text),
        "currency": find_currency(text),
        "date": find_date(text),
    }