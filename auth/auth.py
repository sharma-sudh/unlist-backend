import os
import jwt
import requests
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI  = os.getenv("GOOGLE_REDIRECT_URI")   # e.g. https://your-backend.onrender.com/auth/callback
JWT_SECRET           = os.getenv("JWT_SECRET")
JWT_ALGORITHM        = "HS256"
JWT_EXPIRY_DAYS      = 30

bearer_scheme = HTTPBearer()


# ── OAuth ──────────────────────────────────────────────────────────────────────

def get_google_auth_url() -> str:
    params = (
        f"client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=openid%20email%20profile"
        f"&access_type=offline"
    )
    return f"https://accounts.google.com/o/oauth2/v2/auth?{params}"


def exchange_google_code(code: str) -> dict:
    """Exchange auth code for Google user info."""
    token_res = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        },
    )
    token_res.raise_for_status()
    access_token = token_res.json()["access_token"]

    userinfo_res = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    userinfo_res.raise_for_status()
    return userinfo_res.json()   # sub, email, name, picture

def verify_google_id_token(id_token: str) -> dict:
    res = requests.get(
        "https://oauth2.googleapis.com/tokeninfo",
        params={"id_token": id_token}
    )
    if res.status_code != 200:
        raise ValueError("Invalid Google ID token.")
    data = res.json()
    if data.get("aud") != GOOGLE_CLIENT_ID:
        raise ValueError("Token audience mismatch.")
    return data  # contains sub, email, name, picture

# ── JWT ────────────────────────────────────────────────────────────────────────

def issue_jwt(user_id: int, email: str) -> str:
    payload = {
        "sub": str(user_id),  # cast to string
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRY_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")


# ── FastAPI dependency ─────────────────────────────────────────────────────────

def require_auth(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> dict:
    """Inject into any endpoint that needs a logged-in user."""
    return decode_jwt(credentials.credentials)