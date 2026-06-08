import pickle

with open("severity_model.pkl", "rb") as f:
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
    X = [[
        encode(le_part, part),
        encode(le_soc, soc),
        encode(le_subcat, subcategory),
        is_critical
    ]]
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