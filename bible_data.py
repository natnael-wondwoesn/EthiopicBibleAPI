"""Shared Bible data layer — loads all 66 books into memory once."""

from __future__ import annotations

import json
import os
import random
import logging

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "Books")

# In-memory cache: all books loaded once
_book_cache: dict[str, dict] = {}


def load_all_books():
    """Load all book JSON files into memory."""
    if _book_cache:
        return  # already loaded
    count = 0
    for filename in os.listdir(DATA_DIR):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(DATA_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                book_name = filename.removesuffix(".json")
                _book_cache[book_name] = json.load(f)
                count += 1
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to load %s: %s", filename, e)
    logger.info("Loaded %d books into cache", count)


def get_book(book_name: str) -> dict | None:
    """Look up a book by name."""
    return _book_cache.get(book_name)


def get_all_book_names() -> list[str]:
    """Return sorted list of all book names."""
    return sorted(_book_cache.keys())


def get_random_verse() -> dict:
    """Return a random verse with its reference info."""
    book_name = random.choice(list(_book_cache.keys()))
    book = _book_cache[book_name]
    chapter = random.choice(book["chapters"])
    verse_idx = random.randrange(len(chapter["verses"]))
    return {
        "book": book["title"],
        "chapter": chapter["chapter"],
        "verse_number": verse_idx + 1,
        "text": chapter["verses"][verse_idx],
    }


def get_daily_verse(day_offset: int = 0) -> dict:
    """Return a deterministic verse based on the day number.

    Using day_offset (e.g. days since epoch) ensures the same verse
    is returned all day but changes each day.
    """
    all_verses = []
    for book_name in sorted(_book_cache.keys()):
        book = _book_cache[book_name]
        for chapter in book["chapters"]:
            for idx, text in enumerate(chapter["verses"]):
                all_verses.append({
                    "book": book["title"],
                    "chapter": chapter["chapter"],
                    "verse_number": idx + 1,
                    "text": text,
                })
    # Cycle through all verses deterministically
    verse = all_verses[day_offset % len(all_verses)]
    return verse
