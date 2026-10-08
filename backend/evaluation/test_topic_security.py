from app.services.topic_service import TopicService


def main():

    service = TopicService()

    test_cases = [
        (
            "Google Pixel phones pwned in zero-click attacks",
            "Security",
        ),
        (
            "Google confirms Pixel phones exploited in targeted attack",
            "Security",
        ),
        (
            "Google Pixel Modems: possible permission bypass due to a logic error",
            "Security",
        ),
        (
            "The device has a critical security vulnerability",
            "Security",
        ),
        (
            "The Galaxy S26 has a new AI camera feature",
            "Features",
        ),
        (
            "Samsung increased the price of the Galaxy S26",
            "Pricing",
        ),
        (
            "I am extremely disappointed with my Galaxy S26",
            "Complaints",
        ),
        (
            "The Galaxy S26 is better than the iPhone",
            "Competitors",
        ),
        (
            "The Galaxy S26 has excellent build quality",
            "Quality",
        ),
    ]

    print("=" * 100)
    print("TOPIC SECURITY / DOMAIN TEST")
    print("=" * 100)

    passed = 0

    for index, (text, expected) in enumerate(
        test_cases,
        start=1,
    ):

        result = service.analyze(text)

        predicted = result["topic"]
        confidence = result["confidence"]

        success = (
            predicted == expected
        )

        if success:
            passed += 1

        status = (
            "PASS"
            if success
            else "FAIL"
        )

        print(
            f"[{index:02d}] {status} | "
            f"Expected: {expected:<18} | "
            f"Predicted: {predicted:<18} | "
            f"Confidence: {confidence:.4f}"
        )

        print(
            f"     {text}"
        )

    print("=" * 100)

    accuracy = (
        passed
        / len(test_cases)
        * 100
    )

    print(
        f"RESULT: {passed}/{len(test_cases)}"
    )

    print(
        f"Accuracy: {accuracy:.2f}%"
    )

    print("=" * 100)


if __name__ == "__main__":
    main()