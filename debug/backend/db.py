import os
import json
import sys
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime

# 从运行根目录读取数据库配置
# 兼容PyInstaller打包的exe和普通Python脚本
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # 打包成exe后，database_config.json应该在exe文件所在目录
    ROOT_DIR = Path(os.path.dirname(sys.executable))
else:
    # 普通Python脚本，从文件路径计算
    ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_CONFIG_FILE = ROOT_DIR / "database_config.json"

# 默认数据库配置
DEFAULT_DB_CONFIG = {
    "type": "mysql",  # 只使用mysql
    "mysql": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "root",
        "database": "legal_risk_app"
    }
}

# 加载配置
def load_config():
    """从运行根目录的database_config.json文件加载配置"""
    global db_config
    if DATABASE_CONFIG_FILE.exists():
        try:
            with open(DATABASE_CONFIG_FILE, "r", encoding="utf-8") as f:
                db_config = json.load(f)
        except Exception as e:
            print(f"Error loading database config: {e}")
            # 如果加载失败，使用默认配置
            db_config = DEFAULT_DB_CONFIG.copy()

# 保存配置 - 不再需要，配置由管理员手动编辑
def save_config():
    """保存配置到文件"""
    pass

# 初始化配置
db_config = DEFAULT_DB_CONFIG.copy()
load_config()

# 尝试导入 pymysql
mysql_available = False
try:
    import pymysql
    mysql_available = True
    pymysql.install_as_MySQLdb()
except ImportError:
    pass


def get_db_connection():
    """获取数据库连接"""
    import MySQLdb
    return MySQLdb.connect(
        host=db_config["mysql"]["host"],
        port=db_config["mysql"]["port"],
        user=db_config["mysql"]["user"],
        passwd=db_config["mysql"]["password"],
        db=db_config["mysql"]["database"]
    )


def init_db():
    """初始化数据库"""
    conn = get_db_connection()
    try:
        # MySQL 语法 - 需要使用 cursor
        cursor = conn.cursor()
        # 创建 users 表
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
        # 创建 reports 表，添加 user_id 字段
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
        # 创建 user_configs 表
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
    """数据库连接上下文管理器"""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


def set_db_config(config):
    """设置数据库配置 - 仅在内存中临时使用，不保存"""
    global db_config
    db_config.update(config)
    # 不再保存配置，配置由管理员手动编辑


def get_db_config():
    """获取数据库配置"""
    return db_config


def get_db_type():
    """获取当前数据库类型"""
    return db_config.get("type", "sqlite")


def execute_query(conn, sql, params=()):
    """
    执行 SQL 查询，自动处理占位符
    """
    # 只使用 MySQL
    # MySQL 使用 %s 占位符
    sql = sql.replace("?", "%s")
    # MySQL 需要使用 cursor
    cursor = conn.cursor()
    cursor.execute(sql, params)
    return cursor


def test_db_connection():
    """测试数据库连接"""
    try:
        conn = get_db_connection()
        conn.close()
        return True, "连接成功"
    except Exception as e:
        return False, str(e)
