from typing import Dict, Any

# === Replace this with your actual ML model call ===
def predict_savings_amount(demographics: Dict[str, Any]) -> Dict[str, Any]:
    income = float(demographics.get("income", 0))
    dependents = int(demographics.get("dependents", 0))
    net_worth = float(demographics.get("net_worth", 0))
    age = int(demographics.get("age", 0))

    # Simple heuristic placeholder (replace with your model output)
    base_rate = 0.18 if dependents <= 1 else 0.14
    if net_worth < income * 1.5:
        base_rate += 0.02  # encourage higher savings early
    if age < 35:
        base_rate += 0.01

    annual = income * base_rate
    monthly = annual / 12.0

    return {
        "suggested_savings_rate": round(base_rate, 4),
        "annual_savings": round(annual, 2),
        "monthly_savings": round(monthly, 2),
        "notes": "Heuristic placeholder — swap with your ML model."
    }
