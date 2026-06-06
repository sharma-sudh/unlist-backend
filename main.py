from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scraper import fetch_report
from parser import parse_report

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this later
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyseRequest(BaseModel):
    url: str

@app.post("/analyse")
def analyse(req: AnalyseRequest):
    raw = fetch_report(req.url)
    if not raw:
        raise HTTPException(status_code=400, detail="Invalid or unsupported URL")
    result = parse_report(raw)
    result["car"] = raw["car"]
    return result