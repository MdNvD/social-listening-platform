from collections import Counter

from app.services.sentiment_service import SentimentService


# ==========================================================
# LABELED EVALUATION DATASET
# ==========================================================
#
# These are deliberately clear examples so we can first
# measure basic model behavior before testing harder cases.
#
# Labels:
# positive
# neutral
# negative
# ==========================================================

TEST_CASES = [
    # ------------------------------------------------------
    # POSITIVE
    # ------------------------------------------------------

    (
        "The Samsung Galaxy S26 has an excellent camera "
        "and the photos look amazing.",
        "positive",
    ),
    (
        "I love the Galaxy S26. The battery life is "
        "excellent and performance is very smooth.",
        "positive",
    ),
    (
        "The new update makes the phone faster and "
        "everything works perfectly.",
        "positive",
    ),
    (
        "This is a fantastic phone with a beautiful "
        "display and great performance.",
        "positive",
    ),
    (
        "The Galaxy S26 is much better than my previous "
        "phone. I am very happy with it.",
        "positive",
    ),

    # ------------------------------------------------------
    # NEGATIVE
    # ------------------------------------------------------

    (
        "The Galaxy S26 is far too expensive and the "
        "price is disappointing.",
        "negative",
    ),
    (
        "The battery life is terrible and the phone "
        "gets hot during normal use.",
        "negative",
    ),
    (
        "I regret buying the Galaxy S26. The camera "
        "quality is poor.",
        "negative",
    ),
    (
        "Samsung increased the price again and customers "
        "are unhappy about it.",
        "negative",
    ),
    (
        "The phone has serious performance problems and "
        "keeps freezing.",
        "negative",
    ),

    # ------------------------------------------------------
    # NEUTRAL
    # ------------------------------------------------------

    (
        "Samsung announced the Galaxy S26 today.",
        "neutral",
    ),
    (
        "The Galaxy S26 is available in three storage "
        "configurations.",
        "neutral",
    ),
    (
        "Samsung will release the update next month.",
        "neutral",
    ),
    (
        "The Galaxy S26 comes with a 6.7 inch display.",
        "neutral",
    ),
    (
        "The company has started selling the Galaxy S26 "
        "in India.",
        "neutral",
    ),
]


def calculate_metrics(
    y_true,
    y_pred,
    labels,
):
    """
    Calculate accuracy, precision, recall and F1
    without requiring an additional ML metrics package.
    """

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
    """
    Prints a confusion matrix.

    Rows    = actual
    Columns = predicted
    """

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

    header = (
        f"{'Actual':<12}"
        + "".join(
            f"{label:<12}"
            for label in labels
        )
    )

    print(header)
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
    print("SENTIMENT MODEL EVALUATION")
    print("=" * 80)

    print(
        "\nModel:"
        "\ncardiffnlp/"
        "twitter-roberta-base-sentiment-latest"
    )

    service = SentimentService()

    y_true = []
    y_pred = []

    labels = [
        "positive",
        "neutral",
        "negative",
    ]

    print("\n")
    print("=" * 80)
    print("INDIVIDUAL PREDICTIONS")
    print("=" * 80)

    for index, (text, expected) in enumerate(
        TEST_CASES,
        start=1,
    ):

        result = service.analyze(text)

        predicted = result["sentiment"]
        confidence = result["confidence"]

        y_true.append(expected)
        y_pred.append(predicted)

        status = (
            "PASS"
            if predicted == expected
            else "FAIL"
        )

        print("\n" + "-" * 80)

        print(
            f"[{index}] {status}"
        )

        print(
            f"Expected:   {expected}"
        )

        print(
            f"Predicted:  {predicted}"
        )

        print(
            f"Confidence: {confidence:.4f}"
        )

        print(
            f"Text: {text}"
        )

    # ------------------------------------------------------
    # METRICS
    # ------------------------------------------------------

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
    print("SENTIMENT METRICS")
    print("=" * 80)

    print(
        f"Accuracy: {accuracy:.4f}"
    )

    print()

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
        f"\nMacro F1: {macro_f1:.4f}"
    )

    # ------------------------------------------------------
    # CONFUSION MATRIX
    # ------------------------------------------------------

    print_confusion_matrix(
        y_true,
        y_pred,
        labels,
    )

    # ------------------------------------------------------
    # SUMMARY
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
    print("EVALUATION COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()