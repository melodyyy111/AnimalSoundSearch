import mysql.connector

# Cấu hình kết nối trực tiếp
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "nxh05092005",
    "database": "animal_sound_db"
}

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    print("Ket noi MySQL thanh cong!")
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    print("Danh sach bang:", cursor.fetchall())
    cursor.close()
    conn.close()
except mysql.connector.Error as e:
    print("Loi:", e)