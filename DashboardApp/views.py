from django.shortcuts import render
from datetime import timedelta
from django.utils.timezone import now
from AssetApp.models import Asset, PR
from incidentApp.models import Incident

def dashboard_view(request):
    # Get filter criteria (default to 1 month)
    period = request.GET.get("period", "1m")
    
    # Define time range
    today = now().date()
    if period == "6m":
        start_date = today - timedelta(days=180)
    elif period == "1y":
        start_date = today - timedelta(days=365)
    else:
        start_date = today - timedelta(days=30)

    # Fetch data
    num_assets_added = Asset.objects.filter(installation_date__gte=start_date).count()
    num_assets_issued = Asset.objects.filter(assetissue__issue_date__gte=start_date).count()
    
    
    num_open_prs = PR.objects.filter(status="Open").count()  # All-time open PRs
    num_prs_raised = PR.objects.filter(create_date__gte=start_date).count()
    num_prs_processed = PR.objects.filter(status="Closed", create_date__gte=start_date).count()

    num_open_incidents = Incident.objects.filter(status="Open").count()  # All-time open incidents
    num_incidents_raised = Incident.objects.filter(created_at__gte=start_date).count()

    context = {
        "num_assets_added": num_assets_added,
        "num_assets_issued": num_assets_issued,
        "num_open_prs": num_open_prs,
        "num_prs_raised": num_prs_raised,
        "num_prs_processed": num_prs_processed,
        "num_open_incidents": num_open_incidents,
        "num_incidents_raised": num_incidents_raised,
        "selected_period": period,
    }

    return render(request, "DashboardApp/dashboard.html", context)
