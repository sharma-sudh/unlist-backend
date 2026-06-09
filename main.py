from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from spinny_scraper import fetch_report as fetch_spinny
from cars24_scraper import fetch_report as fetch_cars24
from spinny_parser import parse_report as parse_spinny
from cars24_parser import parse_report as parse_cars24
from ml import enrich_faults, generate_summary

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyseRequest(BaseModel):
    url: str

def detect_platform(url: str) -> str:
    if "spinny.com" in url:
        return "spinny"
    if "cars24.com" in url or "cars24.world" in url:
        return "cars24"
    return "unknown"

@app.post("/analyse")
def analyse(req: AnalyseRequest):
    platform = detect_platform(req.url)

    if platform == "spinny":
        raw = fetch_spinny(req.url)
        if not raw:
            raise HTTPException(status_code=400, detail="Invalid or unsupported Spinny URL")
        result = parse_spinny(raw)
        result["car"] = raw["car"]

    elif platform == "cars24":
        raw = fetch_cars24(req.url)
        if not raw:
            raise HTTPException(status_code=400, detail="Invalid or unsupported Cars24 URL")
        result = parse_cars24(raw)
        result["car"] = raw["car"]

    else:
        raise HTTPException(status_code=400, detail="Unsupported platform. Supported: spinny, cars24")

    result["critical_imperfections"] = enrich_faults(result["critical_imperfections"], is_critical_default=1)
    result["non_critical_imperfections"] = enrich_faults(result["non_critical_imperfections"])
    result["restored_imperfections"] = enrich_faults(result.get("restored_imperfections", []))

    result["checklist"] = [
        f"Check {f['part']} — {f['status']}"
        for f in result["critical_imperfections"]
    ]

    result["summary"] = generate_summary(
        car=result["car"],
        critical=result["critical_imperfections"],
        non_critical=result["non_critical_imperfections"],
        restored=result.get("restored_imperfections", []),
        replaced=result.get("replaced_parts", []),
        repainted=result.get("repainted", False)
    )

    result["platform"] = platform
    return result