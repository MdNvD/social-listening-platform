from transformers import pipeline


class SentimentService:
    """
    Sentiment analysis service using a Hugging Face model.

    Primary model:
        cardiffnlp/twitter-roberta-base-sentiment-latest

    Output:
        positive
        neutral
        negative

    V2 adds a lightweight domain-aware adjustment layer for
    social-listening content.

    The Hugging Face model remains the primary classifier.
    """

    MODEL_NAME = (
        "cardiffnlp/twitter-roberta-base-sentiment-latest"
    )

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
    }

    def __init__(self):

        self.classifier = pipeline(
            "sentiment-analysis",
            model=self.MODEL_NAME,
            tokenizer=self.MODEL_NAME,
        )

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

        # -----------------------------------------------------
        # Hugging Face model
        # -----------------------------------------------------

        result = self.classifier(
            text,
            truncation=True,
            max_length=512,
        )[0]

        model_sentiment = (
            result["label"]
            .lower()
        )

        model_confidence = round(
            float(result["score"]),
            4,
        )

        # -----------------------------------------------------
        # Domain-aware adjustment
        # -----------------------------------------------------

        adjusted_sentiment = (
            self._apply_domain_adjustment(
                text=text,
                model_sentiment=model_sentiment,
                model_confidence=model_confidence,
            )
        )

        # -----------------------------------------------------
        # Confidence
        # -----------------------------------------------------

        adjusted_confidence = (
            self._calculate_confidence(
                original_confidence=model_confidence,
                original_sentiment=model_sentiment,
                adjusted_sentiment=adjusted_sentiment,
                text=text,
            )
        )

        return {
            "sentiment": adjusted_sentiment,
            "confidence": adjusted_confidence,
        }

    # =========================================================
    # Domain adjustment
    # =========================================================

    def _apply_domain_adjustment(
        self,
        text: str,
        model_sentiment: str,
        model_confidence: float,
    ) -> str:

        normalized_text = (
            self._normalize_text(text)
        )

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

        negative_count = len(
            negative_matches
        )

        positive_count = len(
            positive_matches
        )

        # -----------------------------------------------------
        # Strong negative domain signal
        # -----------------------------------------------------
        #
        # We only override the model when:
        #
        # 1. There is a strong negative signal.
        # 2. The model predicted neutral.
        #
        # This avoids unnecessarily overriding confident
        # positive/negative model predictions.
        # -----------------------------------------------------

        if (
            model_sentiment == "neutral"
            and negative_count >= 1
        ):

            return "negative"

        # -----------------------------------------------------
        # Strong positive domain signal
        # -----------------------------------------------------

        if (
            model_sentiment == "neutral"
            and positive_count >= 1
        ):

            return "positive"

        # -----------------------------------------------------
        # If the model is already decisive, preserve it.
        # -----------------------------------------------------

        return model_sentiment

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

            if (
                normalized_signal
                in text
            ):

                matches.append(
                    normalized_signal
                )

        return matches

    # =========================================================
    # Confidence calculation
    # =========================================================

    def _calculate_confidence(
        self,
        original_confidence: float,
        original_sentiment: str,
        adjusted_sentiment: str,
        text: str,
    ) -> float:

        # No adjustment.
        if (
            original_sentiment
            == adjusted_sentiment
        ):

            return round(
                original_confidence,
                4,
            )

        # -----------------------------------------------------
        # The domain layer changed the model result.
        #
        # Do not pretend the rule-based adjustment has the same
        # certainty as the neural model.
        #
        # Use a conservative confidence floor.
        # -----------------------------------------------------

        if adjusted_sentiment == "negative":

            return round(
                max(
                    0.60,
                    original_confidence,
                ),
                4,
            )

        if adjusted_sentiment == "positive":

            return round(
                max(
                    0.60,
                    original_confidence,
                ),
                4,
            )

        return round(
            original_confidence,
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