import os
import sys
import django
from django.utils import timezone
from django.core.mail import send_mail

# Set up Django environment
sys.path.append("/home/it_admin/django_projects/it_dashboard")  # Ensure project root is in sys.path
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "itdashboard.settings")  # Ensure correct settings module
django.setup()

# Now import models
from AssetApp.models import Contract, ContractNotification, SMTPSettings

def send_contract_expiry_notifications():
    today = timezone.now().date()
    print(f"Script started at {today}")

    # Get SMTP settings from the database
    smtp_settings = SMTPSettings.objects.first()
    if not smtp_settings:
        print("No SMTP settings configured. Exiting.")
        return

    print(f"Using SMTP Server: {smtp_settings.smtp_server}, Email: {smtp_settings.smtp_username}")

    # Get all contract notifications that should be triggered
    notifications = ContractNotification.objects.all()
    print(f"Found {notifications.count()} notifications to process.")

    for notification in notifications:
        contract = notification.contract
        days_remaining = (contract.end_date - today).days

        print(f"Processing contract {contract.contract_number}, Days remaining: {days_remaining}")

        if days_remaining == notification.days_before_expiry:
            email_list = notification.get_email_list()
            print(f"Sending email to: {email_list}")

            subject = f"Contract Expiry Alert: {contract.contract_number}"
            message = f"The contract '{contract.contract_number}' is expiring on {contract.end_date}."

            try:
                send_mail(
                    subject,
                    message,
                    smtp_settings.smtp_username,  # From email
                    email_list,  # To email list
                    fail_silently=False,
                )
                print(f"Notification email sent successfully for contract {contract.contract_number}")
            except Exception as e:
                print(f"Failed to send email for contract {contract.contract_number}: {e}")

if __name__ == "__main__":
    send_contract_expiry_notifications()
