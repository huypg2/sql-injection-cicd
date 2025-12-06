import requests
import sys
import time

# Cấu hình
API_URL = "http://localhost:8000/predict"
THRESHOLD = 1.0  # Phải chặn được 100% tấn công mới cho qua (Security Gate)

# Bộ test giả lập (Smoke Test)
# Gồm: [Payload, Nhãn mong muốn (True=SQLi, False=An toàn)]
test_cases = [
    # --- Case 1: Tấn công rõ ràng (AI PHẢI BẮT ĐƯỢC) ---
    ("UNION SELECT user, password FROM users", True),
    ("admin' OR 1=1 --", True),
    ("1; DROP TABLE users", True),
    ("UN/**/ION SEL/**/ECT", True),
    
    # --- Case 2: Câu bình thường (AI KHÔNG ĐƯỢC BẮT NHẦM) ---
    ("Hello world", False),
    ("user@example.com", False),
    ("Select a fruit from the basket", False),
]

def run_security_gate():
    print("🔒 STARTING SECURITY GATE CHECK...")
    print(f"Target: {API_URL}")
    
    # Chờ API khởi động (nếu chạy trong CI)
    for _ in range(5):
        try:
            requests.get("http://localhost:8000/health")
            break
        except:
            print("Waiting for API...")
            time.sleep(2)

    passed = 0
    failed = 0
    
    for payload, expected_is_sqli in test_cases:
        try:
            # Gửi payload vào AI
            response = requests.post(API_URL, json={"query": payload})
            result = response.json()
            
            ai_prediction = result.get("is_sqli")
            confidence = result.get("confidence")
            
            # Kiểm tra xem AI đoán có đúng ý đồ không
            if ai_prediction == expected_is_sqli:
                print(f"✅ PASS: '{payload}' -> AI: {ai_prediction} ({confidence:.2f})")
                passed += 1
            else:
                print(f"❌ FAIL: '{payload}' -> Expected: {expected_is_sqli}, Got: {ai_prediction}")
                failed += 1
                
        except Exception as e:
            print(f"⚠️ ERROR connection: {e}")
            failed += 1

    total = passed + failed
    print("-" * 30)
    print(f"📊 SUMMARY: {passed}/{total} passed.")

    # Logic chặn Pipeline (Security Gate)
    # Nếu có bất kỳ test case nào sai -> HỦY DEPLOY
    if failed > 0:
        print("🚨 SECURITY GATE FAILED! Deploy blocked.")
        print("Reason: AI model failed to detect known attacks or blocked valid users.")
        sys.exit(1) # Trả về exit code 1 để GitHub Actions biết là lỗi
    else:
        print("🚀 SECURITY GATE PASSED. Ready for deployment.")
        sys.exit(0)

if __name__ == "__main__":
    run_security_gate()