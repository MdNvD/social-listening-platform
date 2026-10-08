from app.collectors.models import CollectedMention
from app.services.deduplication_service import (
    DeduplicationService,
)


def create_mention(
    title,
    content,
    url,
):
    return CollectedMention(
        source="test",
        source_id=None,
        url=url,
        title=title,
        content=content,
        author=None,
        published_at=None,
        keyword="Samsung Galaxy S26",
        engagement=0,
    )


def print_result(
    test_name,
    duplicate_index,
    expected,
):
    if duplicate_index is None:
        result = "UNIQUE"
    else:
        result = (
            f"DUPLICATE of mention "
            f"#{duplicate_index + 1}"
        )

    passed = (
        result == expected
        or (
            expected.startswith("DUPLICATE")
            and duplicate_index is not None
        )
    )

    status = "PASS" if passed else "FAIL"

    print(
        f"{status:>5} | "
        f"{test_name:<35} | "
        f"{result}"
    )


def main():

    print()
    print("=" * 80)
    print("DEDUPLICATION SERVICE TEST")
    print("=" * 80)

    service = DeduplicationService(
        similarity_threshold=0.88
    )

    # --------------------------------------------------
    # TEST 1
    # Exact same URL
    # --------------------------------------------------

    original = create_mention(
        title="Samsung Galaxy S26 price announced",
        content=(
            "Samsung Galaxy S26 price starts "
            "at Rs 1 lakh in India."
        ),
        url="https://example.com/article-1",
    )

    duplicate_url = create_mention(
        title="Samsung Galaxy S26 price announced",
        content=(
            "Samsung Galaxy S26 price starts "
            "at Rs 1 lakh in India."
        ),
        url="https://example.com/article-1",
    )

    existing = [original]

    duplicate_index = (
        service.find_duplicate(
            duplicate_url,
            existing,
        )
    )

    print_result(
        "Exact URL duplicate",
        duplicate_index,
        "DUPLICATE",
    )

    # --------------------------------------------------
    # TEST 2
    # Exact same content but different URL
    # --------------------------------------------------

    duplicate_content = create_mention(
        title="Samsung Galaxy S26 price update",
        content=(
            "Samsung Galaxy S26 price starts "
            "at Rs 1 lakh in India."
        ),
        url="https://another-site.com/article-99",
    )

    duplicate_index = (
        service.find_duplicate(
            duplicate_content,
            existing,
        )
    )

    print_result(
        "Exact content duplicate",
        duplicate_index,
        "DUPLICATE",
    )

    # --------------------------------------------------
    # TEST 3
    # Near-duplicate news article
    # --------------------------------------------------

    near_duplicate = create_mention(
        title=(
            "Samsung Galaxy S26 price starts "
            "above Rs 1 lakh in India"
        ),
        content=(
            "Samsung has increased the price "
            "of the Galaxy S26 in India. "
            "The base model now costs more than "
            "Rs 1 lakh."
        ),
        url="https://news-site.com/s26-price",
    )

    existing_news = [
        create_mention(
            title=(
                "Samsung Galaxy S26 price now "
                "above Rs 1 lakh in India"
            ),
            content=(
                "Samsung Galaxy S26 price has "
                "increased in India. The base model "
                "now costs more than Rs 1 lakh."
            ),
            url="https://different-news.com/s26",
        )
    ]

    duplicate_index = (
        service.find_duplicate(
            near_duplicate,
            existing_news,
        )
    )

    print_result(
        "Near-duplicate news article",
        duplicate_index,
        "DUPLICATE",
    )

    # --------------------------------------------------
    # TEST 4
    # Clearly different article
    # --------------------------------------------------

    different_article = create_mention(
        title=(
            "Samsung Galaxy S26 receives "
            "One UI software update"
        ),
        content=(
            "Samsung has started rolling out "
            "a new software update to Galaxy S26 "
            "devices in several countries."
        ),
        url="https://example.com/software-update",
    )

    duplicate_index = (
        service.find_duplicate(
            different_article,
            existing_news,
        )
    )

    print_result(
        "Clearly different article",
        duplicate_index,
        "UNIQUE",
    )

    # --------------------------------------------------
    # TEST 5
    # Tracking parameters in URL
    # --------------------------------------------------

    tracking_original = create_mention(
        title="Galaxy S26 review",
        content="Samsung Galaxy S26 review.",
        url=(
            "https://example.com/review"
            "?utm_source=google"
        ),
    )

    tracking_duplicate = create_mention(
        title="Galaxy S26 review",
        content="Samsung Galaxy S26 review.",
        url=(
            "https://example.com/review"
            "?utm_source=twitter"
        ),
    )

    duplicate_index = (
        service.find_duplicate(
            tracking_duplicate,
            [tracking_original],
        )
    )

    print_result(
        "URL tracking parameter duplicate",
        duplicate_index,
        "DUPLICATE",
    )

    print()
    print("=" * 80)
    print("DEDUPLICATION TEST COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()