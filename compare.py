import json
from ml.ml import client

def normalise(report: dict) -> dict:
    all_faults = []

    for f in report.get("critical_imperfections", []):
        all_faults.append({
            "part": f.get("part", f.get("category", "")),
            "status": f.get("status", ""),
            "severity": f.get("severity", 0),
            "bucket": "critical"
        })

    for f in report.get("non_critical_imperfections", []):
        all_faults.append({
            "part": f.get("part", f.get("category", "")),
            "status": f.get("status", ""),
            "severity": f.get("severity", 0),
            "bucket": "non_critical"
        })

    for f in report.get("restored_imperfections", []):
        all_faults.append({
            "part": f.get("part", ""),
            "status": f.get("status", ""),
            "severity": f.get("severity", 0),
            "bucket": "restored"
        })

    all_faults.sort(key=lambda x: x["severity"], reverse=True)

    return {
        "car": report["car"],
        "red_flag_score": report.get("red_flag_score", 0),
        "faults": all_faults,
        "platform_extras": {
            "tyre_life": report.get("tyre_life"),
            "repainted": report.get("repainted")
        },
        "platform": report["platform"]
    }

def generate_verdict(cars: list) -> dict:
    car_summaries = []
    for i, car in enumerate(cars):
        if "error" in car:
            continue
        faults_text = "\n".join(
            f"  - [{f['bucket'].upper()}] {f['part']} — {f['status']} (severity {f['severity']})"
            for f in car["faults"]
        )
        car_summaries.append(f"""
Car {i + 1}: {car['car']['title']}
Price: ₹{car['car']['price']:,}
KM driven: {car['car']['km']:,}
Red flag score: {car['red_flag_score']}/5
Platform: {car['platform']}
Faults:
{faults_text}
""")

    prompt = f"""You are evaluating used cars for an Indian buyer. Here are {len(car_summaries)} listings:

{"---".join(car_summaries)}

Based on fault severity, km driven, and price, recommend which car is the better buy.
Be direct and specific — mention the exact faults that influenced your decision.
If two cars are close, say so and explain what would tip the decision either way.
Keep it under 100 words.
Return JSON only, no markdown, no preamble:
{{
  "recommended_index": <0-based index of the recommended car, or null if too close to call>,
  "reason": "<your reasoning>"
}}"""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )
    text = response.text.strip().removeprefix("```json").removesuffix("```").strip()

    try:
        parsed = json.loads(text)
        return {
            "recommended_index": parsed.get("recommended_index"),
            "reason": parsed.get("reason", "")
        }
    except json.JSONDecodeError:
        return {
            "recommended_index": None,
            "reason": response.text.strip()
        }

def build_compare_response(raw_results: list, urls: list[str]) -> dict:
    normalised = [
        normalise(r) if "error" not in r else r
        for r in raw_results
    ]
    valid_cars = [c for c in normalised if "error" not in c]
    verdict = generate_verdict(normalised) if len(valid_cars) >= 2 else None
    return {"cars": normalised, "verdict": verdict}