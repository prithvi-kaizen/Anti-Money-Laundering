from fastapi import APIRouter

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("")
def get_metrics():
    # Return mock impact metrics for the ImpactDashboard as specified
    return {
        "manual_time": "4.2 hours avg",
        "sentinel_time": "11 minutes",
        "sar_accuracy_baseline": "71%",
        "sar_accuracy_sentinel": "94%",
        "fp_rate_baseline": "38%",
        "fp_rate_sentinel": "12%",
        "daily_throughput_manual": "8 alerts",
        "daily_throughput_sentinel": "140 alerts",
        "annual_savings": "$2.1M",
        "trend_data": [
            {"day": "-30d", "manual": 8, "sentinel": 120},
            {"day": "-20d", "manual": 8, "sentinel": 135},
            {"day": "-10d", "manual": 8, "sentinel": 145},
            {"day": "Today", "manual": 8, "sentinel": 140}
        ]
    }
