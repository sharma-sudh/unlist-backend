from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from analyse import analyse_single, run_compare
from compare import build_compare_response

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/analyse")
def analyse(req: AnalyseRequest):
    return analyse_single(req.url)

@app.post("/compare")
def compare(req: CompareRequest):
    raw_results = run_compare(req.urls)
    valid_count = sum(1 for r in raw_results if "error" not in r)
    if valid_count < 2:
        raise HTTPException(status_code=400, detail="At least 2 listings must be valid to generate a comparison.")
    return build_compare_response(raw_results, req.urls)