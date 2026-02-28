"""Conversation history logger."""

import json
import os
from datetime import datetime

_LOG_DIR = os.path.expanduser("~/.pipboy")
LOG_FILE = os.path.join(_LOG_DIR, "history.jsonl")


def append_turn(user_msg: str, response: str, elapsed: float) -> None:
    os.makedirs(_LOG_DIR, exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(),
        "user": user_msg,
        "assistant": response,
        "elapsed": round(elapsed, 2),
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def total_turns() -> int:
    try:
        with open(LOG_FILE) as f:
            return sum(1 for _ in f)
    except FileNotFoundError:
        return 0
