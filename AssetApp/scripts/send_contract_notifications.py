import os
import sys
import django
import logging
import subprocess
from django.utils import timezone

# Set up logging
LOG_FILE = "/home/it_admin/django_projects/it_dashboard/logs/contract_notifications.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set up Django environment
sys.path.append("/home/it_admin/django_projects/it_dashboard")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "itdashboard.settings")
django.setup()

# Import models
from AssetApp.models import ContractNotification, SMTPSettings

# Path to your test_email.py script
TEST_EMAIL_SCRIPT = "/home/it_admin/django_projects/it_dashboard/AssetApp/scripts/send_email.py"

def send_contract_expiry_notifications():
    today = timezone.now().date()
    logger.info(f"Script started at {today}")
    print(f"Script started at {today}")

    # Fetch SMTP settings
    smtp_settings = SMTPSettings.objects.first()
    if not smtp_settings:
        logger.error("No SMTP settings found. Exiting.")
        print("No SMTP settings found. Exiting.")
        return

    logger.info(f"Using SMTP Server: {smtp_settings.smtp_server}, Email: {smtp_settings.smtp_username}")
    print(f"Using SMTP Server: {smtp_settings.smtp_server}, Email: {smtp_settings.smtp_username}")

    # Fetch notifications
    notifications = ContractNotification.objects.select_related("contract").all()
    logger.info(f"Found {notifications.count()} notifications to process.")
    print(f"Found {notifications.count()} notifications to process.")

    for notification in notifications:
        contract = notification.contract

        if not contract.end_date:
            logger.warning(f"Contract {contract.contract_number} has no end date. Skipping.")
            print(f"Contract {contract.contract_number} has no end date. Skipping.")
            continue

        days_remaining = (contract.end_date - today).days
        days_before_expiry_list = notification.get_days_list()

        logger.info(f"Contract {contract.contract_number}: Days remaining: {days_remaining}, Notification days: {days_before_expiry_list}")
        print(f"Contract {contract.contract_number}: Days remaining: {days_remaining}, Notification days: {days_before_expiry_list}")

        # Check if the contract expiry is within the specified notification days
        if days_remaining in days_before_expiry_list:
            email_list = notification.get_email_list()

            if not email_list:
                logger.warning(f"No email addresses found for contract {contract.contract_number}. Skipping.")
                print(f"No email addresses found for contract {contract.contract_number}. Skipping.")
                continue

            subject = f"Contract Expiry Alert: {contract.contract_number}"
            message = f"The contract '{contract.contract_number}' is expiring on {contract.end_date}."

            # Send email using test_email.py script
            for email in email_list:
                try:
                    command = [
                        "python3", TEST_EMAIL_SCRIPT,
                        smtp_settings.smtp_username,  # Sender email
                        email,  # Receiver email
                        smtp_settings.smtp_password,  # SMTP password
                        subject,
                        message
                    ]
                    subprocess.run(command, check=True, capture_output=True, text=True)

                    logger.info(f"Notification email sent successfully for contract {contract.contract_number} to {email}")
                    print(f"Notification email sent successfully for contract {contract.contract_number} to {email}")

                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to send email for contract {contract.contract_number} to {email}: {e.stderr}")
                    print(f"Failed to send email for contract {contract.contract_number} to {email}: {e.stderr}")

if __name__ == "__main__":
    send_contract_expiry_notifications()
