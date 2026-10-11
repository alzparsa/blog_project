"""End-to-end check of the account + auth endpoints against a running server.

Start the API first (uvicorn main:app --reload), then:  python -m scripts.smoke_test_acc
Optional: python -m scripts.smoke_test_acc http://localhost   (to go through nginx)
Uses only the standard library. Creates a throwaway account and deletes it at the end.
"""
import json
import sys
import urllib.error
import urllib.request
import uuid

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000").rstrip("/")
results = []


def call(method, path, body=None, token=None, raw=None, content_type="application/json"):
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(BASE + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", content_type)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as resp:
            text = resp.read().decode()
            return resp.status, (json.loads(text) if text else None)
    except urllib.error.HTTPError as err:
        text = err.read().decode()
        try:
            return err.code, json.loads(text)
        except ValueError:
            return err.code, text


def check(name, status, expected, body=None):
    ok = status == expected
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name:55} {status} (expected {expected})")
    if not ok and body is not None:
        print("      ->", body)
    return ok


def multipart(field, filename, content, ctype):
    boundary = uuid.uuid4().hex
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"{field}\"; filename=\"{filename}\"\r\n"
        f"Content-Type: {ctype}\r\n\r\n"
    ).encode() + content + f"\r\n--{boundary}--\r\n".encode()
    return body, f"multipart/form-data; boundary={boundary}"


email = f"smoke_{uuid.uuid4().hex[:8]}@example.com"
password = "Sm0ke-test-pass"
print(f"Target: {BASE}   test account: {email}\n")

s, b = call("POST", "/auth/accounts", {"email": email, "password": password, "name": "Smoke Test"})
if not check("create account", s, 201, b):
    sys.exit("Cannot continue without an account.")
acc_id = b["id"]
s, b = call("POST", "/auth/accounts", {"email": email, "password": password, "name": "Dup"})
check("create duplicate email rejected", s, 400, b)
s, b = call("POST", "/auth/accounts", {"email": "x" + email, "password": "short", "name": "x"})
check("create with short password rejected", s, 422, b)

s, b = call("POST", "/auth/login", {"accountId": acc_id, "email": email, "password": "wrong-password"})
check("login with wrong password", s, 401, b)
s, b = call("POST", "/auth/login", {"accountId": acc_id, "email": email, "password": password})
check("login", s, 200, b)
access, refresh = b["accessToken"], b["refreshToken"]

s, b = call("GET", f"/auth/accounts/{acc_id}")
check("get account", s, 200, b)
s, b = call("GET", "/auth/accounts/999999999")
check("get missing account", s, 404, b)

s, b = call("PUT", f"/auth/accounts/{acc_id}", {"name": "Renamed"})
check("update without token", s, 403, b)  # HTTPBearer returns 403 when the header is missing
s, b = call("PUT", f"/auth/accounts/{acc_id}", {"name": "Renamed"}, token="not-a-jwt")
check("update with garbage token", s, 401, b)
s, b = call("PUT", f"/auth/accounts/{acc_id}", {"name": "Renamed"}, token=refresh)
check("update with refresh token instead of access", s, 401, b)
s, b = call("PUT", f"/auth/accounts/{acc_id + 1}", {"name": "Hacker"}, token=access)
check("update someone else's account", s, 403, b)
s, b = call("PUT", f"/auth/accounts/{acc_id}", {"name": "Renamed"}, token=access)
check("update own account", s, 200, b)

png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
body, ctype = multipart("file", "a.png", png, "image/png")
s, b = call("POST", f"/auth/accounts/{acc_id}/photo", raw=body, token=access, content_type=ctype)
check("upload profile photo", s, 200, b)
body, ctype = multipart("file", "a.png", b"not really a png", "image/png")
s, b = call("POST", f"/auth/accounts/{acc_id}/photo", raw=body, token=access, content_type=ctype)
check("upload fake image rejected", s, 400, b)

s, b = call("POST", "/auth/refresh-token", {"refreshToken": refresh})
check("refresh access token", s, 200, b)
if s == 200:
    s2, b2 = call("PUT", f"/auth/accounts/{acc_id}", {"name": "Via refreshed token"}, token=b["accessToken"])
    check("use refreshed access token", s2, 200, b2)
s, b = call("POST", "/auth/refresh-token", {"refreshToken": access})
check("refresh with an access token rejected", s, 401, b)

s, b = call("DELETE", f"/auth/accounts/{acc_id}")
check("delete without token", s, 403, b)
s, b = call("DELETE", f"/auth/accounts/{acc_id}", token=access)
check("delete own account", s, 204, b)
s, b = call("GET", f"/auth/accounts/{acc_id}")
check("account is gone", s, 404, b)

print(f"\n{sum(results)}/{len(results)} checks passed")
sys.exit(0 if all(results) else 1)
