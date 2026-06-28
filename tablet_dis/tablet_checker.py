"""
Tablet / medicine search validation.

All search-bar validation logic lives in this module.
"""

import re
from dataclasses import dataclass

from django.db.models import Q

from tablet_dis.models import Tablet

# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------
INVALID_INPUT = "Invalid input."
MEDICINE_NOT_FOUND = "Medicine not found."

# Allowed: letters (Latin + Tamil), digits, spaces, hyphen, parentheses, period
_ALLOWED_CHARS = re.compile(r"^[a-zA-Z0-9\u0B80-\u0BFF\s\-().]+$")
_TAMIL_RANGE = re.compile(r"[\u0B80-\u0BFF]")

# ---------------------------------------------------------------------------
# Blocklists
# ---------------------------------------------------------------------------
_KEYBOARD_MASH = frozenset(
    {
        "asdf", "asdfg", "asdfgh", "qwert", "qwerty", "qwertyuiop",
        "zxcvb", "zxcvbn", "xyz", "xyzabc", "hjkl", "dfghjk",
        "abcdef", "abcabc", "testtest", "blahblah",
    }
)

_BLOCKED_WORDS = frozenset(
    {
        # Keyboard / junk
        "asdfgh", "qwerty", "xyzabc", "zxcvbn", "hjkl",
        # People names
        "suresh", "john", "jane", "michael", "david", "maria",
        "ravi", "kumar", "priya", "alex", "sarah", "james",
        # Cities / countries
        "bangalore", "bengaluru", "chennai", "mumbai", "delhi",
        "india", "america", "london", "paris", "tokyo",
        # Fruits / food
        "apple", "banana", "orange", "mango", "grape", "tomato",
        # Animals
        "dog", "cat", "elephant", "tiger", "lion", "monkey", "horse",
        # Other unrelated
        "hello", "world", "testing", "random", "nothing", "something",
        "computer", "mobile", "phone", "internet", "google", "facebook",
    }
)

# Medicine-related tokens that should never be blocked
_MEDICINE_HINTS = frozenset(
    {
        "tablet", "tablets", "capsule", "capsules", "syrup", "injection",
        "mg", "ml", "vitamin", "paracetamol", "amoxicillin", "crocin",
        "dolo", "aspirin", "ibuprofen", "metformin", "insulin",
    }
)


@dataclass(frozen=True)
class CheckResult:
    """Result of a search validation check."""

    ok: bool
    normalized: str = ""
    message: str = ""


def _is_tamil_text(text: str) -> bool:
    return bool(_TAMIL_RANGE.search(text))


def normalize_input(raw: str) -> str:
    """
    Trim, lowercase (Latin only), collapse spaces, remove unnecessary punctuation.
    Keeps hyphens and parentheses used in medicine names.
    """
    if not raw:
        return ""

    text = raw.strip()
    text = re.sub(r"[^\w\s\-().\u0B80-\u0BFF]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()

    if _is_tamil_text(text):
        return text

    return text.lower()


def _is_digits_only(text: str) -> bool:
    compact = re.sub(r"[\s\-().]", "", text)
    return bool(compact) and compact.isdigit()


def _has_allowed_characters(text: str) -> bool:
    return bool(_ALLOWED_CHARS.match(text))


def _is_keyboard_mash(text: str) -> bool:
    compact = re.sub(r"[\s\-().0-9]", "", text.lower())
    if not compact:
        return False
    if compact in _KEYBOARD_MASH:
        return True
    # Consecutive keyboard-row letters with no vowels (e.g. "asdfgh")
    if len(compact) >= 5 and not re.search(r"[aeiou]", compact):
        if re.fullmatch(r"[a-z]+", compact):
            return True
    return False


def _contains_blocked_word(normalized: str) -> bool:
    if _is_tamil_text(normalized):
        return False

    tokens = normalized.split()
    for token in tokens:
        word = re.sub(r"[^a-z]", "", token.lower())
        if not word or len(word) == 1:
            continue
        if word in _MEDICINE_HINTS:
            continue
        if word in _BLOCKED_WORDS:
            return True
        if word in _KEYBOARD_MASH:
            return True
    return False


def validate_input_format(raw: str) -> CheckResult:
    """
    Validate search text format only (no database lookup).

    Returns CheckResult(ok=True, normalized=...) when input is acceptable.
    """
    trimmed = (raw or "").strip()
    if not trimmed:
        return CheckResult(ok=False, message=INVALID_INPUT)

    if not _has_allowed_characters(trimmed):
        return CheckResult(ok=False, message=INVALID_INPUT)

    normalized = normalize_input(trimmed)
    if not normalized:
        return CheckResult(ok=False, message=INVALID_INPUT)

    if _is_digits_only(normalized):
        return CheckResult(ok=False, message=INVALID_INPUT)

    if _is_keyboard_mash(normalized):
        return CheckResult(ok=False, message=INVALID_INPUT)

    if _contains_blocked_word(normalized):
        return CheckResult(ok=False, message=INVALID_INPUT)

    return CheckResult(ok=True, normalized=normalized)


def medicine_matches_db(normalized: str, original: str | None = None) -> bool:
    """
    True if input exactly or partially matches a medicine name in the database.
    Case-insensitive for English; Tamil matched as-is.
    """
    query = (original or normalized or "").strip()
    if not query:
        return False

    return Tablet.objects.filter(
        Q(name_en__icontains=query) | Q(name_ta__icontains=query)
    ).exists()


def check_search_input(raw: str, *, require_db_match: bool = False) -> CheckResult:
    """
    Full search validation pipeline:

    1. Trim & normalize
    2. Reject invalid format
    3. Optionally require DB partial match
    4. Return normalized query ready for DB/API search
    """
    fmt = validate_input_format(raw)
    if not fmt.ok:
        return fmt

    if require_db_match and not medicine_matches_db(fmt.normalized, raw.strip()):
        return CheckResult(ok=False, normalized=fmt.normalized, message=MEDICINE_NOT_FOUND)

    # Return original trimmed casing for display/API; normalized for comparisons
    return CheckResult(ok=True, normalized=raw.strip(), message="")
