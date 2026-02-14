"""
Sentinel AML — Timing Comparison Router
"""

import random
from fastapi import APIRouter

router = APIRouter(tags=["timing"])


@router.get("/timing")
def get_timing_comparison():
    """
    Simulate timing comparison between manual and Sentinel-assisted investigation.
    Based on industry benchmarks: manual = 2-4 hours, AI-assisted = 0.5-1.5 hours.
    """
    random.seed(42)
    sample_size = 20

    manual_times = [random.uniform(90, 240) for _ in range(sample_size)]   # minutes
    sentinel_times = [random.uniform(20, 80) for _ in range(sample_size)]  # minutes

    manual_avg = sum(manual_times) / len(manual_times)
    sentinel_avg = sum(sentinel_times) / len(sentinel_times)
    reduction = ((manual_avg - sentinel_avg) / manual_avg) * 100

    return {
        "manual_avg_minutes": round(manual_avg, 1),
        "sentinel_avg_minutes": round(sentinel_avg, 1),
        "reduction_percent": round(reduction, 1),
        "sample_size": sample_size,
        "manual_samples": [round(t, 1) for t in manual_times],
        "sentinel_samples": [round(t, 1) for t in sentinel_times],
    }
