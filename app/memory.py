import json, os
from typing import Dict, Any
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "profiles")
os.makedirs(DATA_DIR, exist_ok=True)

class JSONProfileStore:
    def __init__(self, base_dir: str = DATA_DIR):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _path(self, user_id: str) -> str:
        return os.path.join(self.base_dir, f"{user_id}.json")

    def load(self, user_id: str) -> Dict[str, Any]:
        try:
            with open(self._path(user_id), "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save(self, user_id: str, profile: Dict[str, Any]) -> None:
        profile = dict(profile)
        profile["_updated_at"] = datetime.utcnow().isoformat()
        with open(self._path(user_id), "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2)

# Light-weight conversational buffer memory
class ConversationBuffer:
    def __init__(self, window: int = 6):
        self.window = window
        self.messages = []  # list of dicts {"role": "...", "content": "..."}

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        # Keep last N messages
        self.messages = self.messages[-(self.window*2):]

    def get(self):
        return list(self.messages)
