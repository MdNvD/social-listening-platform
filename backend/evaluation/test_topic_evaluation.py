from collections import Counter

from app.services.topic_service import TopicService


# ==========================================================
# TOPIC EVALUATION DATASET
# ==========================================================
#
# Labels follow the categories specified in the assignment:
#
# Product
# Pricing
# Customer service
# Quality
# Competitors
# Complaints
# Features
# Other
#
# These examples are manually labeled so we can measure
# the zero-shot classifier before tuning it.
# ==========================================================

TEST_CASES = [

    # ------------------------------------------------------
    # PRODUCT
    # ------------------------------------------------------

    (
        "The Galaxy S26 itself feels solid and has a "
        "premium design.",
        "Product",
    ),

    (
        "I bought the Galaxy S26 yesterday and the phone "
        "looks great in person.",
        "Product",
    ),

    (
        "The Galaxy S26 is Samsung's newest smartphone.",
        "Product",
    ),

    (
        "The phone feels comfortable to hold and the "
        "build quality is good.",
        "Product",
    ),

    # ------------------------------------------------------
    # PRICING
    # ------------------------------------------------------

    (
        "The Galaxy S26 price is too high for what it offers.",
        "Pricing",
    ),

    (
        "Samsung increased the price of the Galaxy S26 "
        "by 17 percent.",
        "Pricing",
    ),

    (
        "The S26 is now available at a much lower price "
        "after the discount.",
        "Pricing",
    ),

    (
        "At Rs 99999, the Galaxy S26 is expensive.",
        "Pricing",
    ),

    # ------------------------------------------------------
    # CUSTOMER SERVICE
    # ------------------------------------------------------

    (
        "Samsung customer support solved my problem quickly.",
        "Customer service",
    ),

    (
        "I contacted Samsung support and they helped me "
        "replace the defective phone.",
        "Customer service",
    ),

    (
        "The support team took three days to respond to "
        "my request.",
        "Customer service",
    ),

    (
        "Samsung's customer care team was very helpful.",
        "Customer service",
    ),

    # ------------------------------------------------------
    # QUALITY
    # ------------------------------------------------------

    (
        "The Galaxy S26 camera produces excellent image "
        "quality.",
        "Quality",
    ),

    (
        "The display quality is disappointing and has "
        "visible problems.",
        "Quality",
    ),

    (
        "The phone feels well built and the materials "
        "are high quality.",
        "Quality",
    ),

    (
        "Battery quality is poor and the phone overheats.",
        "Quality",
    ),

    # ------------------------------------------------------
    # COMPETITORS
    # ------------------------------------------------------

    (
        "The Galaxy S26 camera is better than the iPhone.",
        "Competitors",
    ),

    (
        "I would choose the Galaxy S26 over the Pixel.",
        "Competitors",
    ),

    (
        "Samsung needs to compete with Apple's latest "
        "iPhone.",
        "Competitors",
    ),

    (
        "Compared with the iPhone, the Galaxy S26 has "
        "better battery life.",
        "Competitors",
    ),

    # ------------------------------------------------------
    # COMPLAINTS
    # ------------------------------------------------------

    (
        "I am extremely disappointed with my Galaxy S26.",
        "Complaints",
    ),

    (
        "This phone keeps freezing and I am tired of "
        "dealing with the problem.",
        "Complaints",
    ),

    (
        "Samsung needs to fix these terrible software bugs.",
        "Complaints",
    ),

    (
        "My Galaxy S26 stopped working after two weeks.",
        "Complaints",
    ),

    # ------------------------------------------------------
    # FEATURES
    # ------------------------------------------------------

    (
        "The Galaxy S26 has a new AI-powered camera feature.",
        "Features",
    ),

    (
        "Samsung added several new AI features to the S26.",
        "Features",
    ),

    (
        "The new Galaxy S26 supports satellite connectivity.",
        "Features",
    ),

    (
        "I like the new camera modes and AI editing tools.",
        "Features",
    ),

    # ------------------------------------------------------
    # OTHER
    # ------------------------------------------------------

    (
        "Samsung announced the Galaxy S26 launch event "
        "for September 30.",
        "Other",
    ),

    (
        "The Galaxy S26 is available in India starting today.",
        "Other",
    ),

    (
        "Samsung will release more information next week.",
        "Other",
    ),

    (
        "The company published a new announcement today.",
        "Other",
    ),
]


def calculate_metrics(
    y_true,
    y_pred,
    labels,
):
    total = len(y_true)

    correct = sum(
        true == predicted
        for true, predicted in zip(
            y_true,
            y_pred,
        )
    )

    accuracy = (
        correct / total
        if total
        else 0.0
    )

    metrics = {}

    for label in labels:

        true_positive = sum(
            1
            for true, predicted
            in zip(y_true, y_pred)
            if (
                true == label
                and predicted == label
            )
        )

        false_positive = sum(
            1
            for true, predicted
            in zip(y_true, y_pred)
            if (
                true != label
                and predicted == label
            )
        )

        false_negative = sum(
            1
            for true, predicted
            in zip(y_true, y_pred)
            if (
                true == label
                and predicted != label
            )
        )

        precision = (
            true_positive
            / (
                true_positive
                + false_positive
            )
            if (
                true_positive
                + false_positive
            )
            else 0.0
        )

        recall = (
            true_positive
            / (
                true_positive
                + false_negative
            )
            if (
                true_positive
                + false_negative
            )
            else 0.0
        )

        f1 = (
            2
            * precision
            * recall
            / (precision + recall)
            if (
                precision + recall
            )
            else 0.0
        )

        metrics[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }

    macro_f1 = (
        sum(
            metrics[label]["f1"]
            for label in labels
        )
        / len(labels)
    )

    return (
        accuracy,
        metrics,
        macro_f1,
    )


def print_confusion_matrix(
    y_true,
    y_pred,
    labels,
):
    matrix = {
        actual: {
            predicted: 0
            for predicted in labels
        }
        for actual in labels
    }

    for actual, predicted in zip(
        y_true,
        y_pred,
    ):
        matrix[actual][predicted] += 1

    print("\n")
    print("=" * 100)
    print("CONFUSION MATRIX")
    print("=" * 100)

    print(
        f"{'Actual':<20}"
        + "".join(
            f"{label:<20}"
            for label in labels
        )
    )

    print("-" * 100)

    for actual in labels:

        row = f"{actual:<20}"

        for predicted in labels:
            row += (
                f"{matrix[actual][predicted]:<20}"
            )

        print(row)


def main():

    print()
    print("=" * 100)
    print("TOPIC CLASSIFICATION EVALUATION")
    print("=" * 100)

    print(
        "\nModel:"
        "\nall-MiniLM-L6-v2"
    )

    service = TopicService()

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

    y_true = []
    y_pred = []

    failures = []

    for index, (text, expected) in enumerate(
        TEST_CASES,
        start=1,
    ):

        result = service.analyze(text)

        predicted = result["topic"]
        confidence = result["confidence"]

        y_true.append(expected)
        y_pred.append(predicted)

        passed = (
            predicted == expected
        )

        if not passed:
            failures.append(
                {
                    "index": index,
                    "text": text,
                    "expected": expected,
                    "predicted": predicted,
                    "confidence": confidence,
                }
            )

        status = (
            "PASS"
            if passed
            else "FAIL"
        )

        print(
            f"[{index:02d}] "
            f"{status:<4} | "
            f"Expected: {expected:<18} | "
            f"Predicted: {predicted:<18} | "
            f"Confidence: {confidence:.4f}"
        )

        print(
            f"     {text}"
        )

    (
        accuracy,
        metrics,
        macro_f1,
    ) = calculate_metrics(
        y_true,
        y_pred,
        labels,
    )

    print("\n")
    print("=" * 100)
    print("TOPIC METRICS")
    print("=" * 100)

    print(
        f"Total examples: {len(TEST_CASES)}"
    )

    print(
        f"Accuracy:       {accuracy:.4f}"
    )

    print()

    for label in labels:

        print(
            f"{label:<20} "
            f"Precision: "
            f"{metrics[label]['precision']:.4f}  "
            f"Recall: "
            f"{metrics[label]['recall']:.4f}  "
            f"F1: "
            f"{metrics[label]['f1']:.4f}"
        )

    print(
        f"\nMacro F1:       {macro_f1:.4f}"
    )

    print_confusion_matrix(
        y_true,
        y_pred,
        labels,
    )

    # ------------------------------------------------------
    # MISCLASSIFICATIONS
    # ------------------------------------------------------

    print("\n")
    print("=" * 100)
    print("MISCLASSIFIED EXAMPLES")
    print("=" * 100)

    if not failures:

        print(
            "No misclassified examples."
        )

    else:

        for failure in failures:

            print("\n" + "-" * 100)

            print(
                f"#{failure['index']}"
            )

            print(
                f"Expected:   "
                f"{failure['expected']}"
            )

            print(
                f"Predicted:  "
                f"{failure['predicted']}"
            )

            print(
                f"Confidence: "
                f"{failure['confidence']:.4f}"
            )

            print(
                f"Text: "
                f"{failure['text']}"
            )

    # ------------------------------------------------------
    # PREDICTION DISTRIBUTION
    # ------------------------------------------------------

    counts = Counter(y_pred)

    print("\n")
    print("=" * 100)
    print("PREDICTION DISTRIBUTION")
    print("=" * 100)

    for label in labels:

        print(
            f"{label:<20}: "
            f"{counts.get(label, 0)}"
        )

    print("\n")
    print("=" * 100)
    print("TOPIC EVALUATION COMPLETED")
    print("=" * 100)


if __name__ == "__main__":
    main()
