class SentimentService:
    """
    Lightweight domain-aware sentiment analysis service.

    Classifies text as:
        positive
        neutral
        negative

    Uses keyword and phrase-based signals instead of a
    Hugging Face Transformer model.

    This keeps the service lightweight enough for small
    deployment environments.
    """

    # ---------------------------------------------------------
    # Domain sentiment signals
    # ---------------------------------------------------------

    NEGATIVE_SIGNALS = {
        "attack",
        "attacked",
        "breach",
        "breached",
        "bug",
        "bugs",
        "broken",
        "complaint",
        "complaints",
        "critical flaw",
        "critical issue",
        "danger",
        "dangerous",
        "exploit",
        "exploited",
        "exploits",
        "failure",
        "flaw",
        "hack",
        "hacked",
        "issue",
        "issues",
        "leak",
        "malware",
        "outage",
        "problem",
        "problems",
        "risk",
        "security flaw",
        "security issue",
        "vulnerability",
        "vulnerabilities",
        "zero day",
        "zero-day",
        "zero click",
        "zero-click",
        "pwned",
        "permission bypass",
        "disappointed",
        "disappointing",
        "terrible",
        "awful",
        "worst",
        "poor",
        "bad",
        "hate",
        "hated",
        "slow",
        "expensive",
    }

    POSITIVE_SIGNALS = {
        "excellent",
        "amazing",
        "best",
        "great",
        "love",
        "loved",
        "improved",
        "improvement",
        "success",
        "successful",
        "recommend",
        "recommended",
        "impressive",
        "fantastic",
        "outstanding",
        "good",
        "better",
        "awesome",
        "perfect",
        "fast",
        "reliable",
        "useful",
        "helpful",
    }

    # Phrases that are stronger than individual words.
    STRONG_NEGATIVE_SIGNALS = {
        "very disappointed",
        "extremely disappointed",
        "terrible experience",
        "awful experience",
        "worst experience",
        "critical security flaw",
        "critical security issue",
        "major security vulnerability",
        "serious security issue",
        "data breach",
        "security breach",
        "does not work",
        "doesn't work",
        "not working",
        "stopped working",
        "completely broken",
    }

    STRONG_POSITIVE_SIGNALS = {
        "highly recommend",
        "strongly recommend",
        "very good",
        "very impressive",
        "excellent performance",
        "excellent battery life",
        "great performance",
        "great battery life",
        "works perfectly",
        "works great",
    }

    def __init__(self):
        """
        No external ML model is loaded.

        This makes application startup fast and keeps
        memory usage low.
        """
        pass

    # =========================================================
    # Main analysis
    # =========================================================

    def analyze(
        self,
        text: str,
    ) -> dict:

        text = text.strip()

        if not text:
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
            }

        normalized_text = self._normalize_text(
            text
        )

        # -----------------------------------------------------
        # Find matching signals
        # -----------------------------------------------------

        negative_matches = (
            self._find_signal_matches(
                normalized_text,
                self.NEGATIVE_SIGNALS,
            )
        )

        positive_matches = (
            self._find_signal_matches(
                normalized_text,
                self.POSITIVE_SIGNALS,
            )
        )

        strong_negative_matches = (
            self._find_signal_matches(
                normalized_text,
                self.STRONG_NEGATIVE_SIGNALS,
            )
        )

        strong_positive_matches = (
            self._find_signal_matches(
                normalized_text,
                self.STRONG_POSITIVE_SIGNALS,
            )
        )

        # -----------------------------------------------------
        # Calculate weighted scores
        # -----------------------------------------------------

        negative_score = (
            len(negative_matches)
            + len(strong_negative_matches) * 2
        )

        positive_score = (
            len(positive_matches)
            + len(strong_positive_matches) * 2
        )

        # A positive statement combined with a minor issue
        # should remain positive rather than becoming neutral.
        if (
            "minor issue" in normalized_text
            or "minor problem" in normalized_text
        ):
            negative_score = max(
                0,
                negative_score - 1,
            )

        # -----------------------------------------------------
        # No sentiment signals
        # -----------------------------------------------------

        if (
            negative_score == 0
            and positive_score == 0
        ):
            return {
                "sentiment": "neutral",
                "confidence": 0.50,
            }

        # -----------------------------------------------------
        # Negative wins
        # -----------------------------------------------------

        if negative_score > positive_score:

            confidence = self._calculate_rule_confidence(
                winning_score=negative_score,
                losing_score=positive_score,
            )

            return {
                "sentiment": "negative",
                "confidence": confidence,
            }

        # -----------------------------------------------------
        # Positive wins
        # -----------------------------------------------------

        if positive_score > negative_score:

            confidence = self._calculate_rule_confidence(
                winning_score=positive_score,
                losing_score=negative_score,
            )

            return {
                "sentiment": "positive",
                "confidence": confidence,
            }

        # -----------------------------------------------------
        # Equal positive and negative signals
        # -----------------------------------------------------

        return {
            "sentiment": "neutral",
            "confidence": 0.50,
        }

    # =========================================================
    # Signal matching
    # =========================================================

    @classmethod
    def _find_signal_matches(
        cls,
        text: str,
        signals: set[str],
    ) -> list[str]:

        matches = []

        for signal in signals:

            normalized_signal = (
                cls._normalize_text(signal)
            )

            if not normalized_signal:
                continue

            if normalized_signal in text:
                matches.append(
                    normalized_signal
                )

        return matches

    # =========================================================
    # Confidence
    # =========================================================

    @staticmethod
    def _calculate_rule_confidence(
        winning_score: int,
        losing_score: int,
    ) -> float:

        total = (
            winning_score
            + losing_score
        )

        if total <= 0:
            return 0.50

        # Base confidence based on how strongly one
        # sentiment dominates the other.
        confidence = (
            winning_score / total
        )

        # Conservative floor.
        confidence = max(
            0.60,
            confidence,
        )

        # Cap confidence because this is a
        # rule-based classifier, not a neural model.
        confidence = min(
            0.95,
            confidence,
        )

        return round(
            confidence,
            4,
        )

    # =========================================================
    # Text normalization
    # =========================================================

    @staticmethod
    def _normalize_text(
        text: str,
    ) -> str:

        text = text.lower()

        return " ".join(
            text.split()
        )