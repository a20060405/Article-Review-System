import getpass
from pwdlib import PasswordHash
from db import get_connection

password_hash = PasswordHash.recommended()

conn = get_connection()

try:
    with conn.cursor() as cur:
        for username, role in [
            ("author1", "author"),
            ("editor1", "editor")
        ]:
            password = getpass.getpass(
                f"請設定 {username} 的密碼："
            )

            hashed = password_hash.hash(password)

            cur.execute(
                """
                INSERT INTO users (username, password_hash, role)
                VALUES (%s, %s, %s)
                ON CONFLICT (username)
                DO NOTHING
                """,
                (username, hashed, role)
            )

            if cur.rowcount == 1:
                print(f"✅ {username} 建立成功")
            else:
                print(f"ℹ️ {username} 已存在，未修改")

    conn.commit()

except Exception:
    conn.rollback()
    raise

finally:
    conn.close()