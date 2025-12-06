# Sử dụng Python 3.10 để tương thích tốt
FROM python:3.13-slim

WORKDIR /app

# 1. Cài đặt các thư viện cần thiết (Gộp cả API và Training)
COPY src/detection_api/requirements.txt .
COPY src/ml_training/requirements.txt ./requirements_train.txt
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements_train.txt

# 2. Copy toàn bộ code (Cả API và Training)
COPY src/detection_api/ ./detection_api/
COPY src/ml_training/ ./ml_training/

# 3. Tạo thư mục models (nếu chưa có)
RUN mkdir -p ./detection_api/models

# 4. CHẠY TRAINING NGAY LÚC BUILD
# Lưu ý: Chúng ta cần chỉnh lại đường dẫn output trong code training hoặc dùng biến môi trường, 
# nhưng ở đây ta sẽ dùng lệnh cd để chạy đúng ngữ cảnh.
WORKDIR /app/ml_training/scripts
RUN python train_compare.py

# 5. Quay lại thư mục gốc để chạy API
WORKDIR /app/detection_api

# Expose port
EXPOSE 8000

# Run app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]