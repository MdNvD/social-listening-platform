import numpy as np

from app.services.topic_service import TopicService


class FakeTopicModel:
    def __init__(self, vector):
        self.vector = np.array(vector, dtype=float)

    def encode(
        self,
        text,
        normalize_embeddings=True,
    ):
        if isinstance(text, list):
            return np.array(
                [self.vector for _ in text]
            )

        return self.vector


def make_service(topic_vector):
    service = TopicService.__new__(
        TopicService
    )

    service.model = FakeTopicModel(
        topic_vector
    )

    # Make Security the strongest topic by default.
    service.topic_embeddings = {
        "Product": np.array([0.0, 1.0]),
        "Pricing": np.array([0.0, 1.0]),
        "Customer service": np.array([0.0, 1.0]),
        "Quality": np.array([0.0, 1.0]),
        "Competitors": np.array([0.0, 1.0]),
        "Complaints": np.array([0.0, 1.0]),
        "Features": np.array([0.0, 1.0]),
        "Security": np.array([1.0, 0.0]),
        "Other": np.array([0.0, 1.0]),
    }

    return service


def test_empty_text_returns_other():
    service = make_service([1.0, 0.0])

    result = service.analyze("")

    assert result["topic"] == "Other"
    assert result["confidence"] == 0.0


def test_security_signal_is_classified_as_security():
    service = make_service([1.0, 0.0])

    result = service.analyze(
        "Researchers discovered a security vulnerability."
    )

    assert result["topic"] == "Security"
    assert result["confidence"] > 0.50


def test_pricing_signal_is_detected():
    service = make_service([0.0, 1.0])

    result = service.analyze(
        "The price of the phone increased significantly."
    )

    assert result["topic"] == "Pricing"
    assert result["confidence"] > 0.50


def test_competitor_comparison_signal_is_detected():
    service = make_service([0.0, 1.0])

    result = service.analyze(
        "The Galaxy S26 is better than the iPhone."
    )

    assert result["topic"] == "Competitors"
    assert result["confidence"] > 0.50


def test_complaint_signal_is_detected():
    service = make_service([0.0, 1.0])

    result = service.analyze(
        "I am very disappointed with this phone."
    )

    assert result["topic"] == "Complaints"
    assert result["confidence"] > 0.50


def test_quality_context_is_not_forced_into_complaints():
    service = make_service([0.0, 1.0])

    result = service.analyze(
        "The display quality is disappointing."
    )

    assert result["topic"] != "Complaints"