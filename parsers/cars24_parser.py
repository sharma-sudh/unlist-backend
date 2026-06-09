def parse_report(raw_report):
    checkpoints = raw_report["checkpoints"]
    categories = raw_report["categories"]

    critical_imperfections = []
    non_critical_imperfections = []

    for key, cat in categories.items():
        if cat["status"] == "ERROR" and cat["issues"] > 0:
            critical_imperfections.append({
                "category": cat["label"],
                "issues": cat["issues"],
                "description": cat["description"]
            })

    for category, parts in checkpoints.items():
        for part in parts:
            if part["status"] == "ERROR" and part["infos"]:
                for info in part["infos"]:
                    non_critical_imperfections.append({
                        "category": category,
                        "part": part["label"],
                        "status": info.get("label", ""),
                        "description": info.get("description", "")
                    })

    checklist = [
        f"Check {item['part']} — {item['status']}"
        for item in non_critical_imperfections
    ]

    return {
        "repainted": raw_report["repainted"],
        "critical_imperfections": critical_imperfections,
        "non_critical_imperfections": non_critical_imperfections,
        "tyre_life": raw_report["tyre_life"],
        "checklist": checklist,
        "red_flag_score": len(critical_imperfections)
    }