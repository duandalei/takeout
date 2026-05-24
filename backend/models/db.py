import pyodbc
from config import DB_CONFIG


def get_connection():
    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"Trusted_Connection={DB_CONFIG['trusted_connection']};"
    )
    return pyodbc.connect(conn_str)


def query(sql, params=None):
    """执行查询，返回字典列表"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        columns = [col[0] for col in cursor.description] if cursor.description else []
        rows = []
        for row in cursor.fetchall():
            rows.append(dict(zip(columns, row)))
        return rows


def execute(sql, params=None):
    """执行写操作，返回最后插入的ID"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        conn.commit()
        # 获取自增ID
        try:
            cursor.execute("SELECT @@IDENTITY AS id")
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception:
            return None


def execute_many(sql, params_list):
    """批量执行"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany(sql, params_list)
        conn.commit()
