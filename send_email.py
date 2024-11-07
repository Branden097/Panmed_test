import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(to_address, cc_address, subject, body):
    # Gmail 帳號和密碼（建議使用應用程式專用密碼）
    GMAIL_USER = 'randomization@cims.tw'
    GMAIL_PASSWORD = 'mvmydflkcbncwlnn'

    # 設置郵件訊息
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = to_address
    msg['Cc'] = cc_address
    msg['Subject'] = subject

    # 加入郵件內文
    msg.attach(MIMEText(body, 'plain'))

    # 將收件者和副本合併為收件名單
    recipients = [to_address] + cc_address.split(",")

    try:
        # 透過 Gmail 的 SMTP 伺服器發送郵件
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # 啟用加密傳輸
            server.login(GMAIL_USER, GMAIL_PASSWORD)  # 登入 Gmail 帳戶
            server.sendmail(GMAIL_USER, recipients, msg.as_string())  # 發送郵件
        print("郵件發送成功！")
    except Exception as e:
        print(f"郵件發送失敗：{e}")

# 測試範例
if __name__ == "__main__":
    send_email(
        to_address="recipient@example.com",
        cc_address="cc@example.com",
        subject="測試郵件主旨",
        body="這是測試郵件內文。"
    )

