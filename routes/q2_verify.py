from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt

router = APIRouter()

ISSUER = "https://idp.exam.local"

AUDIENCE = "tds-abc12345.apps.exam.local"

PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQE...
...
-----END PUBLIC KEY-----
"""


class TokenRequest(BaseModel):
    token: str


@router.post("/verify")
def verify_token(request: TokenRequest):
    try:
        payload = jwt.decode(
            request.token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            issuer=ISSUER,
            audience=AUDIENCE,
        )

        return {
            "valid": True,
            "email": payload.get("email"),
            "sub": payload.get("sub"),
            "aud": payload.get("aud"),
        }

    except Exception:
        return JSONResponse(
            status_code=401,
            content={"valid": False}
        )