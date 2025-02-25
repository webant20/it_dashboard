import os
import sys
import django

# Ensure Django finds the project
sys.path.append("/home/it_admin/django_projects/it_dashboard")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "itdashboard.settings")

django.setup()

# Now import models AFTER django.setup()
from PlannedActivityApp.models import PeriodicActivityMaster, PlannedActivity
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# Frequency to timedelta mapping
FREQUENCY_MAPPING = {
    "Weekly": 7,
    "Monthly": 30,  # Approximate
    "Quarterly": 90,
    "Half-Yearly": 180,
    "Yearly": 365,
}

def generate_planned_activities():
    today = timezone.now().date()

    for activity in PeriodicActivityMaster.objects.filter(status="Enabled"):
        frequency_days = FREQUENCY_MAPPING.get(activity.frequency)
        if not frequency_days:
            print(f"Skipping activity {activity.name}: Invalid frequency")
            continue

        due_date = activity.start_date
        while due_date <= activity.end_date:
            if due_date >= today:
                # Check if entry already exists
                if not PlannedActivity.objects.filter(periodic_activity=activity, due_date=due_date).exists():
                    assigned_user = User.objects.order_by('?').first()  # Assign randomly
                    PlannedActivity.objects.create(
                        periodic_activity=activity,
                        due_date=due_date,
                        assigned_to=assigned_user,
                        status="Open"
                    )
                    print(f"Created planned activity for {activity.name} on {due_date}")

            due_date += timedelta(days=frequency_days)

if __name__ == "__main__":
    generate_planned_activities()
