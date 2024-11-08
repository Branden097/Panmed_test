# config.py

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
GMAIL_USER = 'example@gmail.com'
GMAIL_PASSWORD = 'token'
