import streamlit as st
import requests
import json

# Cấu hình API URL (Tên service trong Docker Compose là detection-api)
API_URL = "http://detection-api:8000/predict"

st.set_page_config(page_title="SQLi Detection System", page_icon="🛡️")

st.title("🛡️ Hệ thống Phát hiện Tấn công SQL Injection")
st.markdown("---")

# Khu vực nhập liệu
col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_area("Nhập câu lệnh SQL hoặc văn bản cần kiểm tra:", height=100, placeholder="Ví dụ: UNION SELECT user, password FROM users")
with col2:
    st.write("") # Spacer
    st.write("")
    analyze_btn = st.button("🔍 Phân tích", type="primary", use_container_width=True)

# Xử lý khi bấm nút
if analyze_btn and query:
    try:
        with st.spinner("Đang gửi đến AI phân tích..."):
            # Gọi API
            response = requests.post(API_URL, json={"query": query}, timeout=5)
            
        if response.status_code == 200:
            result = response.json()
            is_sqli = result.get("is_sqli", False)
            confidence = result.get("confidence", 0.0)
            
            # Hiển thị kết quả
            st.subheader("Kết quả phân tích:")
            
            if is_sqli:
                st.error(f"🚨 CẢNH BÁO: PHÁT HIỆN TẤN CÔNG SQL INJECTION!")
                st.markdown(f"**Độ tin cậy của AI:** `{confidence * 100:.2f}%`")
                # Thanh tiến trình màu đỏ
                st.progress(confidence, text="Mức độ nguy hiểm")
            else:
                st.success(f"✅ AN TOÀN: Không phát hiện tấn công.")
                st.markdown(f"**Độ tin cậy của AI:** `{confidence * 100:.2f}%`")
                # Thanh tiến trình màu xanh
                st.progress(confidence, text="Mức độ an toàn")
                
            with st.expander("Xem chi tiết JSON từ API"):
                st.json(result)
        else:
            st.error(f"Lỗi kết nối API: {response.status_code}")
            st.write(response.text)
            
    except Exception as e:
        st.error(f"Không thể kết nối đến Detection API. Hãy kiểm tra Docker.")
        st.error(f"Chi tiết lỗi: {e}")

# Footer
st.markdown("---")
