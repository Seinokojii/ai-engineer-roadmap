"""Cleaning Russian and Kyrgyz text before it reaches a model or a metric.

Reviews and messages arrive dirty: double spaces, non-breaking spaces, «ёлочки» mixed
with straight quotes, decomposed letters. Kyrgyz letters ң ө ү are data, not noise,
and must survive every step.
"""

import logging
import re
import unicodedata
from typing import Literal

from pydantic import BaseModel, Field, field_validator

log = logging.getLogger(__name__)

# Spaces that look like a space but are different characters.
_SPACES = {
    " ": " ",  # no-break space
    " ": " ",  # narrow no-break space
    " ": " ",  # thin space
    "​": "",  # zero-width space
    "﻿": "",  # byte order mark
}
_QUOTES = {
    "«": '"',
    "»": '"',
    "„": '"',
    "“": '"',
    "”": '"',
    "‘": "'",
    "’": "'",
}
_TRANSLATE = str.maketrans(_SPACES | _QUOTES)
_WHITESPACE = re.compile(r"\s+")

Script = Literal["cyrillic", "latin", "mixed", "none"]


def normalize(text: str, *, lower: bool = False) -> str:
    """Return the text with one kind of space and one kind of quote.

    NFC first, so "ё" typed as "е" + combining diaeresis becomes a single character.
    Letters are never removed: Kyrgyz ң ө ү stay as they are.
    """
    result = unicodedata.normalize("NFC", text).translate(_TRANSLATE)
    result = _WHITESPACE.sub(" ", result).strip()
    if lower:
        result = result.lower()
    if result != text:
        log.debug("normalized %r -> %r", text, result)
    return result


def script_of(text: str) -> Script:
    """Which alphabet the letters belong to. Kyrgyz letters count as Cyrillic.

    "mixed" is the signal to look closer: either a real mix ("заказ через WhatsApp")
    or a Latin "c" hiding inside a Russian word.
    """
    cyrillic = latin = 0
    for ch in text:
        if not ch.isalpha():
            continue
        name = unicodedata.name(ch, "")
        if name.startswith("CYRILLIC"):
            cyrillic += 1
        elif name.startswith("LATIN"):
            latin += 1
    if cyrillic and latin:
        return "mixed"
    if cyrillic:
        return "cyrillic"
    if latin:
        return "latin"
    return "none"


class Review(BaseModel):
    """A customer review as it enters the system: text is required, rating is optional."""

    text: str = Field(min_length=1)
    rating: int | None = Field(default=None, ge=1, le=5)

    @field_validator("text", mode="before")
    @classmethod
    def _clean_text(cls, value: object) -> object:
        # Normalize before the length check, so "   " counts as empty.
        return normalize(value) if isinstance(value, str) else value
