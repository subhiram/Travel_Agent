import re
import phonenumbers
from phonenumbers import NumberParseException

def is_valid_name(name):
    """
    Validates that the name contains only letters, spaces, or hyphens.
    """
    if not isinstance(name, str):
        return False
    name = name.strip()
    return bool(re.fullmatch(r"[A-Za-z\s\-]+", name))

def is_valid_email(email):
    """
    Validates email format.
    """
    if not isinstance(email, str):
        return False
    email = email.strip()
    return bool(re.fullmatch(r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+", email))

def is_valid_phone(phone):
    """
    Validates international phone numbers using the `phonenumbers` library.
    Accepts all valid formats with or without country code.
    """
    try:
        parsed = phonenumbers.parse(phone, None)  # None means no default country
        return phonenumbers.is_valid_number(parsed)
    except NumberParseException:
        return False
