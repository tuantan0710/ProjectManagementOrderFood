from flask_mail import Message
from app import mail, app


def send_gmail(to, subject, html_content):
    with app.app_context():
        msg = Message(subject=subject,
                      recipients=[to],
                      html=html_content)
        try:
            mail.send(msg)
            print("Email gửi thành công")
        except Exception as e:
            print("Gửi mail lỗi:", e)
