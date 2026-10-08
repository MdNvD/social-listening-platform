from app.services.topic_service import TopicService


def main():
    service = TopicService()

    test_cases = [
        # Product
        {
            "text": "The Samsung Galaxy S26 has an excellent design and feels premium.",
            "expected": "Product",
        },
        {
            "text": "I really like the Galaxy S26 phone itself.",
            "expected": "Product",
        },

        # Pricing
        {
            "text": "The Samsung Galaxy S26 price is too expensive.",
            "expected": "Pricing",
        },
        {
            "text": "Samsung increased the price of the Galaxy S26.",
            "expected": "Pricing",
        },

        # Customer service
        {
            "text": "Samsung customer support took three days to respond to my issue.",
            "expected": "Customer service",
        },
        {
            "text": "The Samsung support team solved my problem quickly.",
            "expected": "Customer service",
        },

        # Quality
        {
            "text": "The Galaxy S26 battery quality is disappointing.",
            "expected": "Quality",
        },
        {
            "text": "The Galaxy S26 has excellent build quality and reliability.",
            "expected": "Quality",
        },

        # Competitors
        {
            "text": "The Galaxy S26 is being compared with the iPhone 17 Pro.",
            "expected": "Competitors",
        },
        {
            "text": "I would choose the Google Pixel instead of the Galaxy S26.",
            "expected": "Competitors",
        },

        # Complaints
        {
            "text": "I am very disappointed with my Galaxy S26 and Samsung needs to fix this problem.",
            "expected": "Complaints",
        },
        {
            "text": "My Galaxy S26 keeps freezing and I am unhappy with the phone.",
            "expected": "Complaints",
        },

        # Features
        {
            "text": "The Galaxy S26 has a new AI camera feature.",
            "expected": "Features",
        },
        {
            "text": "Samsung added new satellite connectivity features to the Galaxy S26.",
            "expected": "Features",
        },

        # Other
        {
            "text": "Samsung announced a Galaxy S26 launch event next week.",
            "expected": "Other",
        },
        {
            "text": "Samsung released a company announcement about its upcoming event.",
            "expected": "Other",
        },

        # Real-world cases from our pipeline
        {
            "text": "Samsung still glued to its bad habits with Galaxy S26 Ultra.",
            "expected": "Quality",
        },
        {
            "text": (
                "What would it take to enable non-protected VMs "
                "on the Snapdragon chip that ships on the Samsung S26 Ultra?"
            ),
            "expected": "Features",
        },
    ]

    print("=" * 100)
    print("TOPIC SERVICE CONTROLLED TEST")
    print("=" * 100)

    passed = 0

    results = []

    for index, case in enumerate(
        test_cases,
        start=1,
    ):

        result = service.analyze(
            case["text"]
        )

        predicted = result["topic"]
        confidence = result["confidence"]
        expected = case["expected"]

        test_passed = (
            predicted == expected
        )

        if test_passed:
            passed += 1

        status = (
            "PASS"
            if test_passed
            else "FAIL"
        )

        results.append(
            {
                "expected": expected,
                "predicted": predicted,
            }
        )

        print("\n" + "-" * 100)

        print(
            f"Test #{index}"
        )

        print(
            f"Text       : {case['text']}"
        )

        print(
            f"Expected   : {expected}"
        )

        print(
            f"Predicted  : {predicted}"
        )

        print(
            f"Confidence : {confidence:.4f}"
        )

        print(
            f"STATUS     : {status}"
        )

    total = len(test_cases)

    accuracy = (
        passed / total * 100
    )

    print("\n" + "=" * 100)
    print("TOPIC TEST SUMMARY")
    print("=" * 100)

    print(
        f"Passed   : {passed}/{total}"
    )

    print(
        f"Failed   : {total - passed}/{total}"
    )

    print(
        f"Accuracy : {accuracy:.2f}%"
    )

    print("=" * 100)

    print("\nConfusion Matrix:")
    print()

    labels = [
        "Product",
        "Pricing",
        "Customer service",
        "Quality",
        "Competitors",
        "Complaints",
        "Features",
        "Other",
    ]

    print(
        f"{'Actual':<20}",
        end="",
    )

    for label in labels:
        print(
            f"{label[:10]:>12}",
            end="",
        )

    print()

    for actual in labels:

        print(
            f"{actual:<20}",
            end="",
        )

        for predicted in labels:

            count = sum(
                1
                for result in results
                if result["expected"] == actual
                and result["predicted"] == predicted
            )

            print(
                f"{count:>12}",
                end="",
            )

        print()


if __name__ == "__main__":
    main()