from app.services.sentiment_service import SentimentService


def make_service():
    return SentimentService()


def test_empty_text_returns_neutral():
    service = make_service()

    result = service.analyze("")

    assert result["sentiment"] == "neutral"
    assert result["confidence"] == 0.0


def test_positive_sentiment_is_detected():
    service = make_service()

    result = service.analyze(
        "The Samsung Galaxy S26 is excellent."
    )

    assert result["sentiment"] == "positive"
    assert result["confidence"] >= 0.60


def test_negative_sentiment_is_detected():
    service = make_service()

    result = service.analyze(
        "The phone has serious problems."
    )

    assert result["sentiment"] == "negative"
    assert result["confidence"] >= 0.60


def test_negative_security_signal_is_detected():
    service = make_service()

    result = service.analyze(
        "Users reported a serious security vulnerability."
    )

    assert result["sentiment"] == "negative"
    assert result["confidence"] >= 0.60


def test_positive_signal_is_detected():
    service = make_service()

    result = service.analyze(
        "The new camera is excellent."
    )

    assert result["sentiment"] == "positive"
    assert result["confidence"] >= 0.60


def test_strong_positive_signal_can_outweigh_negative_signal():
    service = make_service()

    result = service.analyze(
        "The product is excellent but has a minor issue."
    )

    assert result["sentiment"] == "positive"
    assert result["confidence"] >= 0.60


def test_equal_positive_and_negative_signals_are_neutral():
    service = make_service()

    result = service.analyze(
        "The phone is excellent but has a serious problem."
    )

    assert result["sentiment"] == "neutral"
    assert result["confidence"] == 0.50