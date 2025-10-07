from typing import Dict, Any
def market_snapshot() -> Dict[str, Any]:
    # Stub for demo; wire a real data source later
    return {
        "equities": {"SPY": "snapshot unavailable in demo"},
        "bonds": {"AGG": "snapshot unavailable in demo"},
        "gold": {"GLD": "snapshot unavailable in demo"},
        "crypto": {"BTC": "snapshot unavailable in demo"}
    }
