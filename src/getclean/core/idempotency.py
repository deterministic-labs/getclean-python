# Part of the generated SDK of the getclean API; do not edit.

import uuid


def generate_idempotency_key() -> str:
    return str(uuid.uuid4())
