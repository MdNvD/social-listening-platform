from app.services.sentiment_service import SentimentService


def main():
    service = SentimentService()

    test_texts = [
        "The Samsung Galaxy S26 has an excellent camera and amazing performance.",
        "The Samsung Galaxy S26 price is too expensive.",
        "The Samsung Galaxy S26 was announced today.",
    ]

    for text in test_texts:
        result = service.analyze(text)

        print("\nText:")
        print(text)

        print("Result:")
        print(result)


if __name__ == "__main__":
    main()