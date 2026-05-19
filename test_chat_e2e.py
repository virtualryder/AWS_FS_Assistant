"""
End-to-end chat test against the deployed Railway API.

Usage:
    python test_chat_e2e.py https://your-api.up.railway.app

Tests:
    1. Health check
    2. Create a test customer
    3. Create a conversation
    4. Send a chat message and verify SSE stream
    5. Verify response persisted as messages
    6. Clean up (delete test customer)
"""

import json
import sys
import time
import urllib.request
import urllib.error

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"
PASS = "\033[92m✅\033[0m"
FAIL = "\033[91m❌\033[0m"
INFO = "\033[94m→\033[0m"

def req(method, path, body=None, headers=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    h = {"Content-Type": "application/json", **(headers or {})}
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        return e.code, {}

def test_health():
    print(f"\n{INFO} 1. Health check...")
    status, body = req("GET", "/health")
    if status == 200 and body.get("status") == "ok":
        print(f"   {PASS} /health → {body}")
        return True
    print(f"   {FAIL} /health returned {status}: {body}")
    return False

def test_create_customer():
    print(f"\n{INFO} 2. Create test customer...")
    status, body = req("POST", "/api/customers", {
        "name": "E2E Test Bank",
        "industry": "Bank",
        "arch_context": "OCC-regulated community bank, $2B assets, needs PCI DSS and GLBA coverage",
        "stage": "Active Opportunity",
    })
    if status in (200, 201) and body.get("id"):
        print(f"   {PASS} Created customer: {body['name']} (id={body['id'][:8]}...)")
        return body["id"]
    print(f"   {FAIL} Create customer returned {status}: {body}")
    return None

def test_create_conversation(customer_id):
    print(f"\n{INFO} 3. Create conversation...")
    status, body = req("POST", f"/api/customers/{customer_id}/conversations")
    if status in (200, 201) and body.get("id"):
        print(f"   {PASS} Created conversation: {body['id'][:8]}...")
        return body["id"]
    print(f"   {FAIL} Create conversation returned {status}: {body}")
    return None

def test_chat_stream(conv_id):
    print(f"\n{INFO} 4. Send chat message (SSE stream)...")
    print(f"   Question: 'What AWS architecture do you recommend for a payment processing system at a community bank?'")

    url = f"{BASE}/api/conversations/{conv_id}/chat"
    payload = json.dumps({
        "user_message": "What AWS architecture do you recommend for a payment processing system at a community bank that needs PCI DSS v4.0.1 compliance?",
        "customer_context": "OCC-regulated community bank, $2B assets",
    }).encode()

    r = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }, method="POST")

    status_messages = []
    token_count = 0
    full_response = ""
    start = time.time()

    try:
        with urllib.request.urlopen(r, timeout=300) as resp:
            print(f"   {PASS} SSE stream connected (HTTP {resp.status})")
            for line in resp:
                line = line.decode("utf-8").strip()
                if not line.startswith("data:"):
                    continue
                try:
                    event = json.loads(line[5:].strip())
                except json.JSONDecodeError:
                    continue

                etype = event.get("type")
                text = event.get("text", "")

                if etype == "status":
                    status_messages.append(text)
                    print(f"   {INFO} [{round(time.time()-start)}s] STATUS: {text[:80]}")
                elif etype == "token":
                    token_count += 1
                    if token_count == 1:
                        print(f"   {PASS} First token received at {round(time.time()-start)}s")
                elif etype == "done":
                    full_response = text
                    elapsed = round(time.time() - start)
                    print(f"   {PASS} Done event received ({elapsed}s, {len(full_response):,} chars)")
                    break
                elif etype == "error":
                    print(f"   {FAIL} Error event: {text}")
                    return None, []

    except Exception as e:
        print(f"   {FAIL} Stream failed: {e}")
        return None, []

    # Spot-check the response
    checks = [
        ("contains architecture diagram", "→" in full_response or "[" in full_response),
        ("mentions PCI DSS", "PCI" in full_response),
        ("mentions compliance", any(w in full_response for w in ["GLBA", "compliance", "regulation", "SOX", "FFIEC"])),
        ("has AWS services", any(s in full_response for s in ["RDS", "KMS", "VPC", "IAM", "CloudTrail", "GuardDuty"])),
        ("substantial response (>500 chars)", len(full_response) > 500),
    ]

    print(f"\n   Response quality checks:")
    all_pass = True
    for label, result in checks:
        icon = PASS if result else FAIL
        print(f"   {icon} {label}")
        if not result:
            all_pass = False

    print(f"\n   Status messages seen: {len(status_messages)}")
    print(f"   Response preview:\n   {full_response[:300]}...")

    return full_response, status_messages

def test_messages_persisted(conv_id):
    print(f"\n{INFO} 5. Verify messages persisted...")
    time.sleep(2)  # brief wait for DB write
    status, body = req("GET", f"/api/conversations/{conv_id}/messages")
    if status == 200 and len(body) >= 2:
        roles = [m["role"] for m in body]
        print(f"   {PASS} {len(body)} messages stored: {roles}")
        return True
    print(f"   {FAIL} Messages check returned {status}: {len(body) if isinstance(body, list) else body}")
    return False

def test_cleanup(customer_id):
    print(f"\n{INFO} 6. Cleanup test customer...")
    status, _ = req("DELETE", f"/api/customers/{customer_id}")
    if status in (200, 204):
        print(f"   {PASS} Test customer deleted")
    else:
        print(f"   {FAIL} Cleanup returned {status} (non-critical)")

def main():
    print(f"\n{'='*60}")
    print(f"  AWS FinServ Assistant — End-to-End Chat Test")
    print(f"  Target: {BASE}")
    print(f"{'='*60}")

    results = {}

    results["health"] = test_health()
    if not results["health"]:
        print(f"\n{FAIL} API not reachable. Aborting.")
        sys.exit(1)

    customer_id = test_create_customer()
    results["create_customer"] = bool(customer_id)
    if not customer_id:
        sys.exit(1)

    conv_id = test_create_conversation(customer_id)
    results["create_conversation"] = bool(conv_id)
    if not conv_id:
        test_cleanup(customer_id)
        sys.exit(1)

    response, statuses = test_chat_stream(conv_id)
    results["chat_stream"] = bool(response)
    results["status_updates"] = len(statuses) > 3

    if response:
        results["messages_persisted"] = test_messages_persisted(conv_id)

    test_cleanup(customer_id)

    print(f"\n{'='*60}")
    print(f"  Results")
    print(f"{'='*60}")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    for test, result in results.items():
        icon = PASS if result else FAIL
        print(f"  {icon} {test}")
    print(f"\n  {passed}/{total} tests passed")
    print(f"{'='*60}\n")

    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
