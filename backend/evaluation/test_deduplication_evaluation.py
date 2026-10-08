from app.collectors.models import CollectedMention
from app.services.deduplication_service import DeduplicationService


def create_mention(
    title: str,
    content: str,
    url: str,
):
    return CollectedMention(
        source="test",
        source_id=url,
        url=url,
        title=title,
        content=content,
        author=None,
        published_at=None,
        keyword="Samsung Galaxy S26",
        engagement=0,
    )


def run_test(
    service,
    name,
    first,
    second,
    expected_duplicate,
):
    result = service.find_duplicate(
        second,
        [first],
    )

    actual_duplicate = result is not None

    passed = (
        actual_duplicate
        == expected_duplicate
    )

    status = "PASS" if passed else "FAIL"

    print("\n" + "-" * 100)
    print(f"{status}: {name}")
    print(f"Expected duplicate : {expected_duplicate}")
    print(f"Actual duplicate   : {actual_duplicate}")

    if result is not None:
        print(f"Matched index      : {result}")

    print(f"First title        : {first.title}")
    print(f"Second title       : {second.title}")

    return passed


def main():

    print("\n")
    print("=" * 100)
    print("CONTROLLED DEDUPLICATION EVALUATION")
    print("=" * 100)

    service = DeduplicationService(
        similarity_threshold=0.82
    )

    tests = [

        # --------------------------------------------------
        # 1. Exact same URL
        # --------------------------------------------------

        (
            "Exact same URL",
            create_mention(
                "Samsung Galaxy S26 review",
                "The Galaxy S26 has a new camera and improved battery.",
                "https://example.com/article-1",
            ),
            create_mention(
                "Samsung Galaxy S26 review",
                "The Galaxy S26 has a new camera and improved battery.",
                "https://example.com/article-1",
            ),
            True,
        ),

        # --------------------------------------------------
        # 2. Same content, different URL
        # --------------------------------------------------

        (
            "Same content, different URL",
            create_mention(
                "Samsung Galaxy S26 review",
                "The Galaxy S26 has a new camera and improved battery.",
                "https://example.com/article-1",
            ),
            create_mention(
                "Galaxy S26 review",
                "The Galaxy S26 has a new camera and improved battery.",
                "https://example.com/article-2",
            ),
            True,
        ),

        # --------------------------------------------------
        # 3. Same story rewritten by another publisher
        # --------------------------------------------------

        (
            "Same story, rewritten article",
            create_mention(
                "Samsung Galaxy S26 price increased in India",
                "Samsung has increased the price of the Galaxy S26 in India by 17 percent.",
                "https://example.com/article-3",
            ),
            create_mention(
                "Galaxy S26 gets a price hike in India",
                "The Samsung Galaxy S26 is now more expensive in the Indian market after a 17 percent price increase.",
                "https://example.com/article-4",
            ),
            True,
        ),

        # --------------------------------------------------
        # 4. Related topic but different event
        # --------------------------------------------------

        (
            "Related topic, different event",
            create_mention(
                "Samsung Galaxy S26 price increased in India",
                "Samsung has increased the price of the Galaxy S26 in India by 17 percent.",
                "https://example.com/article-5",
            ),
            create_mention(
                "Samsung Galaxy S26 receives software update",
                "Samsung has released a new software update for the Galaxy S26 with security improvements.",
                "https://example.com/article-6",
            ),
            False,
        ),

        # --------------------------------------------------
        # 5. Similar product, different model
        # --------------------------------------------------

        (
            "Different Galaxy model",
            create_mention(
                "Samsung Galaxy S26 review",
                "The Galaxy S26 has excellent performance and battery life.",
                "https://example.com/article-7",
            ),
            create_mention(
                "Samsung Galaxy S25 review",
                "The Galaxy S25 has excellent performance and battery life.",
                "https://example.com/article-8",
            ),
            False,
        ),

        # --------------------------------------------------
        # 6. Completely different story
        # --------------------------------------------------

        (
            "Completely different article",
            create_mention(
                "Samsung Galaxy S26 camera review",
                "The Galaxy S26 camera produces detailed photos and excellent low-light images.",
                "https://example.com/article-9",
            ),
            create_mention(
                "Samsung opens new semiconductor facility",
                "Samsung announced plans to expand its semiconductor manufacturing operations.",
                "https://example.com/article-10",
            ),
            False,
        ),

        # --------------------------------------------------
        # 7. Same article with tracking parameters
        # --------------------------------------------------

        (
            "Same article with tracking parameters",
            create_mention(
                "Galaxy S26 review",
                "Samsung Galaxy S26 review with camera and battery testing.",
                "https://example.com/article-11",
            ),
            create_mention(
                "Galaxy S26 review",
                "Samsung Galaxy S26 review with camera and battery testing.",
                "https://example.com/article-11?utm_source=google&utm_medium=news",
            ),
            True,
        ),

        # --------------------------------------------------
        # 8. Two different pricing events
        # --------------------------------------------------

        (
            "Different pricing events",
            create_mention(
                "Galaxy S26 price hiked by 17 percent",
                "Samsung increased the Galaxy S26 price in India by up to 17 percent.",
                "https://example.com/article-12",
            ),
            create_mention(
                "Galaxy S26 price drops to lowest level",
                "The Samsung Galaxy S26 is now available at its lowest price following a major discount.",
                "https://example.com/article-13",
            ),
            False,
        ),
    ]

    passed = 0
    failed = 0

    for (
        name,
        first,
        second,
        expected,
    ) in tests:

        result = run_test(
            service,
            name,
            first,
            second,
            expected,
        )

        if result:
            passed += 1
        else:
            failed += 1

    # ------------------------------------------------------
    # Final result
    # ------------------------------------------------------

    print("\n")
    print("=" * 100)
    print("DEDUPLICATION EVALUATION SUMMARY")
    print("=" * 100)

    print(f"Total tests : {len(tests)}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")

    accuracy = (
        passed / len(tests)
    ) * 100

    print(
        f"Accuracy    : {accuracy:.2f}%"
    )

    print("=" * 100)


if __name__ == "__main__":
    main()