import smtplib
from email.mime.text import MIMEText

sender_email = "tituraj.jnv@gmail.com"
receiver_email = "tituraj_doley@oilindia.in"
password = "pekb yalj ugjs samn"  # Use App Password

msg = MIMEText("This is a test email.")
msg["Subject"] = "Test Email"
msg["From"] = sender_email
msg["To"] = receiver_email

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
    print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")
