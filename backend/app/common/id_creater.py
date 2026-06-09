"""
"""

import secrets
import string


ALPHABET = string.ascii_uppercase + string.digits

def generate_id(length = 6):
    return "".join(secrets.choice(ALPHABET) for _ in range(length))

