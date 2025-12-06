from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import joblib
import os
import traceback  # <--- THÊM: Thư viện này giúp in ra toàn bộ dấu vết lỗi
from config import Config
from utils.logger import logger

router = APIRouter()

# Biến toàn cục lưu model
model = None

# Hàm load model (được gọi khi khởi động hoặc khi cần thiết)
def load_model_logic():
    global model
    try:
        # Kiểm tra file có tồn tại không
        if not os.path.exists(Config.MODEL_PATH):
            msg = f"FAILED: File not found at {Config.MODEL_PATH}"
            logger.warning(msg)
            return False, msg

        # Thử load model
        model = joblib.load(Config.MODEL_PATH)
        logger.info(f"SUCCESS: Model loaded from {Config.MODEL_PATH}")
        return True, "Loaded successfully"

    except Exception:
        # <--- SỬA ĐOẠN NÀY: Dùng traceback để bắt lỗi ẩn --->
        # Lấy toàn bộ nội dung lỗi (Stack Trace) thay vì chỉ lấy str(e)
        full_error = traceback.format_exc()
        
        msg = f"CRITICAL ERROR loading model. Details:\n{full_error}"
        logger.error(msg)
        
        # Trả về nguyên văn lỗi để hiện ra Postman
        return False, full_error

# Thử load ngay khi import file
load_model_logic()

class PayloadRequest(BaseModel):
    query: str

@router.post("/predict")
def predict_sqli(request: PayloadRequest):
    global model
    
    # Cơ chế "Lazy Loading": Nếu model chưa có, thử load lại lần nữa
    if model is None:
        success, message = load_model_logic()
        if not success:
            # TRẢ VỀ LỖI CHI TIẾT CHO POSTMAN
            return {
                "error": "Model loading failed",
                "debug_info": message,  # Giờ biến message sẽ chứa chi tiết lỗi dài
                "current_path": os.getcwd(),
                "model_path_env": Config.MODEL_PATH
            }
    
    # Nếu load được rồi thì dự đoán
    try:
        prediction = model.predict([request.query])[0]
        probability = model.predict_proba([request.query]).max()
        is_malicious = bool(prediction == 1)
        
        return {
            "payload": request.query,
            "is_sqli": is_malicious,
            "confidence": float(probability)
        }
    except Exception as e:
        # Bắt lỗi khi dự đoán (ví dụ dữ liệu đầu vào sai)
        error_trace = traceback.format_exc()
        return {
            "error": "Prediction failed",
            "details": str(e),
            "trace": error_trace
        }