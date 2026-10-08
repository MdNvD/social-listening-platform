from app.services.sentiment_service import SentimentService


def main():

    service = SentimentService()

    test_cases = [
        (
            "Google Pixel phones pwned in zero-click attacks",
            "negative",
        ),
        (
            "Google confirms Pixel phones exploited in targeted attack",
            "negative",
        ),
        (
            "The phone has an excellent camera and impressive battery life",
            "positive",
        ),
        (
            "Google announced a new Pixel phone today",
            "neutral",
        ),
        (
            "The new update fixes a critical security flaw",
            "negative",
        ),
    ]

    print("=" * 90)
    print("SENTIMENT V2 TEST")
    print("=" * 90)

    passed = 0

    for index, (text, expected) in enumerate(
        test_cases,
        start=1,
    ):

        result = service.analyze(text)

        sentiment = result["sentiment"]
        confidence = result["confidence"]

        passed_test = (
            sentiment == expected
        )

        if passed_test:
            passed += 1

        status = "PASS" if passed_test else "FAIL"

        print(
            f"{index:02d}. {status} | "
            f"sentiment={sentiment} | "
            f"confidence={confidence:.4f} | "
            f"expected={expected}"
        )

        print(
            f"    {text}"
        )

    print("=" * 90)
    print(
        f"RESULT: {passed}/{len(test_cases)} tests passed"
    )

    accuracy = (
        passed / len(test_cases) * 100
    )

    print(
        f"Accuracy: {accuracy:.2f}%"
    )

    print("=" * 90)


if __name__ == "__main__":
    main()