import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

if __name__ == "__main__":
    try:
        conn = get_connection()
        print("✅ PostgreSQL 資料庫連線成功！")
        conn.close()
    except Exception as e:
        print("❌ 資料庫連線失敗：", e)