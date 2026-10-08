from app.collectors.hackernews import HackerNewsCollector
from app.collectors.rss import RSSCollector
from app.services.ingestion_service import IngestionService
from app.services.normalization_service import NormalizationService


rss_feeds = [
    "https://news.google.com/rss/search?q=Samsung+Galaxy+S26&hl=en-IN&gl=IN&ceid=IN:en"
]

collectors = [
    RSSCollector(rss_feeds),
    HackerNewsCollector(),
]

ingestion_service = IngestionService(collectors)
normalization_service = NormalizationService()


mentions = ingestion_service.collect(
    keyword="Samsung Galaxy S26",
    limit_per_source=5,
)

print(f"\nCollected mentions: {len(mentions)}")

normalized_mentions = []

for mention in mentions:
    normalized = normalization_service.normalize(mention)

    if normalized is None:
        print("Skipped invalid mention")
        continue

    normalized_mentions.append(normalized)

print(
    f"Normalized mentions: "
    f"{len(normalized_mentions)}"
)

for mention in normalized_mentions:
    print("\n---")
    print("Source:", mention.source)
    print("Title:", mention.title)
    print("URL:", mention.url)
    print("Author:", mention.author)
    print("Published:", mention.published_at)
    print("Engagement:", mention.engagement)
    print("Content:", mention.content[:200])