import pickle
import os
from dotenv import load_dotenv
from google import genai
import pandas as pd

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "severity_model.pkl")

with open(_MODEL_PATH, "rb") as f:
    bundle = pickle.load(f)

model = bundle["model"]
le_soc = bundle["le_soc"]
le_part = bundle["le_part"]
le_subcat = bundle["le_subcat"]

def encode(le, value):
    value = value or "unknown"
    if value in le.classes_:
        return le.transform([value])[0]
    return -1  # unseen label

def predict_severity(part: str, soc: str, subcategory: str, is_critical: int) -> int:
    X = pd.DataFrame([[
        encode(le_part, part),
        encode(le_soc, soc),
        encode(le_subcat, subcategory),
        is_critical
    ]], columns=["part_enc", "soc_enc", "subcat_enc", "is_critical"])
    return int(model.predict(X)[0])

def enrich_faults(faults: list, is_critical_default: int = 0) -> list:
    enriched = []
    for fault in faults:
        part = fault.get("part", fault.get("category", ""))
        soc = fault.get("status", fault.get("description", ""))
        subcategory = fault.get("subcategory", fault.get("category", ""))
        is_critical = fault.get("is_critical", is_critical_default)
        severity = predict_severity(part, soc, subcategory, int(is_critical))
        enriched.append({**fault, "severity": severity})
    return sorted(enriched, key=lambda x: x["severity"], reverse=True)

def generate_summary(car: dict, critical: list, non_critical: list, restored: list, replaced: list, repainted: bool = False) -> str:
    faults_text = ""
    if critical:
        faults_text += "Critical issues: " + ", ".join(
        f"{f.get('part', f.get('category', ''))} ({f.get('status', f.get('description', ''))})"
        for f in critical
    ) + ". "
    if non_critical:
        faults_text += "Minor issues: " + ", ".join(
        f"{f.get('part', f.get('category', ''))} ({f.get('status', f.get('description', ''))})"
        for f in non_critical
    ) + ". "
    if restored:
        faults_text += "Restored parts: " + ", ".join(f['part'] for f in restored) + ". "
    if replaced:
        faults_text += "Replaced parts: " + ", ".join(f['part'] for f in replaced) + ". "
    if repainted:
        faults_text += "Car has repainted panels. "

    prompt = (
        f"You are a car inspection expert helping an Indian used car buyer understand an inspection report. "
        f"Write a 2-3 sentence plain English summary of the key findings. "
        f"Be direct and honest about the severity of issues. "
        f"End with a practical suggestion — what to check, ask, or negotiate on — but do not tell the buyer whether to buy or not. "
        f"Do not use bullet points.\n\n"
        f"Car: {car['title']}, {car['km']}km, ₹{car['price']:,}\n"
        f"Inspection findings: {faults_text if faults_text else 'No significant issues found.'}"
    )

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )
    return response.text.strip()