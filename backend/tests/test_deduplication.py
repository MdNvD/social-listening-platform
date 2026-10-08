from app.services.deduplication_service import DeduplicationService
from app.collectors.models import CollectedMention


def make_mention(
    title,
    content,
    url="https://example.com/article",
    keyword="Samsung Galaxy S26",
):
    return CollectedMention(
        source="test",
        source_id="test-1",
        url=url,
        title=title,
        content=content,
        author=None,
        published_at=None,
        keyword=keyword,
        engagement=0,
    )


def test_same_url_is_duplicate():
    service = DeduplicationService.__new__(
        DeduplicationService
    )
    service.similarity_threshold = 0.82

    existing = make_mention(
        "Samsung Galaxy S26 review",
        "A detailed review of the Samsung Galaxy S26.",
        url="https://example.com/article?utm_source=test",
    )

    current = make_mention(
        "Different title",
        "Different content",
        url="https://example.com/article",
    )

    result = service.find_duplicate(
        current,
        [existing],
    )

    assert result == 0


def test_same_content_is_duplicate():
    service = DeduplicationService.__new__(
        DeduplicationService
    )
    service.similarity_threshold = 0.82

    existing = make_mention(
        "Samsung Galaxy S26 review",
        "Samsung Galaxy S26 has a powerful processor and excellent display.",
        url="https://example.com/first",
    )

    current = make_mention(
        "Another title",
        "Samsung Galaxy S26 has a powerful processor and excellent display.",
        url="https://example.com/second",
    )

    result = service.find_duplicate(
        current,
        [existing],
    )

    assert result == 0


def test_different_galaxy_models_are_not_duplicates():
    service = DeduplicationService.__new__(
        DeduplicationService
    )
    service.similarity_threshold = 0.82

    existing = make_mention(
        "Samsung Galaxy S25 review",
        "Samsung Galaxy S25 review and specifications.",
        url="https://example.com/s25",
    )

    current = make_mention(
        "Samsung Galaxy S26 review",
        "Samsung Galaxy S26 review and specifications.",
        url="https://example.com/s26",
    )

    result = service.find_duplicate(
        current,
        [existing],
    )

    assert result is None


def test_same_galaxy_model_is_not_model_conflict():
    first = make_mention(
        "Samsung Galaxy S26 review",
        "Samsung Galaxy S26 review.",
        url="https://example.com/first",
    )

    second = make_mention(
        "Samsung Galaxy S26 camera test",
        "Samsung Galaxy S26 camera performance.",
        url="https://example.com/second",
    )

    result = DeduplicationService._has_model_conflict(
        first,
        second,
    )

    assert result is False


def test_galaxy_model_extraction():
    text = (
        "Samsung Galaxy S26 Ultra and "
        "Samsung Galaxy S26 FE"
    )

    models = DeduplicationService._extract_galaxy_models(
        text
    )

    assert models == {"s26"}


def test_empty_existing_mentions_are_not_duplicate():
    service = DeduplicationService.__new__(
        DeduplicationService
    )
    service.similarity_threshold = 0.82

    current = make_mention(
        "Samsung Galaxy S26 review",
        "A detailed review of the Samsung Galaxy S26.",
    )

    result = service.find_duplicate(
        current,
        [],
    )

    assert result is None