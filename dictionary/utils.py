"""
Diacritic-stripping utilities for VLT/PLT search.

DIACRITIC_STRIP_MAP is the single source of truth: it drives both
strip_diacritics() (Python) and diacritic_strip_sql_args() (SQL translate()
args for the GeneratedField), so the two can never drift out of sync.

Assumes all VLT/PLT/stripped fields are lowercase-only (enforced at the
model/DB layer) — no uppercase variants are included here.
"""

PA_TO_VLT = {
    'ٴ': "ʾ",
    'ٔ': "ʾ",
    'ئ': "ʾ",
    'آ': "ā",
    'ا': "a",
    'ب': "b",
    'ت': "t",
    'ث': "ş",
    'ج': "j",
    'ح': "ḥ",
    'خ': "ḫ",
    'د': "d",
    'ذ': "ź",
    'ر': "r",
    'ز': "z",
    'س': "s",
    'ش': "š",
    'ص': "ṣ",
    'ض': "ż",
    'ط': "ṭ",
    'ظ': "ẓ",
    'ع': "ʿ",
    'غ': "ǧ",
    'ف': "f",
    'ق': "q",
    'ل': "l",
    'م': "m",
    'ن': "n",
    'ه': "h",
    'و': "w",
    'ُ': "u",
    'ّ': "~",
    'پ': "p",
    'چ': "č",
    'ژ': "ž",
    'ک': "k",
    'گ': "g",
    'ی': "y",
    'ە': "h",
    'ة': "t",
    'َ': "a",
    'ِ': "i",
    'ٍ': "n",
    'ً': "n",
    'ڭ': "ŋ",
}

DIACRITIC_STRIP_MAP = {
    "ä": "a",
    "ö": "o",
    "ü": "u",
    "ā": "a",
    "č": "c",   # چ
    "ī": "i",
    "š": "s",   # ش
    "ş": "s",   # ژ
    "ū": "u",
    "ź": "z",   # ذ
    "ż": "z",   # ض
    "ǧ": "g",   # غ
    "ʿ": "'",   # ع (ayin)
    "ʾ": "'",   # ء (hamza)
    "ḥ": "h",   # ح
    "ḫ": "h",   # خ
    "ṗ": "p",   # ف
    "ṣ": "s",   # ص
    "ṭ": "t",   # ط
    "ẓ": "z",   # ظ
}


def strip_diacritics(text: str) -> str:
    """
    Python-side stripping, for use outside the database
    (e.g. one-off scripts, tests, shell/admin logic).
    """
    return text.translate(str.maketrans(DIACRITIC_STRIP_MAP))

def to_vlt(persoarabic: str) -> str:
    """
    Convert a Perso-Arabic string to VLT.
    """
    return persoarabic.translate(str.maketrans(PA_TO_VLT))

def to_ps(vlt: str) -> str:
    """
    Convert a VLT string to Perso-Arabic.
    """
    return vlt.translate(str.maketrans({v: k for k, v in PA_TO_VLT.items()}))


def diacritic_strip_sql_args() -> tuple[str, str]:
    """
    Returns (from_chars, to_chars) for Postgres translate(field, from, to),
    for use in a GeneratedField expression.

    Note: translate() is strictly single-character-to-single-character,
    so this only works because every value in DIACRITIC_STRIP_MAP is
    exactly one character. If any future entry needs a multi-character
    replacement, translate() can't express it and this helper would need
    to change to regexp_replace-based logic instead.
    """
    from_chars = "".join(DIACRITIC_STRIP_MAP.keys())
    to_chars = "".join(DIACRITIC_STRIP_MAP.values())
    return from_chars, to_chars