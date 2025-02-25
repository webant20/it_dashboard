import smtplib
import sys
from email.mime.text import MIMEText

def send_test_email(sender_email, receiver_email, password, subject, message):
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python test_email.py <sender_email> <receiver_email> <password> <subject> <message>")
        sys.exit(1)

    sender = sys.argv[1]
    receiver = sys.argv[2]
    password = sys.argv[3]
    subject = sys.argv[4]
    message = sys.argv[5]

    send_test_email(sender, receiver, password, subject, message)
