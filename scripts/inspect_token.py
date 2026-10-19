"""Decode a JWT and show its claims (debugging only - does NOT verify the signature).

Run from the project root:  python -m scripts.inspect_token
"""
import json
import time
from datetime import datetime

from jose import jwt


def main() -> None:
    token = input("token: ").strip()
    if token.lower().startswith("bearer "):
        print("Note: removed a leading 'Bearer ' - in Swagger's Authorize box paste only the token.")
        token = token[7:].strip()

    try:
        claims = jwt.get_unverified_claims(token)
    except Exception as err:  # malformed token
        print(f"Not a valid JWT: {err}")
        return

    print(json.dumps(claims, indent=2))

    if claims.get("token_type") != "access":
        print(f"-> token_type is {claims.get('token_type')!r}: protected routes need an ACCESS token.")
    if "email" not in claims:
        print("-> no 'email' claim: get_current_account will reject it (refreshed-token bug).")

    exp = claims.get("exp")
    if exp is not None:
        left = int(exp - time.time())
        when = datetime.fromtimestamp(exp).strftime("%H:%M:%S")
        print(f"-> expired at {when}" if left < 0 else f"-> valid until {when} ({left}s left)")


if __name__ == "__main__":
    main()
