import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.funding_intel.scheduler import jobs as scheduler_jobs


class DummyScheduler:
    def __init__(self):
        self.running = False
        self.jobs = []

    def add_job(self, *args, **kwargs):
        self.jobs.append(kwargs.get("id"))

    def start(self):
        self.running = True

    def shutdown(self, wait=False):
        self.running = False

    def get_jobs(self):
        return self.jobs


class SchedulerStartupTests(unittest.TestCase):
    def test_start_scheduler_schedules_initial_sync(self):
        calls = []

        async def fake_daily_sync_job():
            calls.append("run")
            return {"status": "ok"}

        with patch.object(scheduler_jobs, "build_scheduler", return_value=DummyScheduler()), patch.object(
            scheduler_jobs, "daily_sync_job", side_effect=fake_daily_sync_job
        ), patch.object(
            scheduler_jobs,
            "funding_intel_settings",
            SimpleNamespace(
                ENABLED=True,
                DAILY_SYNC_CRON="0 3 * * *",
                WEEKLY_CLEANUP_CRON="0 4 * * 0",
                RUN_INITIAL_SYNC_ON_STARTUP=True,
            ),
        ):
            scheduler_jobs._scheduler = None

            async def run_startup():
                scheduler_jobs.start_scheduler()
                await asyncio.sleep(0)

            asyncio.run(run_startup())

        self.assertEqual(calls, ["run"])


if __name__ == "__main__":
    unittest.main()
