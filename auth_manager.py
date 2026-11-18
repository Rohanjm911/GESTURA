import sqlite3
import bcrypt
from datetime import datetime

DB_NAME = "users.db"
GROUP_INVITE_CODE = "FYP2026"

class AuthManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, timeout=10.0, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash BLOB NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                login_time TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def register_user(self, username: str, password: str, invite_code: str) -> tuple[bool, str]:
        if not username or not password or not invite_code:
            return False, "All fields are required."
        if invite_code.strip() != GROUP_INVITE_CODE:
            return False, "Invalid Group Invite Code. Access Denied."
        if len(username.strip()) < 3 or len(password) < 6:
            return False, "Username must be 3+ chars and password 6+ chars."

        try:
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
                (username.strip(), hashed, "Group Member", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            self.conn.commit()
            return True, "Account created! You can now log in."
        except sqlite3.IntegrityError:
            return False, "Username already exists."
        except Exception as e:
            return False, f"Registration error: {str(e)}"

    def verify_login(self, username: str, password: str) -> tuple[bool, str]:
        if not username or not password:
            return False, "Username and password required."
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username.strip(),))
            row = cursor.fetchone()
            if row:
                stored_hash = row[0]
                hash_bytes = stored_hash if isinstance(stored_hash, bytes) else str(stored_hash).encode("utf-8")
                if bcrypt.checkpw(password.encode("utf-8"), hash_bytes):
                    cursor.execute(
                        "INSERT INTO access_logs (username, login_time) VALUES (?, ?)",
                        (username.strip(), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    )
                    self.conn.commit()
                    return True, "Authentication Successful"
        except Exception:
            pass
        return False, "Invalid username or password."

    def get_recent_logs(self, limit=15):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT username, login_time FROM access_logs ORDER BY id DESC LIMIT ?", (limit,))
            return cursor.fetchall()
        except Exception:
            return []

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass
