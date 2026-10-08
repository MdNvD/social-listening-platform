from app.collectors.stackexchange import (
    StackExchangeCollector,
)


collector = StackExchangeCollector()


results = collector.collect(
    keyword="Samsung Galaxy S26",
    limit=5,
)


print()
print("==============================")
print("STACK EXCHANGE TEST RESULTS")
print("==============================")


for result in results:

    print()
    print("Title:", result.title)
    print("Content:", result.content[:300])
    print("Author:", result.author)
    print("URL:", result.url)
    print("Engagement:", result.engagement)
    print("Published:", result.published_at)