from collections import Counter

from app.services.sentiment_service import SentimentService


# ==========================================================
# HARDER SENTIMENT EVALUATION DATASET
# ==========================================================
#
# These examples are designed to be more realistic than the
# basic evaluation set.
#
# Categories:
# - factual announcements
# - price changes
# - mixed opinions
# - comparisons
# - complaints
# - praise
# - short social-media-style statements
#
# Labels are manually assigned for this evaluation set.
# ==========================================================

TEST_CASES = [

    # ------------------------------------------------------
    # FACTUAL / NEUTRAL
    # ------------------------------------------------------

    (
        "Samsung announced the Galaxy S26 launch event "
        "for September 30.",
        "neutral",
    ),

    (
        "The Galaxy S26 is available with 256GB and "
        "512GB storage options.",
        "neutral",
    ),

    (
        "Samsung released a software update for the "
        "Galaxy S26 this week.",
        "neutral",
    ),

    (
        "The Galaxy S26 starts at Rs 99999 in India.",
        "neutral",
    ),

    (
        "The phone comes with a 6.7-inch AMOLED display "
        "and a 5000mAh battery.",
        "neutral",
    ),

    # ------------------------------------------------------
    # POSITIVE
    # ------------------------------------------------------

    (
        "Honestly, the Galaxy S26 camera is incredible. "
        "The low-light photos are fantastic.",
        "positive",
    ),

    (
        "The latest update fixed the battery issue and "
        "the phone feels much better now.",
        "positive",
    ),

    (
        "I switched from an iPhone to the Galaxy S26 and "
        "I absolutely love it.",
        "positive",
    ),

    (
        "Samsung finally nailed the battery life on this "
        "generation.",
        "positive",
    ),

    (
        "Great performance, excellent display and a "
        "really smooth experience.",
        "positive",
    ),

    # ------------------------------------------------------
    # NEGATIVE
    # ------------------------------------------------------

    (
        "The Galaxy S26 price is ridiculous. There is no "
        "way it is worth that much money.",
        "negative",
    ),

    (
        "Battery life is awful after the latest update. "
        "I regret installing it.",
        "negative",
    ),

    (
        "Samsung keeps increasing prices while giving "
        "customers fewer improvements.",
        "negative",
    ),

    (
        "The phone overheats constantly and the "
        "performance becomes terrible.",
        "negative",
    ),

    (
        "Customer support refused to help me with a "
        "defective Galaxy S26.",
        "negative",
    ),

    # ------------------------------------------------------
    # MIXED
    # ------------------------------------------------------

    (
        "The camera is excellent, but the battery life "
        "is disappointing.",
        "negative",
    ),

    (
        "I love the display and performance, although "
        "the price is too high.",
        "negative",
    ),

    (
        "The phone is fast and the camera is good, but "
        "Samsung should have included a charger.",
        "positive",
    ),

    (
        "Great phone overall, but the software still has "
        "a few annoying bugs.",
        "positive",
    ),

    # ------------------------------------------------------
    # COMPARISONS
    # ------------------------------------------------------

    (
        "The Galaxy S26 is better than my old S24 and "
        "the battery lasts much longer.",
        "positive",
    ),

    (
        "I expected the S26 to be better than the iPhone, "
        "but the camera is actually worse.",
        "negative",
    ),

    (
        "Compared with the previous generation, the new "
        "model has a larger display.",
        "neutral",
    ),

    # ------------------------------------------------------
    # SHORT SOCIAL-MEDIA STYLE
    # ------------------------------------------------------

    (
        "S26 camera 🔥",
        "positive",
    ),

    (
        "Worst battery ever.",
        "negative",
    ),

    (
        "S26 launched today.",
        "neutral",
    ),

    (
        "Not bad, but nothing special.",
        "negative",
    ),

    (
        "Finally!!! Samsung got it right.",
        "positive",
    ),

    # ------------------------------------------------------
    # PRICE / COMMERCIAL CONTEXT
    # ------------------------------------------------------

    (
        "Galaxy S26 price increased by 17 percent in India.",
        "neutral",
    ),

    (
        "Galaxy S26 is now cheaper after the latest "
        "discount.",
        "positive",
    ),

    (
        "The discount looks good, but the phone is still "
        "too expensive.",
        "negative",
    ),

    # ------------------------------------------------------
    # CUSTOMER EXPERIENCE
    # ------------------------------------------------------

    (
        "Ordered the S26 yesterday and it arrived this "
        "morning. Everything was perfect.",
        "positive",
    ),

    (
        "My replacement request has been pending for "
        "three weeks. Terrible service.",
        "negative",
    ),

    (
        "I contacted Samsung support about the update "
        "and they provided the release date.",
        "neutral",
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
        for true, predicted
        in zip(y_true, y_pred)
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
            / (true_positive + false_positive)
            if (
                true_positive
                + false_positive
            )
            else 0.0
        )

        recall = (
            true_positive
            / (true_positive + false_negative)
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
            if precision + recall
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
    print("=" * 80)
    print("CONFUSION MATRIX")
    print("=" * 80)

    print(
        f"{'Actual':<12}"
        + "".join(
            f"{label:<12}"
            for label in labels
        )
    )

    print("-" * 80)

    for actual in labels:

        row = f"{actual:<12}"

        for predicted in labels:
            row += (
                f"{matrix[actual][predicted]:<12}"
            )

        print(row)


def main():

    print()
    print("=" * 80)
    print("HARD SENTIMENT EVALUATION")
    print("=" * 80)

    service = SentimentService()

    labels = [
        "positive",
        "neutral",
        "negative",
    ]

    y_true = []
    y_pred = []

    failures = []

    for index, (text, expected) in enumerate(
        TEST_CASES,
        start=1,
    ):

        result = service.analyze(text)

        predicted = result["sentiment"]
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
            f"Expected: {expected:<8} | "
            f"Predicted: {predicted:<8} | "
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
    print("=" * 80)
    print("HARD EVALUATION METRICS")
    print("=" * 80)

    print(
        f"Total examples: {len(TEST_CASES)}"
    )

    print(
        f"Accuracy:       {accuracy:.4f}"
    )

    for label in labels:

        print(
            f"{label.capitalize():<10} "
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
    # FAILURES
    # ------------------------------------------------------

    print("\n")
    print("=" * 80)
    print("MISCLASSIFIED EXAMPLES")
    print("=" * 80)

    if not failures:

        print(
            "No misclassified examples."
        )

    else:

        for failure in failures:

            print("\n" + "-" * 80)

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
    # DISTRIBUTION
    # ------------------------------------------------------

    counts = Counter(y_pred)

    print("\n")
    print("=" * 80)
    print("PREDICTION DISTRIBUTION")
    print("=" * 80)

    for label in labels:

        print(
            f"{label.capitalize():<10}: "
            f"{counts.get(label, 0)}"
        )

    print("\n")
    print("=" * 80)
    print("HARD EVALUATION COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()