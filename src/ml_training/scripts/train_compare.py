import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import os
import glob # Thư viện để tìm kiếm file

def load_data():
    # Lấy đường dẫn tuyệt đối của thư mục chứa script này
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Trỏ vào thư mục datasets/raw
    raw_dir = os.path.join(script_dir, "../datasets/raw")
    
    # Tìm tất cả file .csv trong thư mục đó
    all_files = glob.glob(os.path.join(raw_dir, "*.csv"))
    
    if not all_files:
        print(f"No CSV files found in {raw_dir}. Using dummy data.")
        data = [
            ("SELECT * FROM users WHERE id = 1", 1),
            ("admin' --", 1),
            ("hello world", 0)
        ]
        return pd.DataFrame(data, columns=['payload', 'label'])

    print(f"Found {len(all_files)} files: {[os.path.basename(f) for f in all_files]}")
    
    df_list = []
    for filename in all_files:
        try:
            df = pd.read_csv(filename)
            # Chuẩn hóa tên cột (đề phòng file khác nhau)
            df.columns = [c.lower() for c in df.columns] 
            
            if 'payload' in df.columns and 'label' in df.columns:
                df_list.append(df)
            else:
                print(f"Skipping {filename}: Missing columns payload/label")
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    if not df_list:
        return None

    # Gộp tất cả lại thành 1 DataFrame lớn
    full_df = pd.concat(df_list, axis=0, ignore_index=True)
    
    # Đảm bảo kiểu dữ liệu sạch sẽ
    full_df = full_df.dropna(subset=['payload', 'label'])
    full_df['label'] = full_df['label'].astype(int)
    full_df['payload'] = full_df['payload'].astype(str)
    
    print(f"Total loaded rows: {len(full_df)}")
    return full_df

def train():
    df = load_data()
    if df is None or df.empty:
        print("No data to train.")
        return

    X = df['payload']
    y = df['label']

    # Chia tập train/test (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # --- CẤU HÌNH PIPELINE MỚI ---
    pipeline = Pipeline([
        # TfidfVectorizer: 
        # ngram_range=(1, 2) -> Học cả từ đơn ("UNION") và cụm từ ("UNION SELECT")
        ('tfidf', TfidfVectorizer(min_df=1, stop_words=None, ngram_range=(1, 2))),
        
        # LogisticRegression:
        # C=10.0 -> Giảm regularization để model fit chặt hơn với dữ liệu lớn
        # max_iter=1000 -> Đảm bảo model chạy đủ lâu để hội tụ
        ('clf', LogisticRegression(C=10.0, max_iter=1000))
    ])

    print("Training model...")
    pipeline.fit(X_train, y_train)

    # Đánh giá
    preds = pipeline.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Accuracy: {acc}")
    print("\nDetailed Report:")
    print(classification_report(y_test, preds))

    # --- XỬ LÝ LƯU FILE (Logic Docker/Local thông minh) ---
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Đường dẫn Docker
    docker_path = os.path.abspath(os.path.join(script_dir, "../../detection_api/models"))
    # Đường dẫn Local
    local_path = os.path.abspath(os.path.join(script_dir, "../../src/detection_api/models"))

    if os.path.exists(os.path.join(script_dir, "../../detection_api")):
        output_dir = docker_path
        print("Environment: Docker/Production structure")
    else:
        output_dir = local_path
        print("Environment: Local/Development structure")

    try:
        os.makedirs(output_dir, exist_ok=True)
        model_path = os.path.join(output_dir, "sqli_model.pkl")
        
        joblib.dump(pipeline, model_path)
        print(f"SUCCESS: Model saved to {model_path}")
    except Exception as e:
        print(f"CRITICAL ERROR: Could not save model to {output_dir}. Error: {e}")

if __name__ == "__main__":
    train()