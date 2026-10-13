import os
import json
import librosa
import numpy as np
import mysql.connector

# Cấu hình kết nối MySQL
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "nxh05092005", # Mật khẩu của bạn
    "database": "animal_sound_db"
}

def extract_and_save_features():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    dataset_dir = "dataset/File_Âm_Thanh"
    
    if not os.path.exists(dataset_dir):
        print(f"Không tìm thấy thư mục {dataset_dir}. Hãy kiểm tra lại cấu trúc thư mục!")
        return

    count = 0
    # os.walk giúp duyệt qua tất cả các thư mục con (Cat_100, Dog_100,...)
    for root, dirs, files in os.walk(dataset_dir):
        for file_name in files:
            if file_name.lower().endswith('.wav'):
                file_path = os.path.join(root, file_name)
                # Lấy tên loài từ tên thư mục chứa file
                animal_name = os.path.basename(root)
                
                try:
                    # 1. Đọc file âm thanh
                    y, sr = librosa.load(file_path, sr=22050)
                    duration = librosa.get_duration(y=y, sr=sr)
                    
                    # 2. Trích xuất đặc trưng MFCC (13 hệ số, lấy trung bình cột)
                    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                    feature_vector = np.mean(mfccs, axis=1).tolist()
                    
                    # 3. Lưu vào MySQL
                    sql = """
                        INSERT INTO animal_sounds (filename, animal_name, duration, sample_rate, feature_vector)
                        VALUES (%s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                        animal_name=VALUES(animal_name), duration=VALUES(duration), feature_vector=VALUES(feature_vector)
                    """
                    cursor.execute(sql, (file_path, animal_name, float(duration), int(sr), json.dumps(feature_vector)))
                    conn.commit()
                    count += 1
                    print(f"[{count}] Đã lưu thành công: {animal_name}/{file_name}")
                    
                except Exception as e:
                    print(f"Lỗi khi xử lý file {file_path}: {e}")
                        
    cursor.close()
    conn.close()
    print(f"Hoàn thành! Đã trích xuất và lưu tổng cộng {count} file vào cơ sở dữ liệu.")

if __name__ == "__main__":
    extract_and_save_features()