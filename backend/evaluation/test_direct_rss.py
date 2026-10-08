import feedparser


def main():

    feed_url = "https://techcrunch.com/feed/"

    keyword = "AI"

    print("\n")
    print("=" * 100)
    print("DIRECT RSS FEED TEST")
    print("=" * 100)

    print(f"\nFeed: {feed_url}")
    print(f"Keyword: {keyword}")

    feed = feedparser.parse(feed_url)

    print(f"\nFeed title: {feed.feed.get('title', 'Unknown')}")
    print(f"Entries received: {len(feed.entries)}")

    matches = 0

    for entry in feed.entries:

        title = entry.get(
            "title",
            "",
        )

        summary = entry.get(
            "summary",
            "",
        )

        link = entry.get(
            "link",
            "",
        )

        searchable_text = (
            f"{title} {summary}"
            .lower()
        )

        if keyword.lower() not in searchable_text:
            continue

        matches += 1

        print("\n" + "-" * 100)

        print(f"Title: {title}")
        print(f"URL  : {link}")

        if matches >= 5:
            break

    print("\n")
    print("=" * 100)
    print(f"Matching articles: {matches}")
    print("=" * 100)


if __name__ == "__main__":
    main()