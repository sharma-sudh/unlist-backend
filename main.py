from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, field_validator
from contextlib import asynccontextmanager
from pydantic import field_validator, EmailStr

from analyse import analyse_single, run_compare
from compare import build_compare_response
from share import save_report as redis_save, load_report, get_cached_analyse, cache_analyse
from auth import get_google_auth_url, exchange_google_code, issue_jwt, require_auth, verify_google_id_token
from auth import upsert_user, save_report as db_save_report, get_saved_reports, delete_saved_report, register_user, login_user
from auth import init_db

@asynccontextmanager
async def lifespan(app):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request models ─────────────────────────────────────────────────────────────

class AnalyseRequest(BaseModel):
    url: str

class CompareRequest(BaseModel):
    urls: list[str]

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, v):
        if len(v) < 2:
            raise ValueError("Provide at least 2 URLs to compare.")
        if len(v) > 4:
            raise ValueError("Compare supports a maximum of 4 URLs.")
        return v

class ShareRequest(BaseModel):
    report: dict

class SaveRequest(BaseModel):
    report: dict
    title: str | None = None

class EmailAuthRequest(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number.")
        return v

class GoogleTokenRequest(BaseModel):
    id_token: str

# ── Public endpoints ───────────────────────────────────────────────────────────

@app.post("/analyse")
def analyse(req: AnalyseRequest):
    cached = get_cached_analyse(req.url)
    if cached:
        return cached
    result = analyse_single(req.url)
    cache_analyse(req.url, result)
    return result


@app.post("/compare")
def compare(req: CompareRequest):
    raw_results = run_compare(req.urls)
    valid_count = sum(1 for r in raw_results if "error" not in r)
    if valid_count < 2:
        raise HTTPException(status_code=400, detail="At least 2 listings must be valid to generate a comparison.")
    return build_compare_response(raw_results, req.urls)


@app.post("/share")
def share(req: ShareRequest):
    report_id = redis_save(req.report)
    return {"id": report_id}


@app.get("/report/{report_id}")
def get_report(report_id: str):
    report = load_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found or expired.")
    return report


# ── Auth ───────────────────────────────────────────────────────────────────────

@app.get("/auth/login")
def login():
    """Redirect the user to Google's consent screen."""
    return RedirectResponse(get_google_auth_url())


@app.get("/auth/callback")
def auth_callback(code: str):
    """Google redirects here with ?code=. Exchange it for a JWT."""
    try:
        userinfo = exchange_google_code(code)
    except Exception:
        raise HTTPException(status_code=400, detail="Google OAuth failed.")

    user = upsert_user(
        google_id=userinfo["sub"],
        email=userinfo["email"],
        name=userinfo.get("name", ""),
        picture=userinfo.get("picture", ""),
    )
    token = issue_jwt(user_id=user["id"], email=user["email"])
    return {"token": token, "user": {"name": user["name"], "email": user["email"], "picture": user["picture"]}}

@app.post("/auth/google")
def google_token_auth(req: GoogleTokenRequest):
    try:
        userinfo = verify_google_id_token(req.id_token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    user = upsert_user(
        google_id=userinfo["sub"],
        email=userinfo["email"],
        name=userinfo.get("name", ""),
        picture=userinfo.get("picture", ""),
    )
    token = issue_jwt(user_id=user["id"], email=user["email"])
    return {"token": token, "user": {"name": user["name"], "email": user["email"], "picture": user.get("picture")}}

@app.post("/auth/register")
def register(req: EmailAuthRequest):
    try:
        user = register_user(email=req.email, password=req.password, name=req.name or "")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    token = issue_jwt(user_id=user["id"], email=user["email"])
    return {"token": token, "user": {"name": user["name"], "email": user["email"], "picture": user.get("picture")}}

@app.post("/auth/login")
def email_login(req: EmailAuthRequest):
    try:
        user = login_user(email=req.email, password=req.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    token = issue_jwt(user_id=user["id"], email=user["email"])
    return {"token": token, "user": {"name": user["name"], "email": user["email"], "picture": user.get("picture")}}

@app.get("/auth/me")
def me(claims: dict = Depends(require_auth)):
    return {"user_id": claims["sub"], "email": claims["email"]}


# ── Protected: saved reports ───────────────────────────────────────────────────

@app.post("/saved")
def save(req: SaveRequest, claims: dict = Depends(require_auth)):
    row = db_save_report(user_id=int(claims["sub"]), report=req.report, title=req.title)
    return row


@app.get("/saved")
def list_saved(claims: dict = Depends(require_auth)):
    return get_saved_reports(user_id=int(claims["sub"]))


@app.delete("/saved/{report_id}")
def delete_saved(report_id: int, claims: dict = Depends(require_auth)):
    deleted = delete_saved_report(user_id=int(claims["sub"]), report_id=report_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Report not found.")
    return {"deleted": True}
