from db import get_connection

conn = get_connection()

try:
    with conn.cursor() as cur:
        users = [
            ("author1", "author"),
            ("editor1", "editor")
        ]

        for username, role in users:
            cur.execute("""
                INSERT INTO users (username, role)
                VALUES (%s, %s)
                ON CONFLICT (username) DO NOTHING
            """, (username, role))

            print(f"✅ 帳號 {username} 已建立或已存在")

    conn.commit()
    print("✅ 測試帳號設定完成！")

except Exception as e:
    conn.rollback()
    print("❌ 發生錯誤：", e)

finally:
    conn.close()