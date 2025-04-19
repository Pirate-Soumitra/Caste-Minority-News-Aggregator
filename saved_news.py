# saved_news.py

import json
import os

SAVE_PATH = "saved_news.json"

def load_saved_news():
    if not os.path.exists(SAVE_PATH):
        return []
    with open(SAVE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_news_item(item):
    saved = load_saved_news()
    if item not in saved:
        saved.append(item)
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(saved, f, indent=4, ensure_ascii=False)

def remove_news_item(index):
    saved = load_saved_news()
    if 0 <= index < len(saved):
        removed = saved.pop(index)
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(saved, f, indent=4, ensure_ascii=False)
        return removed
    return None