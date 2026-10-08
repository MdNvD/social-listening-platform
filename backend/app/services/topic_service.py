import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TopicService:
    """
    Lightweight topic classification service.

    Uses TF-IDF instead of SentenceTransformer embeddings
    to keep memory usage low enough for small deployment
    environments such as Render's free tier.
    """

    TOPIC_EXAMPLES = {
        "Product": [
            "Samsung Galaxy phone",
            "new smartphone product",
            "device model",
            "phone specifications",
            "product release",
        ],
        "Pricing": [
            "phone price",
            "product price",
            "discount",
            "deal",
            "sale",
            "expensive",
            "cheap",
            "cost",
            "price increased",
            "price reduced",
        ],
        "Customer service": [
            "customer support",
            "customer service",
            "support team",
            "service request",
            "help from support",
        ],
        "Quality": [
            "build quality",
            "display quality",
            "camera quality",
            "performance quality",
            "battery quality",
            "excellent quality",
        ],
        "Competitors": [
            "Samsung versus Apple",
            "Galaxy versus iPhone",
            "better than iPhone",
            "compared with Google Pixel",
            "competitor comparison",
            "competing smartphone",
        ],
        "Complaints": [
            "bad experience",
            "terrible experience",
            "very disappointed",
            "poor experience",
            "customer complaint",
            "user complaint",
            "phone does not work",
        ],
        "Features": [
            "new feature",
            "camera feature",
            "AI feature",
            "AirDrop support",
            "software feature",
            "new functionality",
        ],
        "Security": [
            "security vulnerability",
            "security issue",
            "data breach",
            "privacy issue",
            "security flaw",
            "hacking",
            "malware",
            "cyber attack",
        ],
        "Other": [
            "general discussion",
            "news article",
            "general information",
            "technology news",
            "other topic",
        ],
    }

    CONFIDENCE_THRESHOLD = 0.50

    DOMAIN_SIGNAL_BOOST = 0.10
    STRONG_SECURITY_BOOST = 0.20
    STRONG_COMPLAINT_BOOST = 0.10
    STRONG_COMPETITOR_BOOST = 0.15

    SECURITY_STRONG_SIGNALS = [
        "security vulnerability",
        "security flaw",
        "security breach",
        "data breach",
        "cyber attack",
        "cyberattack",
        "malware",
        "ransomware",
        "hack",
        "hacked",
        "hacking",
        "exploit",
        "exploited",
        "vulnerability",
    ]

    COMPLAINT_STRONG_SIGNALS = [
        "very disappointed",
        "extremely disappointed",
        "terrible experience",
        "awful experience",
        "worst experience",
        "customer complaint",
        "user complaint",
        "does not work",
        "doesn't work",
        "not working",
        "stopped working",
        "completely broken",
    ]

    QUALITY_CONTEXT_SIGNALS = [
        "quality",
        "display quality",
        "camera quality",
        "build quality",
        "screen quality",
        "audio quality",
        "performance quality",
    ]

    COMPETITOR_COMPARISON_SIGNALS = [
        "versus",
        "vs",
        "compared with",
        "compared to",
        "better than",
        "worse than",
        "competition",
        "competitor",
        "alternative to",
        "rival",
        "iphone",
        "google pixel",
        "pixel",
        "oneplus",
    ]

    PRICING_SIGNALS = [
        "price",
        "pricing",
        "cost",
        "discount",
        "deal",
        "sale",
        "cheap",
        "expensive",
        "offer",
        "₹",
        "$",
        "€",
        "£",
    ]

    CUSTOMER_SERVICE_SIGNALS = [
        "customer service",
        "customer support",
        "support team",
        "support agent",
        "service center",
        "service centre",
    ]

    FEATURE_SIGNALS = [
        "feature",
        "features",
        "functionality",
        "supports",
        "support for",
        "new capability",
        "capability",
    ]

    QUALITY_SIGNALS = [
        "quality",
        "build quality",
        "display quality",
        "camera quality",
        "battery quality",
        "screen quality",
        "performance",
    ]

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True,
        )

        self.topic_embeddings = self._build_topic_embeddings()

    def _build_topic_embeddings(self):
        """
        Build TF-IDF prototype vectors for every topic.
        """

        topics = list(self.TOPIC_EXAMPLES.keys())

        examples = []

        for topic in topics:
            examples.extend(
                self.TOPIC_EXAMPLES[topic]
            )

        matrix = self.vectorizer.fit_transform(
            examples
        )

        topic_embeddings = {}

        start = 0

        for topic in topics:
            count = len(
                self.TOPIC_EXAMPLES[topic]
            )

            topic_matrix = matrix[
                start:start + count
            ]

            prototype = topic_matrix.mean(
                axis=0
            )

            prototype = np.asarray(
                prototype
            ).ravel()

            norm = np.linalg.norm(prototype)

            if norm > 0:
                prototype = prototype / norm

            topic_embeddings[topic] = prototype

            start += count

        return topic_embeddings

    def analyze(self, text: str) -> dict:
        """
        Classify text into one of the configured topics.
        """

        if not text or not text.strip():
            return {
                "topic": "Other",
                "confidence": 0.0,
            }

        normalized_text = self._normalize_text(
            text
        )

        # ---------------------------------------------
        # Strong domain-specific signals
        # ---------------------------------------------

        security_match = self._contains_any(
            normalized_text,
            self.SECURITY_STRONG_SIGNALS,
        )

        complaint_match = self._contains_any(
            normalized_text,
            self.COMPLAINT_STRONG_SIGNALS,
        )

        competitor_match = self._contains_any(
            normalized_text,
            self.COMPETITOR_COMPARISON_SIGNALS,
        )

        quality_match = self._contains_any(
            normalized_text,
            self.QUALITY_CONTEXT_SIGNALS,
        )

        pricing_match = self._contains_any(
            normalized_text,
            self.PRICING_SIGNALS,
        )

        customer_service_match = self._contains_any(
            normalized_text,
            self.CUSTOMER_SERVICE_SIGNALS,
        )

        feature_match = self._contains_any(
            normalized_text,
            self.FEATURE_SIGNALS,
        )

        # ---------------------------------------------
        # Calculate TF-IDF similarity
        # ---------------------------------------------

        try:
            text_vector = self.vectorizer.transform(
                [normalized_text]
            )
        except ValueError:
            return {
                "topic": "Other",
                "confidence": 0.0,
            }

        scores = {}

        for topic, prototype in self.topic_embeddings.items():
            if not np.any(prototype):
                scores[topic] = 0.0
                continue

            similarity = cosine_similarity(
                text_vector,
                prototype.reshape(1, -1),
            )[0][0]

            scores[topic] = float(
                similarity
            )

        # ---------------------------------------------
        # Domain signal boosts
        # ---------------------------------------------

        if security_match:
            scores["Security"] = (
                scores.get("Security", 0.0)
                + self.STRONG_SECURITY_BOOST
            )

        if competitor_match:
            scores["Competitors"] = (
                scores.get("Competitors", 0.0)
                + self.STRONG_COMPETITOR_BOOST
            )

        if complaint_match:
            scores["Complaints"] = max(
                scores.get("Complaints", 0.0)
                + self.STRONG_COMPLAINT_BOOST,
                0.60,
            )

        if pricing_match:
            scores["Pricing"] = (
                scores.get("Pricing", 0.0)
                + self.DOMAIN_SIGNAL_BOOST
            )

        if customer_service_match:
            scores["Customer service"] = (
                scores.get(
                    "Customer service",
                    0.0,
                )
                + self.DOMAIN_SIGNAL_BOOST
            )

        if feature_match:
            scores["Features"] = (
                scores.get("Features", 0.0)
                + self.DOMAIN_SIGNAL_BOOST
            )

        # ---------------------------------------------
        # Quality should win over complaint for
        # quality-specific wording.
        # ---------------------------------------------

        if quality_match:
            scores["Quality"] = (
                scores.get("Quality", 0.0)
                + self.DOMAIN_SIGNAL_BOOST
            )

            # A sentence such as:
            # "The display quality is disappointing."
            # should remain Quality rather than becoming
            # Complaints.
            if "disappointing" in normalized_text:
                scores["Quality"] += 0.15

                scores["Complaints"] = min(
                    scores.get("Complaints", 0.0),
                    scores["Quality"] - 0.01,
                )

        # ---------------------------------------------
        # Strong signals should take priority.
        # ---------------------------------------------

        if security_match:
            return self._result(
                "Security",
                scores["Security"],
            )

        if competitor_match:
            return self._result(
                "Competitors",
                scores["Competitors"],
            )

        if pricing_match:
            return self._result(
                "Pricing",
                scores["Pricing"],
            )

        if customer_service_match:
            return self._result(
                "Customer service",
                scores["Customer service"],
            )

        if feature_match:
            return self._result(
                "Features",
                scores["Features"],
            )

        # ---------------------------------------------
        # Select strongest topic
        # ---------------------------------------------

        topic = max(
            scores,
            key=scores.get,
        )

        confidence = scores[topic]

        # Complaint only wins when it is genuinely
        # stronger than Quality.
        if (
            topic == "Complaints"
            and quality_match
        ):
            if scores.get("Quality", 0.0) >= confidence:
                topic = "Quality"
                confidence = scores["Quality"]

        if confidence < self.CONFIDENCE_THRESHOLD:
            return {
                "topic": "Other",
                "confidence": float(
                    confidence
                ),
            }

        return self._result(
            topic,
            confidence,
        )

    @staticmethod
    def _result(
        topic: str,
        confidence: float,
    ) -> dict:
        return {
            "topic": topic,
            "confidence": float(
                min(max(confidence, 0.0), 1.0)
            ),
        }

    @staticmethod
    def _normalize_text(text: str) -> str:
        text = text.lower()

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    @staticmethod
    def _contains_any(
        text: str,
        signals: list[str],
    ) -> bool:
        return any(
            signal.lower() in text
            for signal in signals
        )