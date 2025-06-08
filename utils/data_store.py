import json
import os
from datetime import datetime

def save_user_data(user, fruit):
    path = "storage/user_wins.json"
    os.makedirs("storage", exist_ok=True)
    data = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)

    record = {
        "username": user.username,
        "first_name": user.first_name,
        "fruit": fruit,
        "time": datetime.now().isoformat()
    }

    data.setdefault(str(user.id), []).append(record)
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)