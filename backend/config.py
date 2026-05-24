# 数据库配置 — SQL Server Windows 认证
DB_CONFIG = {
    "driver": "{ODBC Driver 17 for SQL Server}",
    "server": "localhost",
    "database": "TakeoutDB",
    "trusted_connection": "yes",
}

SECRET_KEY = "takeout-secret-key-2024"
TOKEN_EXPIRE_HOURS = 24
