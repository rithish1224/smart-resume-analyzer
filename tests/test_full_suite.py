import urllib.request
import json
import random
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(name, url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    if data and isinstance(data, dict):
        data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8")
            status = resp.status
            print(f"[PASS] [{method}] {name} ({status})")
            return status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        print(f"[FAIL] [{method}] {name} ({e.code}) -> {body[:100]}")
        return e.code, body
    except Exception as e:
        print(f"[ERROR] [{method}] {name} -> {e}")
        return 500, str(e)

def main():
    print("==================================================")
    print("RUNNING FULL END-TO-END APPLICATION AUDIT SUITE")
    print("==================================================")

    # 1. Health Endpoint
    test_endpoint("Health Check", f"{BASE_URL}/health")

    # 2. Frontend HTML Routes (SPA Catch-all)
    test_endpoint("Root Page (/)", f"{BASE_URL}/")
    test_endpoint("Analyze Page (/analyze)", f"{BASE_URL}/analyze")
    test_endpoint("Compare Page (/compare)", f"{BASE_URL}/compare")
    test_endpoint("About Page (/about)", f"{BASE_URL}/about")
    test_endpoint("Login Page (/login)", f"{BASE_URL}/login")

    # 3. Static Assets
    test_endpoint("Static Assets (index.html)", f"{BASE_URL}/index.html")

    # 4. OpenAPI & Docs
    test_endpoint("Swagger UI (/api/docs)", f"{BASE_URL}/api/docs")
    test_endpoint("OpenAPI Schema (/api/openapi.json)", f"{BASE_URL}/api/openapi.json")

    # 5. Auth API: Register & Login (Candidate)
    cand_email = f"cand_{random.randint(10000,99999)}@example.com"
    status, reg_body = test_endpoint("Register Candidate", f"{BASE_URL}/api/auth/register", method="POST", data={
        "email": cand_email,
        "password": "Password123!",
        "full_name": "Test Candidate",
        "role": "candidate"
    })

    status, login_body = test_endpoint("Login Candidate", f"{BASE_URL}/api/auth/login", method="POST", data={
        "email": cand_email,
        "password": "Password123!"
    })

    # 6. Auth API: Register & Login (Recruiter)
    rec_email = f"rec_{random.randint(10000,99999)}@example.com"
    test_endpoint("Register Recruiter", f"{BASE_URL}/api/auth/register", method="POST", data={
        "email": rec_email,
        "password": "Password123!",
        "full_name": "Test Recruiter",
        "role": "recruiter"
    })

    # 7. Roadmap Provider Status
    test_endpoint("AI Provider Status", f"{BASE_URL}/api/roadmap/provider-status")

    # 8. Score Endpoint
    test_endpoint("Get Scores List", f"{BASE_URL}/api/score")

    # 9. Comparison Endpoint
    test_endpoint("Compare Candidates API", f"{BASE_URL}/api/compare", method="POST", data={
        "ids": ["cand1", "cand2"]
    })

    print("==================================================")
    print("AUDIT SUITE COMPLETE")
    print("==================================================")

if __name__ == "__main__":
    main()
