from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.database.models import (
    Mention,
    MentionAnalysis,
    Search,
)


class AlertService:
    """
    Detect deterministic statistical alert conditions from
    processed social-listening mentions.

    Current alert:
        - Negative sentiment spike

    Monitoring periods:

        Recent:
            last 7 days

        Previous:
            7 days immediately before the recent period

    Scheduled monitoring creates a new Search record for
    each monitoring run.

    Therefore, alert calculations aggregate processed
    mentions across completed searches for the same keyword.

    Timestamp priority:

        collected_at
            Preferred because monitoring should measure
            when the platform observed the mention.

        published_at
            Used as a fallback when collected_at is unavailable.

    Alerts are deterministic and do not use an LLM.
    """

    # =========================================================
    # Monitoring configuration
    # =========================================================

    RECENT_DAYS = 7

    MIN_RECENT_MENTIONS = 3
    MIN_RECENT_NEGATIVE_MENTIONS = 2

    # Prevent alerts when there is almost no historical
    # comparison data.
    MIN_PREVIOUS_MENTIONS = 3

    # 0.20 = 20 percentage-point increase.
    SPIKE_RATE_INCREASE = 0.20

    # =========================================================
    # Main alert calculation
    # =========================================================

    def get_alerts(
        self,
        db: Session,
        search_id: int,
    ) -> dict[str, Any]:

        # -----------------------------------------------------
        # Find selected search
        # -----------------------------------------------------

        search = (
            db.query(Search)
            .filter(
                Search.id == search_id
            )
            .first()
        )

        if search is None:
            return None

        keyword = search.keyword.strip()

        # -----------------------------------------------------
        # Current time
        # -----------------------------------------------------

        now = datetime.now(timezone.utc)

        # -----------------------------------------------------
        # Monitoring periods
        # -----------------------------------------------------

        recent_start = (
            now
            - timedelta(
                days=self.RECENT_DAYS
            )
        )

        previous_start = (
            recent_start
            - timedelta(
                days=self.RECENT_DAYS
            )
        )

        # -----------------------------------------------------
        # Find all completed searches for this keyword
        # -----------------------------------------------------

        matching_search_ids = [
            row[0]
            for row in (
                db.query(Search.id)
                .filter(
                    Search.keyword.ilike(
                        keyword
                    )
                )
                .filter(
                    Search.status == "completed"
                )
                .all()
            )
        ]

        # Always include requested search.
        if search_id not in matching_search_ids:
            matching_search_ids.append(
                search_id
            )

        # -----------------------------------------------------
        # Load relevant, non-duplicate mentions
        # -----------------------------------------------------

        rows = (
            db.query(
                Mention,
                MentionAnalysis,
            )
            .join(
                MentionAnalysis,
                Mention.id
                == MentionAnalysis.mention_id,
            )
            .filter(
                Mention.search_id.in_(
                    matching_search_ids
                )
            )
            .filter(
                MentionAnalysis.is_relevant.is_(
                    True
                )
            )
            .filter(
                MentionAnalysis.is_duplicate.is_(
                    False
                )
            )
            .all()
        )

        # -----------------------------------------------------
        # Separate mentions into monitoring periods
        # -----------------------------------------------------

        recent_rows = []
        previous_rows = []

        for mention, analysis in rows:

            # Prefer collected_at because this represents
            # when our platform observed the mention.
            timestamp = (
                mention.collected_at
                or mention.published_at
            )

            if timestamp is None:
                continue

            timestamp = self._ensure_utc(
                timestamp
            )

            # -------------------------------------------------
            # Recent period
            # -------------------------------------------------

            if (
                recent_start
                <= timestamp
                <= now
            ):
                recent_rows.append(
                    (
                        mention,
                        analysis,
                    )
                )

            # -------------------------------------------------
            # Previous period
            # -------------------------------------------------

            elif (
                previous_start
                <= timestamp
                < recent_start
            ):
                previous_rows.append(
                    (
                        mention,
                        analysis,
                    )
                )

        # -----------------------------------------------------
        # Counts
        # -----------------------------------------------------

        recent_total = len(
            recent_rows
        )

        previous_total = len(
            previous_rows
        )

        recent_negative = (
            self._count_negative(
                recent_rows
            )
        )

        previous_negative = (
            self._count_negative(
                previous_rows
            )
        )

        # -----------------------------------------------------
        # Negative sentiment rates
        # -----------------------------------------------------

        recent_negative_rate = (
            recent_negative
            / recent_total
            if recent_total
            else 0.0
        )

        previous_negative_rate = (
            previous_negative
            / previous_total
            if previous_total
            else 0.0
        )

        # -----------------------------------------------------
        # Rate change
        # -----------------------------------------------------

        rate_change = (
            recent_negative_rate
            - previous_negative_rate
        )

        # -----------------------------------------------------
        # Data sufficiency
        # -----------------------------------------------------

        enough_recent_data = (
            recent_total
            >= self.MIN_RECENT_MENTIONS
        )

        enough_negative_data = (
            recent_negative
            >= self.MIN_RECENT_NEGATIVE_MENTIONS
        )

        enough_previous_data = (
            previous_total
            >= self.MIN_PREVIOUS_MENTIONS
        )

        alerts = []

        # =====================================================
        # Negative sentiment spike
        # =====================================================

        if (
            enough_recent_data
            and enough_negative_data
            and enough_previous_data
            and rate_change
            >= self.SPIKE_RATE_INCREASE
        ):

            alerts.append(
                {
                    "type": (
                        "negative_sentiment_spike"
                    ),
                    "severity": "high",
                    "title": (
                        "Negative sentiment spike detected"
                    ),
                    "description": (
                        "The negative sentiment rate "
                        "during the recent monitoring "
                        "period increased by at least "
                        f"{self.SPIKE_RATE_INCREASE * 100:.0f} "
                        "percentage points compared "
                        "with the previous monitoring "
                        "period."
                    ),
                    "evidence": {
                        "recent_mentions": (
                            recent_total
                        ),
                        "recent_negative_mentions": (
                            recent_negative
                        ),
                        "recent_negative_rate": round(
                            recent_negative_rate,
                            4,
                        ),
                        "previous_mentions": (
                            previous_total
                        ),
                        "previous_negative_mentions": (
                            previous_negative
                        ),
                        "previous_negative_rate": round(
                            previous_negative_rate,
                            4,
                        ),
                        "rate_change": round(
                            rate_change,
                            4,
                        ),
                    },
                }
            )

        # =====================================================
        # Return alert result
        # =====================================================

        return {
            "search_id": search.id,

            "keyword": search.keyword,

            "period": {
                "recent_days": (
                    self.RECENT_DAYS
                ),
                "recent_start": (
                    recent_start
                ),
                "previous_start": (
                    previous_start
                ),
                "end": now,
            },

            "summary": {
                "recent_mentions": (
                    recent_total
                ),

                "recent_negative_mentions": (
                    recent_negative
                ),

                "recent_negative_rate": round(
                    recent_negative_rate,
                    4,
                ),

                "previous_mentions": (
                    previous_total
                ),

                "previous_negative_mentions": (
                    previous_negative
                ),

                "previous_negative_rate": round(
                    previous_negative_rate,
                    4,
                ),

                "negative_rate_change": round(
                    rate_change,
                    4,
                ),

                "enough_recent_data": (
                    enough_recent_data
                ),

                "enough_previous_data": (
                    enough_previous_data
                ),
            },

            "alerts": alerts,

            "alert_count": len(
                alerts
            ),
        }

    # =========================================================
    # Count negative mentions
    # =========================================================

    @staticmethod
    def _count_negative(
        rows,
    ) -> int:

        return sum(
            1
            for _, analysis in rows
            if analysis.sentiment
            == "negative"
        )

    # =========================================================
    # Normalize datetime to UTC
    # =========================================================

    @staticmethod
    def _ensure_utc(
        value: datetime,
    ) -> datetime:

        if value.tzinfo is None:
            return value.replace(
                tzinfo=timezone.utc
            )

        return value.astimezone(
            timezone.utc
        )