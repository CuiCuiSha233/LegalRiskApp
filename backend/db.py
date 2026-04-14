import os
import json
import sys
from pathlib import Path
from contextlib import contextmanager

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    ROOT_DIR = Path(os.path.dirname(sys.executable))
else:
    ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_CONFIG_FILE = ROOT_DIR / "database_config.json"

DEFAULT_DB_CONFIG = {
    "type": "mysql",
    "mysql": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "root",
        "database": "legal_risk_app",
    },
}


def load_config():
    global db_config
    if DATABASE_CONFIG_FILE.exists():
        try:
            with open(DATABASE_CONFIG_FILE, "r", encoding="utf-8") as f:
                db_config = json.load(f)
        except Exception as e:
            print(f"Error loading database config: {e}")
            db_config = DEFAULT_DB_CONFIG.copy()


db_config = DEFAULT_DB_CONFIG.copy()
load_config()

try:
    import pymysql

    pymysql.install_as_MySQLdb()
except ImportError:
    pass


def get_db_connection():
    import MySQLdb

    return MySQLdb.connect(
        host=db_config["mysql"]["host"],
        port=db_config["mysql"]["port"],
        user=db_config["mysql"]["user"],
        passwd=db_config["mysql"]["password"],
        db=db_config["mysql"]["database"],
    )


def init_db():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE,
                created_at VARCHAR(50) NOT NULL,
                last_login VARCHAR(50),
                last_activity VARCHAR(50),
                role VARCHAR(20) DEFAULT 'user',
                current_token TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                created_at VARCHAR(50) NOT NULL,
                title TEXT,
                input_content LONGTEXT,
                final_report LONGTEXT,
                expert1_report LONGTEXT,
                expert2_report LONGTEXT,
                expert3_report LONGTEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_configs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL UNIQUE,
                api_key TEXT,
                base_url TEXT,
                model TEXT,
                prompt_configs TEXT,
                created_at VARCHAR(50) NOT NULL,
                updated_at VARCHAR(50) NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        conn.commit()
    finally:
        conn.close()


@contextmanager
def get_db():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

def get_db_type():
    return db_config.get("type", "sqlite")


def execute_query(conn, sql, params=()):
    sql = sql.replace("?", "%s")
    cursor = conn.cursor()
    cursor.execute(sql, params)
    return cursor
