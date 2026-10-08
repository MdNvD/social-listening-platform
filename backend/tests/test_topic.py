from app.services.topic_service import TopicService


def make_service():
    return TopicService()


def test_empty_text_returns_other():
    service = make_service()

    result = service.analyze("")

    assert result["topic"] == "Other"
    assert result["confidence"] == 0.0


def test_security_signal_is_classified_as_security():
    service = make_service()

    result = service.analyze(
        "Researchers discovered a security vulnerability."
    )

    assert result["topic"] == "Security"
    assert result["confidence"] > 0.50


def test_pricing_signal_is_detected():
    service = make_service()

    result = service.analyze(
        "The price of the phone increased significantly."
    )

    assert result["topic"] == "Pricing"
    assert result["confidence"] > 0.50


def test_competitor_comparison_signal_is_detected():
    service = make_service()

    result = service.analyze(
        "The Galaxy S26 is better than the iPhone."
    )

    assert result["topic"] == "Competitors"
    assert result["confidence"] > 0.50


def test_complaint_signal_is_detected():
    service = make_service()

    result = service.analyze(
        "I am very disappointed with this phone."
    )

    assert result["topic"] == "Complaints"
    assert result["confidence"] > 0.50


def test_quality_context_is_not_forced_into_complaints():
    service = make_service()

    result = service.analyze(
        "The display quality is disappointing."
    )

    assert result["topic"] == "Quality"
    assert result["topic"] != "Complaints"