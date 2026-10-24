import re

_GARBAGE_PATTERNS = [
    re.compile(r"https?://\S+", re.IGNORECASE),
    re.compile(r"linkedin\.com", re.IGNORECASE),
    re.compile(r"page\s*\d+", re.IGNORECASE),
    re.compile(r"\b\d{1,4}\s*\|\s*[A-Z]"),
]

_MIN_MEANINGFUL_CHARS = 80
_MAX_GARBAGE_RATIO = 0.25


def is_good_chunk(text: str) -> tuple[bool, str]:
    if not text or not text.strip():
        return False, "empty"

    clean = text.strip()

    if len(clean) < _MIN_MEANINGFUL_CHARS:
        return False, f"too short ({len(clean)} chars)"

    garbage_chars = 0
    for pattern in _GARBAGE_PATTERNS:
        for match in pattern.finditer(clean):
            garbage_chars += len(match.group())

    garbage_ratio = garbage_chars / len(clean)
    if garbage_ratio > _MAX_GARBAGE_RATIO:
        return False, f"too much garbage ({garbage_ratio:.0%})"

    alpha_count = sum(c.isalpha() for c in clean)
    alpha_ratio = alpha_count / len(clean)
    if alpha_ratio < 0.4:
        return False, f"low alpha ratio ({alpha_ratio:.0%})"

    return True, "ok"