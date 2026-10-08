from app.services.search_service import SearchService


def main():
    keyword = "Samsung Galaxy S26"

    service = SearchService()

    print(f"\nSearching for: {keyword}")
    print("=" * 60)

    result = service.run_search(
        keyword=keyword,
        limit_per_source=5,
    )

    print("\nPROCESSING STATISTICS")
    print("-" * 60)

    for key, value in result["statistics"].items():
        print(f"{key}: {value}")

    print("\nRELEVANT MENTIONS")
    print("-" * 60)

    for index, processed in enumerate(
        result["relevant_mentions"],
        start=1,
    ):
        mention = processed.mention

        print(f"\n[{index}] {mention.source}")
        print(f"Title: {mention.title}")
        print(f"URL: {mention.url}")
        print(f"Relevance: {processed.relevance_score}")
        print(f"Content: {mention.content[:300]}")

    print("\n" + "=" * 60)
    print("Search pipeline completed successfully.")


if __name__ == "__main__":
    main()