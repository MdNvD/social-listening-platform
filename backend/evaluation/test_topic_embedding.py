from sentence_transformers import SentenceTransformer
import numpy as np


MODEL_NAME = "all-MiniLM-L6-v2"

TOPIC_EXAMPLES = {
    "Product": [
        "The phone itself looks great.",
        "I like the design of the product.",
        "The smartphone feels comfortable to hold.",
        "I bought the Galaxy S26 and like the phone.",
        "The device has a premium design.",
    ],

    "Pricing": [
        "The phone is too expensive.",
        "The price of the Galaxy S26 is too high.",
        "Samsung increased the price.",
        "The phone is available at a discount.",
        "The product is affordable.",
        "The price dropped after the discount.",
    ],

    "Customer service": [
        "Samsung customer support helped me.",
        "The customer care team solved my problem.",
        "I contacted support about my issue.",
        "Customer service took three days to respond.",
        "The support representative was helpful.",
    ],

    "Quality": [
        "The camera quality is excellent.",
        "The display quality is disappointing.",
        "The phone has poor build quality.",
        "The battery quality is good.",
        "The device is reliable and well built.",
        "The phone overheats and has poor performance.",
    ],

    "Competitors": [
        "The Galaxy S26 is better than the iPhone.",
        "I would choose the Pixel instead.",
        "Samsung is competing with Apple.",
        "Compared with the iPhone, this phone is better.",
        "The Galaxy S26 competes with Google Pixel.",
    ],

    "Complaints": [
        "I am very disappointed with this phone.",
        "This phone keeps freezing and needs to be fixed.",
        "I am unhappy with the product.",
        "The phone stopped working after two weeks.",
        "Samsung needs to fix this problem.",
        "I have a serious problem with this product.",
    ],

    "Features": [
        "The phone has a new AI feature.",
        "Samsung added new camera features.",
        "The Galaxy S26 supports satellite connectivity.",
        "I like the new AI editing tools.",
        "The phone has a new camera mode.",
        "This device supports a new technology.",
    ],

    "Other": [
        "Samsung announced the launch event.",
        "The Galaxy S26 is available in India.",
        "Samsung released a company announcement.",
        "More information will be released next week.",
        "The company announced a new event.",
    ],
}


TEST_CASES = [
    (
        "The Galaxy S26 itself feels solid and has a premium design.",
        "Product",
    ),
    (
        "I bought the Galaxy S26 yesterday and the phone looks great in person.",
        "Product",
    ),
    (
        "The Galaxy S26 is Samsung's newest smartphone.",
        "Product",
    ),
    (
        "The phone feels comfortable to hold and the build quality is good.",
        "Product",
    ),

    (
        "The Galaxy S26 price is too high for what it offers.",
        "Pricing",
    ),
    (
        "Samsung increased the price of the Galaxy S26 by 17 percent.",
        "Pricing",
    ),
    (
        "The S26 is now available at a much lower price after the discount.",
        "Pricing",
    ),
    (
        "At Rs 99999, the Galaxy S26 is expensive.",
        "Pricing",
    ),

    (
        "Samsung customer support solved my problem quickly.",
        "Customer service",
    ),
    (
        "I contacted Samsung support and they helped me replace the defective phone.",
        "Customer service",
    ),
    (
        "The support team took three days to respond to my request.",
        "Customer service",
    ),
    (
        "Samsung's customer care team was very helpful.",
        "Customer service",
    ),

    (
        "The Galaxy S26 camera produces excellent image quality.",
        "Quality",
    ),
    (
        "The display quality is disappointing and has visible problems.",
        "Quality",
    ),
    (
        "The phone feels well built and the materials are high quality.",
        "Quality",
    ),
    (
        "Battery quality is poor and the phone overheats.",
        "Quality",
    ),

    (
        "The Galaxy S26 camera is better than the iPhone.",
        "Competitors",
    ),
    (
        "I would choose the Galaxy S26 over the Pixel.",
        "Competitors",
    ),
    (
        "Samsung needs to compete with Apple's latest iPhone.",
        "Competitors",
    ),
    (
        "Compared with the iPhone, the Galaxy S26 has better battery life.",
        "Competitors",
    ),

    (
        "I am extremely disappointed with my Galaxy S26.",
        "Complaints",
    ),
    (
        "This phone keeps freezing and I am tired of dealing with the problem.",
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

    (
        "Samsung announced the Galaxy S26 launch event for September 30.",
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


def main():

    print()
    print("=" * 100)
    print("TOPIC CLASSIFICATION - EMBEDDING BENCHMARK")
    print("=" * 100)

    print(f"\nModel: {MODEL_NAME}")

    print("\nLoading model...")

    model = SentenceTransformer(MODEL_NAME)

    topics = list(TOPIC_EXAMPLES.keys())

    # ------------------------------------------------------
    # Create topic prototype embeddings
    # ------------------------------------------------------

    print("\nCreating topic embeddings...")

    topic_embeddings = {}

    for topic in topics:

        examples = TOPIC_EXAMPLES[topic]

        embeddings = model.encode(
            examples,
            normalize_embeddings=True,
        )

        # Average all example embeddings for the topic.
        prototype = np.mean(
            embeddings,
            axis=0,
        )

        # Normalize prototype again.
        prototype = prototype / np.linalg.norm(
            prototype
        )

        topic_embeddings[topic] = prototype

    # ------------------------------------------------------
    # Evaluate
    # ------------------------------------------------------

    y_true = []
    y_pred = []

    failures = []

    print("\n")
    print("=" * 100)
    print("PREDICTIONS")
    print("=" * 100)

    for index, (text, expected) in enumerate(
        TEST_CASES,
        start=1,
    ):

        embedding = model.encode(
            text,
            normalize_embeddings=True,
        )

        scores = {}

        for topic in topics:

            score = float(
                np.dot(
                    embedding,
                    topic_embeddings[topic],
                )
            )

            scores[topic] = score

        predicted = max(
            scores,
            key=scores.get,
        )

        confidence = scores[predicted]

        y_true.append(expected)
        y_pred.append(predicted)

        passed = predicted == expected

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

        status = "PASS" if passed else "FAIL"

        print(
            f"[{index:02d}] "
            f"{status:<4} | "
            f"Expected: {expected:<18} | "
            f"Predicted: {predicted:<18} | "
            f"Similarity: {confidence:.4f}"
        )

        print(
            f"     {text}"
        )

    # ------------------------------------------------------
    # Metrics
    # ------------------------------------------------------

    total = len(y_true)

    correct = sum(
        actual == predicted
        for actual, predicted in zip(
            y_true,
            y_pred,
        )
    )

    accuracy = correct / total

    print("\n")
    print("=" * 100)
    print("TOPIC METRICS")
    print("=" * 100)

    print(
        f"Total examples: {total}"
    )

    print(
        f"Accuracy:       {accuracy:.4f}"
    )

    macro_f1_values = []

    for topic in topics:

        tp = sum(
            1
            for actual, predicted
            in zip(y_true, y_pred)
            if actual == topic
            and predicted == topic
        )

        fp = sum(
            1
            for actual, predicted
            in zip(y_true, y_pred)
            if actual != topic
            and predicted == topic
        )

        fn = sum(
            1
            for actual, predicted
            in zip(y_true, y_pred)
            if actual == topic
            and predicted != topic
        )

        precision = (
            tp / (tp + fp)
            if tp + fp
            else 0.0
        )

        recall = (
            tp / (tp + fn)
            if tp + fn
            else 0.0
        )

        f1 = (
            2 * precision * recall
            / (precision + recall)
            if precision + recall
            else 0.0
        )

        macro_f1_values.append(f1)

        print(
            f"{topic:<20} "
            f"Precision: {precision:.4f}  "
            f"Recall: {recall:.4f}  "
            f"F1: {f1:.4f}"
        )

    macro_f1 = sum(
        macro_f1_values
    ) / len(
        macro_f1_values
    )

    print(
        f"\nMacro F1:       {macro_f1:.4f}"
    )

    # ------------------------------------------------------
    # Confusion matrix
    # ------------------------------------------------------

    print("\n")
    print("=" * 100)
    print("CONFUSION MATRIX")
    print("=" * 100)

    matrix = {
        actual: {
            predicted: 0
            for predicted in topics
        }
        for actual in topics
    }

    for actual, predicted in zip(
        y_true,
        y_pred,
    ):
        matrix[actual][predicted] += 1

    print(
        f"{'Actual':<20}"
        + "".join(
            f"{topic:<20}"
            for topic in topics
        )
    )

    print("-" * 100)

    for actual in topics:

        row = f"{actual:<20}"

        for predicted in topics:

            row += (
                f"{matrix[actual][predicted]:<20}"
            )

        print(row)

    # ------------------------------------------------------
    # Failures
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
                f"Similarity: "
                f"{failure['confidence']:.4f}"
            )

            print(
                f"Text: "
                f"{failure['text']}"
            )

    print("\n")
    print("=" * 100)
    print("EMBEDDING BENCHMARK COMPLETED")
    print("=" * 100)


if __name__ == "__main__":
    main()