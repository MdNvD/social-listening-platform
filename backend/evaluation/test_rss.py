from app.collectors.rss import RSSCollector


feed_urls = [
    "https://news.google.com/rss/search?q=Samsung+Galaxy+S26&hl=en-IN&gl=IN&ceid=IN:en"
]


collector = RSSCollector(feed_urls)

mentions = collector.collect(
    keyword="Samsung Galaxy S26",
    limit=10,
)

print(f"Collected {len(mentions)} mentions")

for mention in mentions:
    print("\n---")
    print("Source:", mention.source)
    print("Title:", mention.title)
    print("URL:", mention.url)
    print("Author:", mention.author)
    print("Published:", mention.published_at)
    print("Content:", mention.content[:200])