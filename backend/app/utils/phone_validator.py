import re

INDIAN_PHONE_REGEX = re.compile(r"^(\+91)?[6-9]\d{9}$")


def validate_indian_phone(phone: str) -> bool:
    cleaned = phone.strip().replace(" ", "").replace("-", "")
    return bool(INDIAN_PHONE_REGEX.match(cleaned))


def normalize_phone(phone: str) -> str:
    cleaned = phone.strip().replace(" ", "").replace("-", "")
    if cleaned.startswith("+91"):
        return cleaned
    if cleaned.startswith("91") and len(cleaned) == 12:
        return f"+{cleaned}"
    if len(cleaned) == 10:
        return f"+91{cleaned}"
    return cleaned
