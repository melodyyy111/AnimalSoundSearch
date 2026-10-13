import os
import json
import librosa
import numpy as np
import mysql.connector
from sklearn.metrics.pairwise import cosine_similarity

# Cấu hình kết nối MySQL (Đã điền sẵn mật khẩu của bạn)
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "nxh05092005",
    "database": "animal_sound_db"
}

def search_similar_sound(query_file_path, top_k=5):
    if not os.path.exists(query_file_path):
        print(f"Không tìm thấy file truy vấn: {query_file_path}")
        return

    print(f"Đang phân tích file truy vấn: {query_file_path}...")
    
    # 1. Trích xuất đặc trưng của file cần tìm kiếm
    try:
        y, sr = librosa.load(query_file_path, sr=22050)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        query_vector = np.mean(mfccs, axis=1).reshape(1, -1)
    except Exception as e:
        print(f"Lỗi khi đọc file âm thanh truy vấn: {e}")
        return

    # 2. Lấy toàn bộ dữ liệu vector từ MySQL
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT filename, animal_name, feature_vector FROM animal_sounds")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    if not rows:
        print("Cơ sở dữ liệu chưa có file nào!")
        return

    results = []
    
    # 3. So sánh độ tương đồng (Cosine Similarity)
    for row in rows:
        filename, animal_name, feature_json = row
        db_vector = np.array(json.loads(feature_json)).reshape(1, -1)
        
        similarity = cosine_similarity(query_vector, db_vector)[0][0]
        
        results.append({
            "filename": filename,
            "animal_name": animal_name,
            "similarity": float(similarity)
        })

    # 4. Sắp xếp kết quả giảm dần theo độ tương đồng và lấy Top K
    results = sorted(results, key=lambda x: x['similarity'], reverse=True)
    top_results = results[:top_k]

    # 5. Hiển thị kết quả
    print("\n--- TOP 5 KẾT QUẢ ÂM THANH TƯƠNG ĐỒNG NHẤT ---")
    for i, res in enumerate(top_results, 1):
        print(f"{i}. Loài: {res['animal_name']} | File: {res['filename']} | Độ tương đồng: {res['similarity']:.4f}")

if __name__ == "__main__":
    # Tự động lấy ngẫu nhiên 1 file bất kỳ đang có trong database để làm mẫu tìm kiếm thử
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT filename FROM animal_sounds LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if row:
        test_query_file = row[0]
        print(f"Đã tự động chọn file mẫu từ CSDL: {test_query_file}")
        search_similar_sound(test_query_file, top_k=5)
    else:
        print("Cơ sở dữ liệu chưa có file nào!")