"""Background scheduler for the Funding Intelligence Service.

The scheduler is started by ``app.main`` during application startup
and shut down on application exit. It runs three recurring jobs:

* ``daily_sync``     — incremental sync of every enabled provider.
* ``weekly_cleanup`` — full sync + mark expired rows.
* ``health_probe``   — periodic health snapshot of each provider.
"""
from .jobs import (
    start_scheduler,
    stop_scheduler,
    scheduler_running,
    daily_sync_job,
    weekly_cleanup_job,
    health_probe_job,
    build_scheduler,
)

__all__ = [
    "start_scheduler",
    "stop_scheduler",
    "scheduler_running",
    "daily_sync_job",
    "weekly_cleanup_job",
    "health_probe_job",
    "build_scheduler",
]
