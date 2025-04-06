import smtplib
import sys
from email.mime.text import MIMEText

def send_test_email(smtp_server, smtp_port, smtp_user, smtp_password, sender_email, receiver_email, subject, message):
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        # Convert port to integer
        smtp_port = int(smtp_port)

        # Connect to the SMTP server
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Upgrade connection to secure if not using SSL directly

        # Perform authentication only if username is provided
        if smtp_user.strip():
            server.login(smtp_user, smtp_password)

        # Send email
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 9:
        print("Usage: python send_email.py <smtp_server> <smtp_port> <smtp_user> <smtp_password> <sender_email> <receiver_email> <subject> <message>")
        sys.exit(1)

    smtp_server = sys.argv[1]
    smtp_port = sys.argv[2]
    smtp_user = sys.argv[3].strip()
    smtp_password = sys.argv[4]
    sender = sys.argv[5].strip()
    receiver = sys.argv[6]
    subject = sys.argv[7]
    message = sys.argv[8]

    send_test_email(smtp_server, smtp_port, smtp_user, smtp_password, sender, receiver, subject, message)
