from app.services.llm_service import LLMService


def main():
    service = LLMService()

    evidence = {
        "total_mentions": 4,
        "sentiment_distribution": [
            {
                "sentiment": "negative",
                "count": 3,
            },
            {
                "sentiment": "neutral",
                "count": 1,
            },
        ],
        "topic_distribution": [
            {
                "topic": "Security",
                "count": 3,
            },
            {
                "topic": "Other",
                "count": 1,
            },
        ],
        "representative_mentions": [
            {
                "id": 66,
                "title": "Google Pixel phones pwned in zero-click attacks",
                "content": "Google Pixel phones pwned in zero-click attacks",
                "source": "hackernews",
                "sentiment": "negative",
                "topic": "Security",
                "engagement": 21,
            },
            {
                "id": 67,
                "title": "Google Pixel Modems: There is a possible permission bypass due to a logic error",
                "content": "Google Pixel Modems: There is a possible permission bypass due to a logic error",
                "source": "hackernews",
                "sentiment": "negative",
                "topic": "Security",
                "engagement": 4,
            },
            {
                "id": 68,
                "title": "Google confirms Pixel phones exploited in targeted modem based attack",
                "content": "Google confirms Pixel phones exploited in targeted modem based attack",
                "source": "hackernews",
                "sentiment": "negative",
                "topic": "Security",
                "engagement": 4,
            },
            {
                "id": 69,
                "title": "Google has removed the Pixel Tablet from its store",
                "content": "Google has removed the Pixel Tablet from its store",
                "source": "hackernews",
                "sentiment": "neutral",
                "topic": "Other",
                "engagement": 1,
            },
        ],
    }

    result = service.generate_insights(
        keyword="Google Pixel",
        evidence=evidence,
    )

    print("\n" + "=" * 70)
    print("LLM INSIGHT TEST")
    print("=" * 70)

    print("\nSUMMARY:")
    print(result["summary"])

    print("\nKEY THEMES:")
    for theme in result["key_themes"]:
        print(theme)

    print("\nPAIN POINTS:")
    for pain_point in result["pain_points"]:
        print(pain_point)

    print("\nOPPORTUNITIES:")
    for opportunity in result["opportunities"]:
        print(opportunity)

    print("\nRECOMMENDED ACTIONS:")
    for action in result["recommended_actions"]:
        print("-", action)

    print("\nLIMITATIONS:")
    for limitation in result["limitations"]:
        print("-", limitation)

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()