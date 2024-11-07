# 使用 Python 3.8 slim 基礎映像
FROM python:3.8-slim

# 安裝必要的系統套件
RUN apt-get update && \
    apt-get install -y unzip libaio1 && \
    rm -rf /var/lib/apt/lists/*

# 複製 Oracle Instant Client zip 文件到容器中
COPY instantclient-basic-linux.x64-11.2.0.4.0.zip /opt/oracle/

# 下載並安裝 Oracle Instant Client
RUN unzip /opt/oracle/instantclient-basic-linux.x64-11.2.0.4.0.zip -d /opt/oracle/ && \
    rm /opt/oracle/instantclient-basic-linux.x64-11.2.0.4.0.zip

# 設置 Oracle Instant Client 的路徑
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_11_2:$LD_LIBRARY_PATH

# 設置工作目錄
WORKDIR /app

# 複製需求檔案並安裝 Python 套件
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案檔案到容器中
COPY . .

# 設置容器啟動時執行的指令
CMD ["python", "app.py"]

