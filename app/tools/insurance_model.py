from typing import Dict, Any

# === Replace this with your actual ML model call ===
def recommend_insurance(demographics: Dict[str, Any]) -> Dict[str, Any]:
    age = int(demographics.get("age", 0))
    income = float(demographics.get("income", 0))
    dependents = int(demographics.get("dependents", 0))
    net_worth = float(demographics.get("net_worth", 0))

    life_cover = max(income * 10, net_worth * 1.2) if dependents > 0 else income * 5
    term_years = 20 if age < 50 else 15
    health_priority = "High" if age >= 40 else "Medium"

    return {
        "coverage": {
            "term_life": {
                "recommended_cover": round(life_cover, 2),
                "term_years": term_years
            },
            "health": {"priority": health_priority},
            "disability": {"priority": "Medium" if income > 0 else "Low"},
            "home_auto": {"note": "If applicable"}
        },
        "notes": "Heuristic placeholder — swap with your ML model."
    }
