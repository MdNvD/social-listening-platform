from app.collectors.models import CollectedMention
from app.services.relevance_service import (
    RelevanceService,
)


service = RelevanceService()


def make_mention(
    keyword,
    title,
    content="",
):
    return CollectedMention(
        source="test",
        source_id=None,
        url="https://example.com",
        title=title,
        content=content,
        author=None,
        published_at=None,
        keyword=keyword,
        engagement=0,
    )


def run_test(
    number,
    keyword,
    title,
    expected,
    content="",
):
    mention = make_mention(
        keyword=keyword,
        title=title,
        content=content,
    )

    score, relevant = (
        service.analyze(
            mention
        )
    )

    passed = (
        relevant == expected
    )

    print(
        f"{number:02d}. "
        f"{'PASS' if passed else 'FAIL'} | "
        f"score={score:.4f} | "
        f"relevant={relevant} | "
        f"title={title}"
    )

    return passed


tests = [

    # ---------------------------------------------------------
    # Google Pixel
    # ---------------------------------------------------------

    (
        "Google Pixel",
        "Google Pixel 10 review",
        True,
    ),

    (
        "Google Pixel",
        "Google Pixel phones receive a major update",
        True,
    ),

    (
        "Google Pixel",
        "Google Pixel Tablet gets new features",
        True,
    ),

    (
        "Google Pixel",
        "Google announces new AI products",
        False,
    ),

    (
        "Google Pixel",
        "Apple launches a new iPhone",
        False,
    ),

    (
        "Google Pixel",
        "T-Mobile brings back its iconic referral discount",
        False,
    ),

    (
        "Google Pixel",
        "Google announces new products while Pixel remains unchanged",
        True,
    ),

    # ---------------------------------------------------------
    # Samsung Galaxy S26
    # ---------------------------------------------------------

    (
        "Samsung Galaxy S26",
        "Samsung Galaxy S26 review",
        True,
    ),

    (
        "Samsung Galaxy S26",
        "Samsung Galaxy S26 Ultra gets a major camera update",
        True,
    ),

    (
        "Samsung Galaxy S26",
        "Samsung Galaxy S27 announced",
        False,
    ),

    (
        "Samsung Galaxy S26",
        "Samsung announces Galaxy S27 pricing",
        False,
    ),

    (
        "Samsung Galaxy S26",
        "Apple iPhone 17 review",
        False,
    ),

    # ---------------------------------------------------------
    # Pricing
    # ---------------------------------------------------------

    (
        "iPhone 17",
        "iPhone 17 price drops after launch",
        True,
    ),

    (
        "iPhone 17",
        "Google announces Pixel pricing",
        False,
    ),

    # ---------------------------------------------------------
    # Single keyword
    # ---------------------------------------------------------

    (
        "Tesla",
        "Tesla announces new vehicle",
        True,
    ),

    (
        "Tesla",
        "Apple announces a new MacBook",
        False,
    ),
]


passed = 0


print("\n")
print("=" * 90)
print("RELEVANCE V2 EVALUATION")
print("=" * 90)


for index, test in enumerate(
    tests,
    start=1,
):

    keyword = test[0]
    title = test[1]
    expected = test[2]

    if run_test(
        number=index,
        keyword=keyword,
        title=title,
        expected=expected,
    ):
        passed += 1


total = len(tests)

accuracy = (
    passed / total
) * 100


print("=" * 90)

print(
    f"RESULT: {passed}/{total} "
    f"tests passed"
)

print(
    f"Accuracy: {accuracy:.2f}%"
)

print("=" * 90)