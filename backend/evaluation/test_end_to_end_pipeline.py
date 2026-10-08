from app.services.search_service import SearchService


def main():

    keyword = "Samsung Galaxy S26"

    print("\n")
    print("=" * 110)
    print("END-TO-END SOCIAL LISTENING PIPELINE")
    print("=" * 110)

    print(f"\nKeyword: {keyword}")

    service = SearchService()

    result = service.run_search(
        keyword=keyword,
        limit_per_source=5,
    )

    processed_mentions = result["processed_mentions"]

    # ------------------------------------------------------
    # PROCESSING SUMMARY
    # ------------------------------------------------------

    print("\n")
    print("=" * 110)
    print("PROCESSING SUMMARY")
    print("=" * 110)

    for key, value in result["statistics"].items():
        print(f"{key:<25}: {value}")

    # ------------------------------------------------------
    # ALL CANDIDATES
    # ------------------------------------------------------

    print("\n")
    print("=" * 110)
    print("MENTION ANALYSIS")
    print("=" * 110)

    for index, processed in enumerate(
        processed_mentions,
        start=1,
    ):

        mention = processed.mention

        print("\n" + "-" * 110)

        print(f"#{index}")

        print(
            f"Source              : "
            f"{mention.source}"
        )

        print(
            f"Title               : "
            f"{mention.title}"
        )

        print(
            f"URL                 : "
            f"{mention.url}"
        )

        print(
            f"Relevance score     : "
            f"{processed.relevance_score:.4f}"
        )

        print(
            f"Relevant            : "
            f"{processed.is_relevant}"
        )

        print(
            f"Duplicate           : "
            f"{processed.is_duplicate}"
        )

        if processed.duplicate_of is not None:

            print(
                f"Duplicate of       : "
                f"mention #{processed.duplicate_of}"
            )

        # --------------------------------------------------
        # NLP ANALYSIS
        # --------------------------------------------------

        if (
            processed.is_relevant
            and not processed.is_duplicate
        ):

            print(
                f"Sentiment           : "
                f"{processed.sentiment}"
            )

            print(
                f"Sentiment confidence: "
                f"{processed.sentiment_confidence:.4f}"
            )

            print(
                f"Topic               : "
                f"{processed.topic}"
            )

            print(
                f"Topic confidence    : "
                f"{processed.topic_confidence:.4f}"
            )

        else:

            print(
                "Sentiment           : "
                "not analyzed"
            )

            print(
                "Topic               : "
                "not analyzed"
            )

        print(
            f"Content             : "
            f"{mention.content[:500]}"
        )

    # ------------------------------------------------------
    # UNIQUE RELEVANT MENTIONS
    # ------------------------------------------------------

    unique_mentions = (
        service.processing_service
        .get_relevant_mentions(
            processed_mentions
        )
    )

    print("\n")
    print("=" * 110)
    print("UNIQUE RELEVANT MENTIONS")
    print("=" * 110)

    for index, processed in enumerate(
        unique_mentions,
        start=1,
    ):

        mention = processed.mention

        print("\n" + "-" * 110)

        print(
            f"[{index}] "
            f"{mention.source.upper()}"
        )

        print(
            f"Title: {mention.title}"
        )

        print(
            f"Sentiment: "
            f"{processed.sentiment} "
            f"({processed.sentiment_confidence:.4f})"
        )

        print(
            f"Topic: "
            f"{processed.topic} "
            f"({processed.topic_confidence:.4f})"
        )

        print(
            f"Relevance: "
            f"{processed.relevance_score:.4f}"
        )

        print(
            f"URL: "
            f"{mention.url}"
        )

    # ------------------------------------------------------
    # SENTIMENT DISTRIBUTION
    # ------------------------------------------------------

    sentiment_counts = {
        "positive": 0,
        "neutral": 0,
        "negative": 0,
    }

    topic_counts = {}

    for processed in unique_mentions:

        sentiment = processed.sentiment

        if sentiment in sentiment_counts:
            sentiment_counts[sentiment] += 1

        topic = processed.topic

        if topic:
            topic_counts[topic] = (
                topic_counts.get(topic, 0)
                + 1
            )

    print("\n")
    print("=" * 110)
    print("SENTIMENT DISTRIBUTION")
    print("=" * 110)

    for sentiment, count in sentiment_counts.items():

        print(
            f"{sentiment:<15}: "
            f"{count}"
        )

    # ------------------------------------------------------
    # TOPIC DISTRIBUTION
    # ------------------------------------------------------

    print("\n")
    print("=" * 110)
    print("TOPIC DISTRIBUTION")
    print("=" * 110)

    for topic, count in sorted(
        topic_counts.items(),
        key=lambda item: item[1],
        reverse=True,
    ):

        print(
            f"{topic:<25}: "
            f"{count}"
        )

    # ------------------------------------------------------
    # FINAL RESULT
    # ------------------------------------------------------

    print("\n")
    print("=" * 110)
    print("END-TO-END PIPELINE COMPLETED")
    print("=" * 110)

    print(
        "\nPipeline:"
    )

    print(
        "Collectors"
        " → Normalization"
        " → Relevance"
        " → Deduplication"
        " → Sentiment"
        " → Topic"
    )


if __name__ == "__main__":
    main()