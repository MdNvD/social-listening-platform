from app.services.sentiment_service import SentimentService


class FakeClassifier:
    def __init__(self, label, score):
        self.label = label
        self.score = score

    def __call__(
        self,
        text,
        truncation=True,
        max_length=None,
    ):
        return [
            {
                "label": self.label,
                "score": self.score,
            }
        ]


def make_service(label, score):
    service = SentimentService.__new__(
        SentimentService
    )

    service.classifier = FakeClassifier(
        label,
        score,
    )

    return service


def test_empty_text_returns_neutral():
    service = make_service(
        "neutral",
        0.90,
    )

    result = service.analyze("")

    assert result["sentiment"] == "neutral"
    assert result["confidence"] == 0.0


def test_positive_model_prediction():
    service = make_service(
        "positive",
        0.95,
    )

    result = service.analyze(
        "The Samsung Galaxy S26 is excellent."
    )

    assert result["sentiment"] == "positive"
    assert result["confidence"] == 0.95


def test_negative_model_prediction():
    service = make_service(
        "negative",
        0.93,
    )

    result = service.analyze(
        "The phone has serious problems."
    )

    assert result["sentiment"] == "negative"
    assert result["confidence"] == 0.93


def test_neutral_with_negative_signal_becomes_negative():
    service = make_service(
        "neutral",
        0.70,
    )

    result = service.analyze(
        "Users reported a serious security vulnerability."
    )

    assert result["sentiment"] == "negative"
    assert result["confidence"] >= 0.60


def test_neutral_with_positive_signal_becomes_positive():
    service = make_service(
        "neutral",
        0.70,
    )

    result = service.analyze(
        "The new camera is excellent."
    )

    assert result["sentiment"] == "positive"
    assert result["confidence"] >= 0.60


def test_decisive_model_prediction_is_preserved():
    service = make_service(
        "positive",
        0.91,
    )

    result = service.analyze(
        "The product is excellent but has a security issue."
    )

    assert result["sentiment"] == "positive"
    assert result["confidence"] == 0.91