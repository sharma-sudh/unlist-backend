import json

def parse_report(raw_report):
    parts = raw_report["parts"]

    critical_imperfections = []
    non_critical_imperfections = []
    restored_imperfections = []
    replaced_parts = []
    checklist = []

    for subcat_key, part_list in parts.items():
        subcat_display = subcat_key.replace("_", " ").title()

        for part in part_list:
            soc = (part.get("soc") or "").strip()
            name = part["name"]
            is_critical = part["is_critical"]
            condition = part["condition"]

            entry = {
                "subcategory": subcat_display,
                "part": name,
                "status": soc
            }

            # catch replaced/repainted regardless of condition bucket
            if soc.lower() in ["replaced", "repainted"]:
                replaced_parts.append(entry)
                continue

            if condition != "imperfection":
                continue

            if soc.lower() == "restored":
                restored_imperfections.append(entry)
            elif is_critical:
                critical_imperfections.append(entry)
            else:
                non_critical_imperfections.append(entry)

    # checklist only from actual unresolved critical issues
    for item in critical_imperfections:
        checklist.append(f"Check {item['part']} — {item['status']}")

    return {
        "critical_imperfections": critical_imperfections,
        "non_critical_imperfections": non_critical_imperfections,
        "restored_imperfections": restored_imperfections,
        "replaced_parts": replaced_parts,
        "checklist": checklist,
        "red_flag_score": len(critical_imperfections)
    }


if __name__ == "__main__":
    from scraper import fetch_report
    url = "https://www.spinny.com/buy-used-cars/jaipur/hyundai/elite-i20/sportz-plus-12-ajmer-road-2019/29483061/"
    raw = fetch_report(url)
    result = parse_report(raw)
    print(json.dumps(result, indent=2))