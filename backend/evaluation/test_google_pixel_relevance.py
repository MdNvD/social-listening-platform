from app.collectors.models import CollectedMention
from app.services.relevance_service import RelevanceService


service = RelevanceService()


tests = [
    # =========================================================
    # SHOULD BE RELEVANT
    # =========================================================

    {
        "title": "Google Pixel 10 review",
        "content": (
            "The Google Pixel 10 has a strong camera "
            "and display."
        ),
        "expected": True,
    },

    {
        "title": "Google Pixel phones receive a major update",
        "content": (
            "Google Pixel phones received a major "
            "software update."
        ),
        "expected": True,
    },

    {
        "title": "Google Pixel Tablet gets new features",
        "content": (
            "The Google Pixel Tablet received several "
            "new features."
        ),
        "expected": True,
    },

    {
        "title": "Google Pixel phones exploited in attack",
        "content": (
            "Google Pixel phones were affected by "
            "a serious security issue."
        ),
        "expected": True,
    },

    {
        "title": "Google Pixel Tablet removed from store",
        "content": (
            "Google has removed the Pixel Tablet "
            "from its store."
        ),
        "expected": True,
    },

    # =========================================================
    # SHOULD NOT BE RELEVANT
    # =========================================================

    {
        "title": (
            "T-Mobile brings back its iconic referral "
            "discount, but there's a catch"
        ),
        "content": (
            "The T-Mobile logo is displayed on a "
            "Google Pixel phone. T-Mobile is offering "
            "a new referral discount."
        ),
        "expected": False,
    },

    {
        "title": (
            "Facer wants to end your endless search "
            "for the perfect Wear OS watch face"
        ),
        "content": (
            "Google Pixel Watch users can also use "
            "the redesigned watch face store."
        ),
        "expected": False,
    },

    {
        "title": (
            "Apple's rumored smart display is coming "
            "this month"
        ),
        "content": (
            "The report compares Apple's product with "
            "Google Pixel Tablet and Google Home."
        ),
        "expected": False,
    },

    {
        "title": (
            "Google announces new AI products"
        ),
        "content": (
            "Google announced several new products "
            "and services today."
        ),
        "expected": False,
    },
]


print()
print("=" * 90)
print("GOOGLE PIXEL RELEVANCE V2 EVALUATION")
print("=" * 90)

passed = 0


for index, test in enumerate(
    tests,
    start=1,
):

    mention = CollectedMention(
        source="test",
        source_id=str(index),
        url=f"https://example.com/{index}",
        title=test["title"],
        content=test["content"],
        author="test",
        published_at=None,
        keyword="Google Pixel",
        engagement=0,
    )

    score, relevant = service.analyze(
        mention
    )

    expected = test["expected"]

    success = (
        relevant == expected
    )

    if success:
        passed += 1

    print(
        f"{index:02d}. "
        f"{'PASS' if success else 'FAIL'} | "
        f"score={score:.4f} | "
        f"relevant={relevant} | "
        f"title={test['title']}"
    )


accuracy = (
    passed / len(tests)
) * 100


print("=" * 90)

print(
    f"RESULT: "
    f"{passed}/{len(tests)} tests passed"
)

print(
    f"Accuracy: {accuracy:.2f}%"
)

print("=" * 90)