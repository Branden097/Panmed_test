import cx_Oracle
import logging
import config  # 匯入設定檔

# 設置 logging 設定
logging.basicConfig(
    filename=config.LOGGING_CONFIG['filename'],
    level=getattr(logging, config.LOGGING_CONFIG['level']),
    format=config.LOGGING_CONFIG['format']
)

# 設定 Oracle 資料庫連接參數
dsn = cx_Oracle.makedsn(config.ORACLE_DSN["host"], config.ORACLE_DSN["port"], sid=config.ORACLE_DSN["sid"])
username = config.ORACLE_USERNAME
password = config.ORACLE_PASSWORD

def get_value(protocolid, patientid, datapointid):
    # 連接 Oracle 資料庫
    connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
    try:
        cursor = connection.cursor()
        query = """
            SELECT dpdr.value
            FROM PROTOCOL_PATIENT pp, visit v, datarecord dr, DATAPOINTDATARECORD dpdr
            WHERE pp.PATIENTID = :patientid
            AND pp.PROTOCOLID = :protocolid
            AND pp.id = v.PCLPATIENTID
            AND dr.EVENTID = v.EVENTID
            AND dpdr.DATARECORDID = dr.id
            AND dpdr.DATAPOINTID = :datapointid
        """
        cursor.execute(query, patientid=patientid, protocolid=protocolid, datapointid=datapointid)
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        cursor.close()
        connection.close()

# 其他函數保持不變，只要調用 `username`, `password` 和 `dsn` 即可
