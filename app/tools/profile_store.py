from typing import Dict, Any
from ..memory import JSONProfileStore

_store = JSONProfileStore()

def upsert_profile(user_id: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    current = _store.load(user_id)
    current.update(profile or {})
    _store.save(user_id, current)
    return current

def get_profile(user_id: str) -> Dict[str, Any]:
    return _store.load(user_id)
