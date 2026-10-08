from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.database.connection import SessionLocal
from app.database.models import Monitoring, Search
from app.services.search_persistence_service import (
    SearchPersistenceService,
)
from app.services.search_service import SearchService


class SchedulerService:
    """
    Manages scheduled social-listening jobs.

    Each active Monitoring record gets one APScheduler job.

    Each scheduled execution creates a new Search record so
    every collection run remains separately traceable.

    Scheduler responsibilities:
        1. Load active monitoring records.
        2. Register APScheduler jobs.
        3. Execute scheduled searches.
        4. Persist collected and processed mentions.
        5. Update monitoring timestamps.
        6. Handle failed scheduled runs safely.
    """

    def __init__(self):
        self.scheduler = BackgroundScheduler(
            timezone="UTC"
        )

        self.search_service = SearchService()

        self.persistence_service = (
            SearchPersistenceService()
        )

    # =========================================================
    # START SCHEDULER
    # =========================================================

    def start(self):
        """
        Start APScheduler and load all active monitoring
        records from PostgreSQL.

        The scheduler is started only once.
        """

        if self.scheduler.running:
            print(
                "Scheduler is already running."
            )
            return

        self.scheduler.start()

        db = SessionLocal()

        try:
            monitorings = (
                db.query(Monitoring)
                .filter(
                    Monitoring.is_active.is_(True)
                )
                .all()
            )

            for monitoring in monitorings:
                self._schedule_monitoring(
                    monitoring
                )

            print(
                "Scheduler started successfully."
            )

            print(
                f"Loaded {len(monitorings)} "
                f"active monitoring job(s)."
            )

        finally:
            db.close()

    # =========================================================
    # SHUTDOWN SCHEDULER
    # =========================================================

    def shutdown(self):
        """
        Safely stop APScheduler.
        """

        if not self.scheduler.running:
            return

        self.scheduler.shutdown(
            wait=False
        )

        print(
            "Scheduler stopped."
        )

    # =========================================================
    # ADD MONITORING
    # =========================================================

    def add_monitoring(
        self,
        monitoring_id: int,
    ):
        """
        Add or replace a monitoring job.

        This method is normally called after a new
        Monitoring record is created or updated.
        """

        db = SessionLocal()

        try:
            monitoring = (
                db.query(Monitoring)
                .filter(
                    Monitoring.id
                    == monitoring_id
                )
                .first()
            )

            if monitoring is None:
                raise ValueError(
                    f"Monitoring {monitoring_id} "
                    f"not found."
                )

            if not monitoring.is_active:
                self.remove_monitoring(
                    monitoring_id
                )
                return

            self._schedule_monitoring(
                monitoring
            )

        finally:
            db.close()

    # =========================================================
    # REMOVE MONITORING
    # =========================================================

    def remove_monitoring(
        self,
        monitoring_id: int,
    ):
        """
        Remove a monitoring job from APScheduler.
        """

        job_id = self._job_id(
            monitoring_id
        )

        job = self.scheduler.get_job(
            job_id
        )

        if job is None:
            return

        self.scheduler.remove_job(
            job_id
        )

        print(
            f"Removed monitoring job: "
            f"{job_id}"
        )

    # =========================================================
    # SCHEDULE MONITORING
    # =========================================================

    def _schedule_monitoring(
        self,
        monitoring: Monitoring,
    ):
        """
        Register one Monitoring record with APScheduler.

        The first execution occurs after the configured
        interval rather than immediately.

        The calculated next execution time is also stored
        in PostgreSQL.
        """

        if not monitoring.is_active:
            return

        job_id = self._job_id(
            monitoring.id
        )

        # -----------------------------------------------------
        # Remove an existing job first
        # -----------------------------------------------------

        existing_job = (
            self.scheduler.get_job(
                job_id
            )
        )

        if existing_job is not None:
            self.scheduler.remove_job(
                job_id
            )

        # -----------------------------------------------------
        # Calculate first execution
        # -----------------------------------------------------

        now = datetime.now(
            timezone.utc
        )

        next_run_at = (
            now
            + timedelta(
                minutes=monitoring.interval_minutes
            )
        )

        # -----------------------------------------------------
        # Register APScheduler job
        # -----------------------------------------------------

        job = self.scheduler.add_job(
            self._run_monitoring,

            trigger=IntervalTrigger(
                minutes=monitoring.interval_minutes,
                timezone="UTC",
            ),

            args=[
                monitoring.id
            ],

            id=job_id,

            replace_existing=True,

            max_instances=1,

            coalesce=True,

            misfire_grace_time=300,

            next_run_time=next_run_at,
        )

        # -----------------------------------------------------
        # Store actual APScheduler next run time
        # -----------------------------------------------------

        self._update_next_run_time(
            monitoring.id,
            job.next_run_time,
        )

        print(
            f"Scheduled monitoring "
            f"#{monitoring.id}: "
            f"'{monitoring.keyword}' "
            f"every "
            f"{monitoring.interval_minutes} "
            f"minute(s)."
        )

        print(
            f"Next run: "
            f"{job.next_run_time.isoformat()}"
        )

    # =========================================================
    # RUN MONITORING
    # =========================================================

    def _run_monitoring(
        self,
        monitoring_id: int,
    ):
        """
        Execute one scheduled search.

        A new Search record is created for every execution.

        Successful execution:
            Monitoring.last_run_at is updated.

        Failed execution:
            The Search is marked failed and the monitoring
            schedule itself remains active.
        """

        db = SessionLocal()

        try:
            # -------------------------------------------------
            # Load monitoring
            # -------------------------------------------------

            monitoring = (
                db.query(Monitoring)
                .filter(
                    Monitoring.id
                    == monitoring_id
                )
                .first()
            )

            if monitoring is None:
                print(
                    f"Monitoring "
                    f"#{monitoring_id} "
                    f"no longer exists."
                )

                self.remove_monitoring(
                    monitoring_id
                )

                return

            # -------------------------------------------------
            # Check whether monitoring is still active
            # -------------------------------------------------

            if not monitoring.is_active:
                print(
                    f"Monitoring "
                    f"#{monitoring_id} "
                    f"is inactive."
                )

                self.remove_monitoring(
                    monitoring_id
                )

                return

            keyword = monitoring.keyword

            # -------------------------------------------------
            # Record actual run time
            # -------------------------------------------------

            run_started_at = (
                datetime.now(
                    timezone.utc
                )
            )

            # -------------------------------------------------
            # Logging
            # -------------------------------------------------

            print(
                "\n"
                + "=" * 70
            )

            print(
                "SCHEDULED MONITORING RUN"
            )

            print(
                "=" * 70
            )

            print(
                f"Monitoring ID: "
                f"{monitoring.id}"
            )

            print(
                f"Keyword: "
                f"{keyword}"
            )

            print(
                f"Interval: "
                f"{monitoring.interval_minutes} "
                f"minute(s)"
            )

            print(
                f"Started: "
                f"{run_started_at.isoformat()}"
            )

            # -------------------------------------------------
            # Create new Search record
            # -------------------------------------------------

            search = Search(
                keyword=keyword,
                status="pending",
            )

            db.add(search)

            db.commit()

            db.refresh(search)

            try:
                # ---------------------------------------------
                # Mark search as running
                # ---------------------------------------------

                self.persistence_service.mark_search_started(
                    db=db,
                    search=search,
                )

                # ---------------------------------------------
                # Collect and process mentions
                # ---------------------------------------------

                result = (
                    self.search_service.run_search(
                        keyword=keyword,
                        limit_per_source=10,
                    )
                )

                raw_mentions = result.get(
                    "raw_mentions",
                    [],
                )

                processed_mentions = result.get(
                    "processed_mentions",
                    [],
                )

                # ---------------------------------------------
                # Save processed results
                #
                # IMPORTANT:
                #
                # save_search_results() returns the actual
                # number of mentions saved after relevance
                # filtering and duplicate filtering.
                # ---------------------------------------------

                saved_count = (
                    self.persistence_service.save_search_results(
                        db=db,
                        search=search,
                        processed_mentions=processed_mentions,
                        raw_count=len(
                            raw_mentions
                        ),
                    )
                )

                # ---------------------------------------------
                # Mark search completed
                # ---------------------------------------------

                self.persistence_service.mark_search_completed(
                    db=db,
                    search=search,
                )

                # ---------------------------------------------
                # Update monitoring
                # ---------------------------------------------

                run_completed_at = (
                    datetime.now(
                        timezone.utc
                    )
                )

                monitoring.last_run_at = (
                    run_completed_at
                )

                # -------------------------------------------------
                # Read next run directly from APScheduler
                # -------------------------------------------------

                job = self.scheduler.get_job(
                    self._job_id(
                        monitoring.id
                    )
                )

                if job is not None:
                    monitoring.next_run_at = (
                        job.next_run_time
                    )
                else:
                    monitoring.next_run_at = (
                        run_completed_at
                        + timedelta(
                            minutes=monitoring.interval_minutes
                        )
                    )

                db.commit()

                # ---------------------------------------------
                # Success logging
                # ---------------------------------------------

                print(
                    "Scheduled search completed "
                    "successfully."
                )

                print(
                    f"Search ID: "
                    f"{search.id}"
                )

                print(
                    f"Collected: "
                    f"{len(raw_mentions)}"
                )

                # -------------------------------------------------
                # IMPORTANT:
                #
                # Print saved_count instead of
                # len(processed_mentions).
                #
                # saved_count represents the actual number
                # persisted after relevance and deduplication.
                # -------------------------------------------------

                print(
                    f"Processed: "
                    f"{saved_count}"
                )

                print(
                    f"Completed: "
                    f"{run_completed_at.isoformat()}"
                )

                if monitoring.next_run_at:
                    print(
                        f"Next run: "
                        f"{monitoring.next_run_at.isoformat()}"
                    )

            except Exception as error:

                # ---------------------------------------------
                # Roll back current transaction
                # ---------------------------------------------

                db.rollback()

                # ---------------------------------------------
                # Mark search as failed
                # ---------------------------------------------

                failed_search = (
                    db.query(Search)
                    .filter(
                        Search.id
                        == search.id
                    )
                    .first()
                )

                if failed_search is not None:
                    self.persistence_service.mark_search_failed(
                        db=db,
                        search=failed_search,
                    )

                # ---------------------------------------------
                # Keep monitoring active
                # ---------------------------------------------

                failure_time = (
                    datetime.now(
                        timezone.utc
                    )
                )

                monitoring = (
                    db.query(Monitoring)
                    .filter(
                        Monitoring.id
                        == monitoring_id
                    )
                    .first()
                )

                if monitoring is not None:

                    job = self.scheduler.get_job(
                        self._job_id(
                            monitoring_id
                        )
                    )

                    if job is not None:
                        monitoring.next_run_at = (
                            job.next_run_time
                        )
                    else:
                        monitoring.next_run_at = (
                            failure_time
                            + timedelta(
                                minutes=monitoring.interval_minutes
                            )
                        )

                    db.commit()

                # ---------------------------------------------
                # Failure logging
                # ---------------------------------------------

                print(
                    "\n"
                    "Scheduled monitoring failed:"
                )

                print(
                    f"{type(error).__name__}: "
                    f"{error}"
                )

                print(
                    f"Search ID: "
                    f"{search.id}"
                )

                if monitoring is not None:
                    print(
                        f"Next scheduled run: "
                        f"{monitoring.next_run_at}"
                    )

            print(
                "=" * 70
                + "\n"
            )

        except Exception as error:

            # -------------------------------------------------
            # Protect APScheduler worker from unexpected errors
            # -------------------------------------------------

            print(
                "\n"
                "Unexpected scheduler error:"
            )

            print(
                f"{type(error).__name__}: "
                f"{error}"
            )

        finally:
            db.close()

    # =========================================================
    # UPDATE NEXT RUN TIME
    # =========================================================

    @staticmethod
    def _update_next_run_time(
        monitoring_id: int,
        next_run_at,
    ):
        """
        Persist the APScheduler job's next execution time
        in PostgreSQL.
        """

        if next_run_at is None:
            return

        db = SessionLocal()

        try:
            monitoring = (
                db.query(Monitoring)
                .filter(
                    Monitoring.id
                    == monitoring_id
                )
                .first()
            )

            if monitoring is None:
                return

            monitoring.next_run_at = (
                next_run_at
            )

            db.commit()

        finally:
            db.close()

    # =========================================================
    # GET JOB ID
    # =========================================================

    @staticmethod
    def _job_id(
        monitoring_id: int,
    ) -> str:
        return (
            f"monitoring:{monitoring_id}"
        )


# =========================================================
# SINGLE SCHEDULER INSTANCE
# =========================================================

scheduler_service = SchedulerService()