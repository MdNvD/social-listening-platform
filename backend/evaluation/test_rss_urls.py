from app.collectors.rss import RSSCollector


def main():

    keyword = "Samsung Galaxy S26"

    feed_url = (
        "https://news.google.com/rss/search"
        f"?q={keyword.replace(' ', '+')}"
        "&hl=en-IN"
        "&gl=IN"
        "&ceid=IN:en"
    )

    collector = RSSCollector(
        feed_urls=[feed_url]
    )

    mentions = collector.collect(
        keyword=keyword,
        limit=5,
    )

    print("\n")
    print("=" * 100)
    print("RSS URL TEST")
    print("=" * 100)

    for index, mention in enumerate(
        mentions,
        start=1,
    ):

        print("\n" + "-" * 100)

        print(f"[{index}]")
        print(f"Title : {mention.title}")
        print(f"Source: {mention.source}")
        print(f"URL   : {mention.url}")

    print("\n")
    print("=" * 100)
    print("TEST COMPLETED")
    print("=" * 100)


if __name__ == "__main__":
    main()