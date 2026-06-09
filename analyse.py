from fastapi import HTTPException
from scrapers.spinny_scraper import fetch_report as fetch_spinny
from scrapers.cars24_scraper import fetch_report as fetch_cars24
from parsers.spinny_parser import parse_report as parse_spinny
from parsers.cars24_parser import parse_report as parse_cars24
from ml.ml import enrich_faults, generate_summary
from concurrent.futures import ThreadPoolExecutor, as_completed

def detect_platform(url: str) -> str:
    if "spinny.com" in url:
        return "spinny"
    if "cars24.com" in url or "cars24.world" in url:
        return "cars24"
    return "unknown"

def analyse_single(url: str) -> dict:
    url = url.strip()
    platform = detect_platform(url)

    if platform == "unknown":
        raise HTTPException(status_code=400, detail="Unsupported platform. Paste a Spinny or Cars24 listing URL.")

    try:
        if platform == "spinny":
            raw = fetch_spinny(url)
            if not raw:
                raise HTTPException(status_code=400, detail="Couldn't extract a car ID. Make sure this is a specific car listing, not a search page.")
            result = parse_spinny(raw)
            result["car"] = raw["car"]

        elif platform == "cars24":
            raw = fetch_cars24(url)
            if not raw:
                raise HTTPException(status_code=400, detail="Couldn't extract a car ID. Make sure this is a specific car listing, not a search page.")
            if not raw.get("categories") and not raw.get("checkpoints"):
                raise HTTPException(status_code=404, detail="No inspection data found. This may be a Cars24 direct seller listing — Unlist only supports Cars24 owned stock and all Spinny listings.")
            result = parse_cars24(raw)
            result["car"] = raw["car"]

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Couldn't fetch this listing. It may have been sold or removed.")

    result["critical_imperfections"] = enrich_faults(result["critical_imperfections"], is_critical_default=1)
    result["non_critical_imperfections"] = enrich_faults(result["non_critical_imperfections"])

    if platform == "spinny":
        result["restored_imperfections"] = enrich_faults(result.get("restored_imperfections", []))
        result["checklist"] = [
            f"Check {f.get('part', '')} — {f.get('status', '')}"
            for f in result["critical_imperfections"]
        ]
    else:
        result.pop("restored_imperfections", None)
        result["checklist"] = [
            f"Check {f.get('part', '')} — {f.get('status', '')}"
            for f in result["non_critical_imperfections"]
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

def run_compare(urls: list[str]) -> list[dict]:
    results = [None] * len(urls)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(analyse_single, url): i for i, url in enumerate(urls)}
        for future in as_completed(futures):
            i = futures[future]
            try:
                results[i] = future.result()
            except HTTPException as e:
                results[i] = {"error": e.detail, "url": urls[i]}
            except Exception:
                results[i] = {"error": "Unexpected error", "url": urls[i]}
    return results