from app.collectors.hackernews import HackerNewsCollector
from app.collectors.rss import RSSCollector
from app.services.ingestion_service import IngestionService


rss_feeds = [
    "https://news.google.com/rss/search?q=Samsung+Galaxy+S26&hl=en-IN&gl=IN&ceid=IN:en"
]

collectors = [
    RSSCollector(rss_feeds),
    HackerNewsCollector(),
]

service = IngestionService(collectors)

mentions = service.collect(
    keyword="Samsung Galaxy S26",
    limit_per_source=5,
)

print(f"\nTotal mentions collected: {len(mentions)}")

for mention in mentions:
    print("\n---")
    print("Source:", mention.source)
    print("Title:", mention.title)
    print("URL:", mention.url)
    print("Author:", mention.author)
    print("Published:", mention.published_at)
    print("Engagement:", mention.engagement)
    print("Content:", mention.content[:200])