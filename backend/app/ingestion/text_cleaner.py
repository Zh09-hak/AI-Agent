import re
from collections import Counter

_URL_RE = re.compile(r"https?://[^\s<>\"')\]]+|www\.[^\s<>\"')\]]+", re.IGNORECASE)
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_LINKEDIN_RE = re.compile(r"linkedin\.com/in/[a-zA-Z0-9_-]+/?", re.IGNORECASE)
_PAGE_NUM_RE = re.compile(r"(?im)^\s*(?:page\s*)?\d{1,4}\s*(?:\|\s*[A-Za-z][^\n]{0,60})?\s*$")
_CHAPTER_HEADER_RE = re.compile(r"(?im)^\s*[A-Z][^\n]{2,80}\s*\|\s*\d{1,4}\s*$")
_TOC_RE = re.compile(r"(?im)^\s*(?:table\s+of\s+contents|contents|summary\s+and\s+outlook)[^\n]*\s*$")

_AUTHOR_NOISE_PATTERNS = [
    r"steve\s+nouri",
    r"ste\s*v\s*e\s+n\s*o\s*u\s*r\s*i",
    r"andreas\s+c\.?\s*m[üu]ller",
    r"sarah\s+guido",
    r"introduction\s+to\s+machine\s+learning\s+with\s+python",
    r"o'?reilly\s+media",
    r"safari\s+books\s+online",
]
_AUTHOR_NOISE_RES = [re.compile(p, re.IGNORECASE) for p in _AUTHOR_NOISE_PATTERNS]

_TORN_WORD_LEADING_RE = re.compile(r"\b([a-zA-Z])\s+([a-z]{2,})\b")
_TORN_WORD_TRAILING_RE = re.compile(r"\b([a-zA-Z]{3,}[a-z])\s+([a-z])\b")
_MULTI_SPACE_RE = re.compile(r"[ \t]{2,}")
_MULTI_NEWLINE_RE = re.compile(r"\n{3,}")
_HYPHENATED_BREAK_RE = re.compile(r"([a-zA-Z])-\s*\n\s*([a-zA-Z])")


def _detect_repeated_lines(text: str, min_count: int = 3) -> set[str]:
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return set()
    counter = Counter(lines)
    return {line for line, cnt in counter.items()
            if cnt >= min_count and len(line) < 120}


def _remove_torn_words(text: str) -> str:
    text = _TORN_WORD_LEADING_RE.sub(lambda m: m.group(1) + m.group(2), text)
    text = _TORN_WORD_TRAILING_RE.sub(lambda m: m.group(1) + m.group(2), text)
    return text


def clean_text(text: str) -> str:
    if not text:
        return ""

    original_len = len(text)
    repeated_lines = _detect_repeated_lines(text, min_count=3)

    text = _HYPHENATED_BREAK_RE.sub(r"\1\2", text)
    text = _remove_torn_words(text)
    text = _URL_RE.sub(" ", text)
    text = _EMAIL_RE.sub(" ", text)
    text = _LINKEDIN_RE.sub(" ", text)

    for regex in _AUTHOR_NOISE_RES:
        text = regex.sub(" ", text)

    clean_lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            clean_lines.append("")
            continue
        if stripped in repeated_lines:
            continue
        if _PAGE_NUM_RE.match(stripped):
            continue
        if _CHAPTER_HEADER_RE.match(stripped):
            continue
        if _TOC_RE.match(stripped):
            continue
        if len(stripped) < 3:
            continue
        alpha_ratio = sum(c.isalpha() for c in stripped) / len(stripped)
        if alpha_ratio < 0.3 and len(stripped) < 40:
            continue
        clean_lines.append(line)

    text = "\n".join(clean_lines)
    text = _MULTI_SPACE_RE.sub(" ", text)
    text = _MULTI_NEWLINE_RE.sub("\n\n", text)
    text = re.sub(r" +", " ", text)
    text = text.strip()

    removed_pct = (1 - len(text) / max(original_len, 1)) * 100
    print(f"  [cleaner] {original_len:,} → {len(text):,} chars (removed {removed_pct:.1f}% noise)")
    return text