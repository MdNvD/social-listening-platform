from app.services.search_service import SearchService


def main():
    keyword = "Samsung Galaxy S26"

    print("\n")
    print("=" * 80)
    print(f"RELEVANCE EVALUATION: {keyword}")
    print("=" * 80)

    service = SearchService()

    result = service.run_search(
        keyword=keyword,
        limit_per_source=5,
    )

    processed_mentions = result["processed_mentions"]

    print("\n")
    print("=" * 80)
    print("ALL COLLECTED CANDIDATES")
    print("=" * 80)

    for index, processed in enumerate(
        processed_mentions,
        start=1,
    ):
        mention = processed.mention

        status = (
            "RELEVANT"
            if processed.is_relevant
            else "IRRELEVANT"
        )

        if processed.is_duplicate:
            status = "DUPLICATE"

        print("\n" + "-" * 80)

        print(f"[{index}] {status}")

        print(f"Source: {mention.source}")

        print(f"Relevance score: {processed.relevance_score}")

        print(f"Title: {mention.title}")

        print(f"URL: {mention.url}")

        print(
            f"Content: "
            f"{mention.content[:300]}"
        )

    print("\n")
    print("=" * 80)
    print("PROCESSING STATISTICS")
    print("=" * 80)

    for key, value in result["statistics"].items():
        print(f"{key}: {value}")

    print("\n")
    print("=" * 80)
    print("EVALUATION COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()