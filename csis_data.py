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

def get_valueDesc(protocolid, patientid, datapointid):
    # 連接 Oracle 資料庫
    connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
    try:
        cursor = connection.cursor()
        query = """
            SELECT et.DESCRIPTION
            FROM PROTOCOL_PATIENT pp, visit v, datarecord dr, DATAPOINTDATARECORD dpdr
            ,datapoint dp , CSISMETA_TRA.MEASUREMENTUNIT mu, CSISMETA_TRA.ENUMTYPE et
            WHERE pp.PATIENTID = :patientid
            AND pp.PROTOCOLID = :protocolid
            AND pp.id = v.PCLPATIENTID
            AND dr.EVENTID = v.EVENTID
            AND dpdr.DATARECORDID = dr.id
            AND dpdr.DATAPOINTID = :datapointid
            And dp.id = dpdr.DATAPOINTID
            And dp.MEASUNITID = mu.id
            And mu.id = et.MEASUNITID
            And et.VALUE = dpdr.value
        """
        cursor.execute(query, patientid=patientid, protocolid=protocolid, datapointid=datapointid)
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        cursor.close()
        connection.close()

def get_datarecord_id(protocolid, patientid, datapointid):
    """查詢特定的 datarecord_id"""
    connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
    try:
        cursor = connection.cursor()
        query = """
            SELECT dr.id
            FROM PROTOCOL_PATIENT pp, visit v, datarecord dr
            WHERE pp.PATIENTID = :patientid
            AND pp.PROTOCOLID = :protocolid
            AND pp.id = v.PCLPATIENTID
            AND dr.EVENTID = v.EVENTID
            AND EXISTS (
                SELECT 1
                FROM DATAPOINTDATARECORD dpdr
                WHERE dpdr.DATARECORDID = dr.id
                AND dpdr.DATAPOINTID = :datapointid
            )
        """
        cursor.execute(query, patientid=patientid, protocolid=protocolid, datapointid=datapointid)
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        cursor.close()
        connection.close()

def get_mrn(patientid):
    connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
    try:
        cursor = connection.cursor()
        query = """
            select MRN from patient where patientid = :patientid
        """
        cursor.execute(query, patientid=patientid)
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        cursor.close()
        connection.close()

def add_dpdr(datapointid, datarecordid, value, lastupdid):
    """插入新的紀錄到 datapointdatarecord 表中"""
    connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO datapointdatarecord (DATAPOINTID, DATARECORDID, VALUE, LASTUPDID, CREATORID)
            VALUES (:datapointid, :datarecordid, :value, :lastupdid, :creatorid)
        """
        cursor.execute(query, datapointid=datapointid, datarecordid=datarecordid,
                       value=value, lastupdid=lastupdid, creatorid=lastupdid)
        connection.commit()  # 提交更改
        print("記錄已成功插入。")
    except cx_Oracle.DatabaseError as e:
        print(f"插入失敗：{e}")
        connection.rollback()  # 回滾更改
    finally:
        cursor.close()
        connection.close()