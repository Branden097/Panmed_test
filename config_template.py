# config.py
import os

# 資料庫連接參數
ORACLE_DSN = {
    "host": "localhost",
    "port": "1521",
    "sid": "xe"
}
ORACLE_USERNAME = "ACCOUTN"
ORACLE_PASSWORD = "PWD"

# Logging 設定
LOGGING_CONFIG = {
    "filename": "app.log",
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s"
}

# Gmail 帳號和應用程式密碼
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")

if not GMAIL_USER or not GMAIL_PASSWORD:
    raise ValueError("請設定 GMAIL_USER 與 GMAIL_PASSWORD 的環境變數")
