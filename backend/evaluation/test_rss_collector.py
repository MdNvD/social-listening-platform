from app.collectors.rss import RSSCollector


def main():

    print("=" * 100)
    print("RSS CANDIDATE COLLECTION TEST")
    print("=" * 100)

    feeds = [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://feeds.arstechnica.com/arstechnica/index",
        "http://feed.androidauthority.com/",
    ]

    collector = RSSCollector(
        feed_urls=feeds
    )

    keyword = "Samsung Galaxy S26"

    print(
        f"\nKeyword: {keyword}"
    )

    print(
        f"Feeds: {len(feeds)}"
    )

    mentions = collector.collect(
        keyword=keyword,
        limit=20,
    )

    print("\n" + "=" * 100)

    print(
        f"RSS CANDIDATES: {len(mentions)}"
    )

    print("=" * 100)

    for index, mention in enumerate(
        mentions,
        start=1,
    ):

        print(
            "\n" + "-" * 100
        )

        print(
            f"#{index}"
        )

        print(
            f"Source    : {mention.source}"
        )

        print(
            f"Title     : {mention.title}"
        )

        print(
            f"URL       : {mention.url}"
        )

        print(
            f"Published : {mention.published_at}"
        )

        print(
            f"Content   : "
            f"{mention.content[:500]}"
        )

    print(
        "\n" + "=" * 100
    )

    if mentions:

        print(
            "RSS STATUS: "
            "CANDIDATE COLLECTION WORKING"
        )

    else:

        print(
            "RSS STATUS: "
            "NO CURRENT MATCHING CANDIDATES"
        )

    print("=" * 100)


if __name__ == "__main__":
    main()