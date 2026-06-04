"""Flask 配置"""

import os


class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'takeout-secret-key-2025')

    # SQL Server 连接 — Windows 身份验证
    DB_SERVER = os.environ.get('DB_SERVER', '.')
    DB_NAME   = os.environ.get('DB_NAME',   'TakeoutDB')

    # pyodbc 连接串 (Windows 身份验证 + ODBC Driver 17)
    SQLALCHEMY_DATABASE_URI = (
        'mssql+pyodbc://'
        f'{DB_SERVER}/{DB_NAME}'
        '?driver=ODBC+Driver+17+for+SQL+Server'
        '&trusted_connection=yes'
        '&TrustServerCertificate=yes'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
