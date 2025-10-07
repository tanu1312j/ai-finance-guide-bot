from typing import Dict, Any, Tuple

REQUIRED_DEMOGRAPHICS = ["age", "marital_status", "dependents", "income", "net_worth"]

def validate_demographics(demo: Dict[str, Any]) -> Tuple[bool, str]:
    missing = [k for k in REQUIRED_DEMOGRAPHICS if demo.get(k) in (None, "", [])]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    if not (0 < int(demo.get("age", 0)) < 120):
        return False, "Age must be between 1 and 119."
    if float(demo.get("income", 0)) < 0 or float(demo.get("net_worth", 0)) < 0:
        return False, "Income and net worth must be non-negative."
    return True, ""

def pii_minimize(demo: Dict[str, Any]) -> Dict[str, Any]:
    # Remove fields we do not need downstream (example).
    demo = dict(demo)
    demo.pop("full_name", None)
    demo.pop("address", None)
    demo.pop("ssn", None)
    return demo

DISCLAIMER = "Disclaimer: This is general information, not financial advice."
