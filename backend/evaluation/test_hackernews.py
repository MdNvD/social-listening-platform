from app.collectors.hackernews import HackerNewsCollector


collector = HackerNewsCollector()

mentions = collector.collect(
    keyword="AI",
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
    print("Engagement:", mention.engagement)
    print("Content:", mention.content[:300])