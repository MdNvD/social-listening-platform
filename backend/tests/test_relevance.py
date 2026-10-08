from app.services.relevance_service import RelevanceService
from app.collectors.models import CollectedMention


def make_mention(keyword, title, content=""):
    return CollectedMention(
        source="test",
        source_id="test-1",
        url="https://example.com/test",
        title=title,
        content=content,
        author=None,
        published_at=None,
        keyword=keyword,
        engagement=0,
    )


def test_relevant_product_title():
    service = RelevanceService()

    mention = make_mention(
        "Samsung Galaxy S26",
        "Samsung Galaxy S26 review",
        "Here is our detailed review of the new phone.",
    )

    score, relevant = service.analyze(mention)

    assert relevant is True
    assert score >= 0.60


def test_relevant_google_pixel_title():
    service = RelevanceService()

    mention = make_mention(
        "Google Pixel",
        "Google Pixel phones receive a major update",
        "The latest update improves several Pixel devices.",
    )

    score, relevant = service.analyze(mention)

    assert relevant is True
    assert score >= 0.60


def test_wrong_samsung_model_is_irrelevant():
    service = RelevanceService()

    mention = make_mention(
        "Samsung Galaxy S26",
        "Samsung Galaxy S27 announced",
        "Samsung has announced its next Galaxy model.",
    )

    score, relevant = service.analyze(mention)

    assert relevant is False


def test_incidental_body_mention_is_irrelevant():
    service = RelevanceService()

    mention = make_mention(
        "Google Pixel",
        "T-Mobile brings back its iconic referral discount",
        "The article briefly mentions Google Pixel phones.",
    )

    score, relevant = service.analyze(mention)

    assert relevant is False


def test_empty_keyword_is_irrelevant():
    service = RelevanceService()

    mention = make_mention(
        "",
        "Some technology news",
        "This is a technology article.",
    )

    score, relevant = service.analyze(mention)

    assert score == 0.0
    assert relevant is False


def test_empty_content_and_title_are_irrelevant():
    service = RelevanceService()

    mention = make_mention(
        "Google Pixel",
        "",
        "",
    )

    score, relevant = service.analyze(mention)

    assert score == 0.0
    assert relevant is False