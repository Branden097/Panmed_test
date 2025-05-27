FROM python:3.8-slim

# 安裝必要套件
RUN apt-get update && \
    apt-get install -y unzip libaio1 && \
    rm -rf /var/lib/apt/lists/*

# 建立非 root 使用者
RUN useradd -m appuser

# 複製檔案（用 root 複製 OK）
COPY instantclient-basic-linux.x64-11.2.0.4.0.zip /opt/oracle/
RUN unzip /opt/oracle/instantclient-basic-linux.x64-11.2.0.4.0.zip -d /opt/oracle/ && \
    rm /opt/oracle/instantclient-basic-linux.x64-11.2.0.4.0.zip

# 設定 Oracle 環境變數
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_11_2:$LD_LIBRARY_PATH

# 設定工作目錄並給予權限
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# 將權限給 appuser（必要時）
RUN chown -R appuser:appuser /app

# 切換為非 root 使用者
USER appuser

# 設定啟動指令
CMD ["python", "app.py"]
