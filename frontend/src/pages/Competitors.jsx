import { useState } from "react";
import axios from "axios";

// =========================================================
// API
// =========================================================

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

// =========================================================
// Main Component
// =========================================================

function Competitors() {
  const [keywords, setKeywords] = useState(["", ""]);

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // =======================================================
  // Input handling
  // =======================================================

  const handleKeywordChange = (index, value) => {
    setKeywords((previous) => {
      const updated = [...previous];
      updated[index] = value;
      return updated;
    });
  };

  // =======================================================
  // Add competitor
  // =======================================================

  const addCompetitor = () => {
    if (keywords.length >= 5) {
      return;
    }

    setKeywords((previous) => [...previous, ""]);
  };

  // =======================================================
  // Remove competitor
  // =======================================================

  const removeCompetitor = (index) => {
    if (keywords.length <= 2) {
      return;
    }

    setKeywords((previous) =>
      previous.filter(
        (_, currentIndex) => currentIndex !== index
      )
    );
  };

  // =======================================================
  // Compare competitors
  // =======================================================

  const handleCompare = async (event) => {
    event.preventDefault();

    const cleanedKeywords = keywords
      .map((keyword) => keyword.trim())
      .filter(Boolean);

    // -------------------------------------------------------
    // Validation
    // -------------------------------------------------------

    if (cleanedKeywords.length < 2) {
      setError("Please enter at least 2 competitors.");
      return;
    }

    if (cleanedKeywords.length > 5) {
      setError("You can compare a maximum of 5 competitors.");
      return;
    }

    // Prevent duplicate competitor names
    const uniqueKeywords = new Set(
      cleanedKeywords.map((keyword) =>
        keyword.toLowerCase()
      )
    );

    if (uniqueKeywords.size !== cleanedKeywords.length) {
      setError("Please enter different competitors.");
      return;
    }

    // -------------------------------------------------------
    // API request
    // -------------------------------------------------------

    try {
      setLoading(true);
      setError("");
      setData(null);

      const response = await axios.post(
        `${API_BASE_URL}/api/competitors/compare`,
        {
          keywords: cleanedKeywords,
          limit_per_source: 10,
        }
      );

      setData(response.data);
    } catch (error) {
      console.error(
        "Competitor comparison error:",
        error
      );

      setError(
        error.response?.data?.detail ||
          error.message ||
          "Failed to compare competitors."
      );
    } finally {
      setLoading(false);
    }
  };

  // =======================================================
  // Loading
  // =======================================================

  if (loading) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center">
        <div className="text-center">
          <div
            className="
              mx-auto
              h-10
              w-10
              animate-spin
              rounded-full
              border-4
              border-slate-700
              border-t-blue-500
            "
          />

          <h2 className="mt-5 text-lg font-semibold text-white">
            Comparing competitors...
          </h2>

          <p className="mt-2 text-sm text-slate-400">
            Collecting and processing public mentions.
          </p>
        </div>
      </div>
    );
  }

  // =======================================================
  // Page
  // =======================================================

  return (
    <div className="space-y-6">

      {/* ===================================================
          Header
      ==================================================== */}

      <div>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-3xl font-bold text-white">
            Competitor Comparison
          </h1>

          <span
            className="
              rounded-full
              bg-blue-500/10
              px-3
              py-1
              text-xs
              font-medium
              text-blue-400
            "
          >
            Observed Data
          </span>
        </div>

        <p className="mt-2 text-sm text-slate-400">
          Compare mention volume, sentiment, topics,
          engagement, source coverage, and observed
          negative mentions.
        </p>

        <p className="mt-1 text-xs text-slate-600">
          Comparisons are based on the mentions collected
          by this platform and do not represent an overall
          ranking of the products or brands.
        </p>
      </div>

      {/* ===================================================
          Competitor Form
      ==================================================== */}

      <section
        className="
          rounded-xl
          border
          border-slate-800
          bg-slate-900
          p-6
        "
      >
        <div className="mb-5">
          <h2 className="text-lg font-semibold text-white">
            Select competitors
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Enter 2 to 5 brands, products, or keywords.
          </p>
        </div>

        <form
          onSubmit={handleCompare}
          className="space-y-4"
        >
          {keywords.map((keyword, index) => (
            <div
              key={index}
              className="flex gap-3"
            >
              <div className="flex-1">
                <label
                  className="
                    mb-2
                    block
                    text-xs
                    font-medium
                    uppercase
                    tracking-wide
                    text-slate-500
                  "
                >
                  Competitor {index + 1}
                </label>

                <input
                  type="text"
                  value={keyword}
                  onChange={(event) =>
                    handleKeywordChange(
                      index,
                      event.target.value
                    )
                  }
                  placeholder={
                    index === 0
                      ? "Samsung Galaxy S26"
                      : index === 1
                      ? "Google Pixel"
                      : "iPhone 17"
                  }
                  className="
                    w-full
                    rounded-lg
                    border
                    border-slate-700
                    bg-slate-950
                    px-4
                    py-3
                    text-sm
                    text-white
                    outline-none
                    transition
                    placeholder:text-slate-600
                    focus:border-blue-500
                  "
                />
              </div>

              {keywords.length > 2 && (
                <button
                  type="button"
                  onClick={() =>
                    removeCompetitor(index)
                  }
                  className="
                    mt-7
                    rounded-lg
                    border
                    border-red-900/50
                    px-4
                    text-sm
                    text-red-400
                    transition
                    hover:bg-red-950/40
                  "
                >
                  Remove
                </button>
              )}
            </div>
          ))}

          {/* Buttons */}

          <div className="flex flex-wrap gap-3 pt-2">
            {keywords.length < 5 && (
              <button
                type="button"
                onClick={addCompetitor}
                className="
                  rounded-lg
                  border
                  border-slate-700
                  px-4
                  py-2.5
                  text-sm
                  font-medium
                  text-slate-300
                  transition
                  hover:border-slate-600
                  hover:bg-slate-800
                "
              >
                + Add Competitor
              </button>
            )}

            <button
              type="submit"
              className="
                rounded-lg
                bg-blue-600
                px-5
                py-2.5
                text-sm
                font-semibold
                text-white
                transition
                hover:bg-blue-500
              "
            >
              Compare
            </button>
          </div>
        </form>

        {/* Error */}

        {error && (
          <div
            className="
              mt-5
              rounded-lg
              border
              border-red-900/50
              bg-red-950/30
              p-4
            "
          >
            <p className="text-sm text-red-400">
              {error}
            </p>
          </div>
        )}
      </section>

      {/* ===================================================
          Results
      ==================================================== */}

      {data && (
        <ComparisonResults
          competitors={data.competitors || []}
        />
      )}
    </div>
  );
}

// =========================================================
// Comparison Results
// =========================================================

function ComparisonResults({
  competitors,
}) {
  if (!competitors.length) {
    return (
      <div
        className="
          rounded-xl
          border
          border-slate-800
          bg-slate-900
          p-8
          text-center
        "
      >
        <p className="text-sm text-slate-500">
          No comparison data available.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">

      {/* =================================================
          Comparison Overview
      ================================================== */}

      <section>
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-white">
            Comparison Overview
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Metrics from the currently collected and
            processed mentions.
          </p>
        </div>

        <div
          className="
            grid
            gap-4
            md:grid-cols-2
            xl:grid-cols-3
          "
        >
          {competitors.map((competitor) => (
            <CompetitorCard
              key={competitor.search_id}
              competitor={competitor}
            />
          ))}
        </div>
      </section>

      {/* =================================================
          Sentiment Comparison
      ================================================== */}

      <section
        className="
          rounded-xl
          border
          border-slate-800
          bg-slate-900
          p-6
        "
      >
        <div className="mb-5">
          <h2 className="text-lg font-semibold text-white">
            Sentiment Distribution
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Counts of classified relevant mentions.
          </p>
        </div>

        <div
          className="
            grid
            gap-6
            md:grid-cols-2
            xl:grid-cols-3
          "
        >
          {competitors.map((competitor) => (
            <SentimentPanel
              key={competitor.search_id}
              competitor={competitor}
            />
          ))}
        </div>
      </section>

      {/* =================================================
          Topic Comparison
      ================================================== */}

      <section
        className="
          rounded-xl
          border
          border-slate-800
          bg-slate-900
          p-6
        "
      >
        <div className="mb-5">
          <h2 className="text-lg font-semibold text-white">
            Topic Distribution
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Topics identified across relevant mentions.
          </p>
        </div>

        <div className="space-y-6">
          {competitors.map((competitor) => (
            <TopicPanel
              key={competitor.search_id}
              competitor={competitor}
            />
          ))}
        </div>
      </section>

      {/* =================================================
          Source Comparison
      ================================================== */}

      <section
        className="
          rounded-xl
          border
          border-slate-800
          bg-slate-900
          p-6
        "
      >
        <div className="mb-5">
          <h2 className="text-lg font-semibold text-white">
            Source Distribution
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Sources represented in the relevant,
            non-duplicate mentions collected for each
            competitor.
          </p>
        </div>

        <div className="space-y-6">
          {competitors.map((competitor) => (
            <SourcePanel
              key={competitor.search_id}
              competitor={competitor}
            />
          ))}
        </div>
      </section>

      {/* =================================================
          Negative Mentions
      ================================================== */}

      <section>
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-white">
            Observed Negative Mentions
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Negative mentions identified by the sentiment
            pipeline. These are source-level observations,
            not independently verified claims.
          </p>
        </div>

        <div className="space-y-4">
          {competitors.map((competitor) => (
            <NegativeMentionsPanel
              key={competitor.search_id}
              competitor={competitor}
            />
          ))}
        </div>
      </section>
    </div>
  );
}

// =========================================================
// Competitor Card
// =========================================================

function CompetitorCard({
  competitor,
}) {
  const totalCollected =
    competitor.total_collected || 0;

  const totalMentions =
    competitor.total_mentions || 0;

  const totalEngagement =
    competitor.total_engagement || 0;

  return (
    <div
      className="
        rounded-xl
        border
        border-slate-800
        bg-slate-900
        p-5
      "
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">
            Competitor
          </p>

          <h3 className="mt-1 text-lg font-semibold text-white">
            {competitor.keyword}
          </h3>
        </div>

        <span
          className="
            rounded-md
            bg-slate-800
            px-2
            py-1
            text-xs
            text-slate-400
          "
        >
          Search #{competitor.search_id}
        </span>
      </div>

      <div className="mt-5 grid grid-cols-3 gap-3">
        <Metric
          label="Collected"
          value={totalCollected}
        />

        <Metric
          label="Relevant"
          value={totalMentions}
        />

        <Metric
          label="Engagement"
          value={totalEngagement}
        />
      </div>

      {totalCollected > 0 && (
        <p className="mt-4 text-xs text-slate-600">
          {totalMentions} relevant mention
          {totalMentions === 1 ? "" : "s"} from{" "}
          {totalCollected} collected candidate
          {totalCollected === 1 ? "" : "s"}.
        </p>
      )}
    </div>
  );
}

// =========================================================
// Metric
// =========================================================

function Metric({
  label,
  value,
}) {
  return (
    <div>
      <p className="text-xs text-slate-500">
        {label}
      </p>

      <p className="mt-1 text-xl font-bold text-white">
        {value}
      </p>
    </div>
  );
}

// =========================================================
// Sentiment Panel
// =========================================================

function SentimentPanel({
  competitor,
}) {
  const distribution =
    competitor.sentiment_distribution || [];

  const getCount = (sentiment) => {
    const item = distribution.find(
      (entry) =>
        entry.sentiment === sentiment
    );

    return item?.count || 0;
  };

  const positive = getCount("positive");
  const neutral = getCount("neutral");
  const negative = getCount("negative");

  const total =
    positive +
    neutral +
    negative;

  return (
    <div
      className="
        rounded-lg
        border
        border-slate-800
        bg-slate-950
        p-5
      "
    >
      <h3 className="font-semibold text-white">
        {competitor.keyword}
      </h3>

      {total === 0 ? (
        <EmptyState
          message="No relevant mentions were processed."
        />
      ) : (
        <div className="mt-5 space-y-4">
          <SentimentRow
            label="Positive"
            count={positive}
            total={total}
            className="text-green-400"
            barClass="bg-green-500"
          />

          <SentimentRow
            label="Neutral"
            count={neutral}
            total={total}
            className="text-slate-400"
            barClass="bg-slate-500"
          />

          <SentimentRow
            label="Negative"
            count={negative}
            total={total}
            className="text-red-400"
            barClass="bg-red-500"
          />
        </div>
      )}
    </div>
  );
}

// =========================================================
// Sentiment Row
// =========================================================

function SentimentRow({
  label,
  count,
  total,
  className,
  barClass,
}) {
  const percentage =
    total > 0
      ? Math.round(
          (count / total) * 100
        )
      : 0;

  return (
    <div>
      <div className="flex justify-between text-sm">
        <span className={className}>
          {label}
        </span>

        <span className="text-slate-500">
          {count} · {percentage}%
        </span>
      </div>

      <div
        className="
          mt-2
          h-2
          overflow-hidden
          rounded-full
          bg-slate-800
        "
      >
        <div
          className={`h-full ${barClass}`}
          style={{
            width: `${percentage}%`,
          }}
        />
      </div>
    </div>
  );
}

// =========================================================
// Topic Panel
// =========================================================

function TopicPanel({
  competitor,
}) {
  const topics =
    competitor.topic_distribution || [];

  return (
    <div
      className="
        rounded-lg
        border
        border-slate-800
        bg-slate-950
        p-5
      "
    >
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-white">
          {competitor.keyword}
        </h3>

        <span className="text-xs text-slate-600">
          {topics.length} topic
          {topics.length === 1 ? "" : "s"}
        </span>
      </div>

      {topics.length === 0 ? (
        <EmptyState
          message="No topic data available."
        />
      ) : (
        <div className="mt-4 flex flex-wrap gap-3">
          {topics.map((topic) => (
            <div
              key={topic.topic}
              className="
                rounded-lg
                border
                border-slate-800
                bg-slate-900
                px-4
                py-3
              "
            >
              <p className="text-sm font-medium text-slate-200">
                {topic.topic}
              </p>

              <p className="mt-1 text-xs text-slate-500">
                {topic.count} mention
                {topic.count === 1 ? "" : "s"}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// =========================================================
// Source Panel
// =========================================================

function SourcePanel({
  competitor,
}) {
  const sources =
    competitor.source_distribution || [];

  const total =
    sources.reduce(
      (sum, source) =>
        sum + (source.count || 0),
      0
    );

  return (
    <div
      className="
        rounded-lg
        border
        border-slate-800
        bg-slate-950
        p-5
      "
    >
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-white">
            {competitor.keyword}
          </h3>

          <p className="mt-1 text-xs text-slate-600">
            {sources.length} source
            {sources.length === 1 ? "" : "s"} ·{" "}
            {total} relevant mention
            {total === 1 ? "" : "s"}
          </p>
        </div>
      </div>

      {sources.length === 0 ? (
        <EmptyState
          message="No source data available."
        />
      ) : (
        <div className="mt-5 space-y-4">
          {sources.map((source) => (
            <SourceRow
              key={source.source}
              source={source.source}
              count={source.count}
              total={total}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// =========================================================
// Source Row
// =========================================================

function SourceRow({
  source,
  count,
  total,
}) {
  const percentage =
    total > 0
      ? Math.round(
          (count / total) * 100
        )
      : 0;

  return (
    <div>
      <div className="flex items-center justify-between gap-4">
        <span className="text-sm font-medium text-slate-300">
          {formatSource(source)}
        </span>

        <span className="text-xs text-slate-500">
          {count} · {percentage}%
        </span>
      </div>

      <div
        className="
          mt-2
          h-2
          overflow-hidden
          rounded-full
          bg-slate-800
        "
      >
        <div
          className="
            h-full
            rounded-full
            bg-blue-500
          "
          style={{
            width: `${percentage}%`,
          }}
        />
      </div>
    </div>
  );
}

// =========================================================
// Negative Mentions
// =========================================================

function NegativeMentionsPanel({
  competitor,
}) {
  const mentions =
    competitor.negative_mentions || [];

  return (
    <div
      className="
        rounded-xl
        border
        border-slate-800
        bg-slate-900
        p-5
      "
    >
      <div className="flex items-center justify-between gap-4">
        <div>
          <h3 className="font-semibold text-white">
            {competitor.keyword}
          </h3>

          <p className="mt-1 text-xs text-slate-500">
            {mentions.length} negative mention
            {mentions.length === 1
              ? ""
              : "s"} shown
          </p>
        </div>
      </div>

      {mentions.length === 0 ? (
        <EmptyState
          message="No negative mentions were identified."
        />
      ) : (
        <div className="mt-4 space-y-3">
          {mentions.map((mention) => (
            <div
              key={mention.id}
              className="
                rounded-lg
                border
                border-slate-800
                bg-slate-950
                p-4
              "
            >
              <div className="flex flex-wrap items-center gap-2">
                <span
                  className="
                    rounded-md
                    bg-red-500/10
                    px-2
                    py-1
                    text-xs
                    text-red-400
                  "
                >
                  Negative
                </span>

                <span
                  className="
                    rounded-md
                    bg-slate-800
                    px-2
                    py-1
                    text-xs
                    text-slate-400
                  "
                >
                  {formatSource(mention.source)}
                </span>

                {mention.topic && (
                  <span
                    className="
                      rounded-md
                      bg-slate-800
                      px-2
                      py-1
                      text-xs
                      text-slate-400
                    "
                  >
                    {mention.topic}
                  </span>
                )}
              </div>

              <h4 className="mt-3 text-sm font-medium text-slate-200">
                {mention.title ||
                  "Untitled mention"}
              </h4>

              {mention.sentiment_confidence != null && (
                <p className="mt-2 text-xs text-slate-600">
                  Sentiment confidence:{" "}
                  {Math.round(
                    mention.sentiment_confidence * 100
                  )}
                  %
                </p>
              )}

              {mention.url && (
                <a
                  href={mention.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="
                    mt-3
                    inline-flex
                    rounded-md
                    border
                    border-blue-500/30
                    px-3
                    py-1.5
                    text-xs
                    font-medium
                    text-blue-400
                    transition
                    hover:bg-blue-500/10
                  "
                >
                  View Original Source ↗
                </a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// =========================================================
// Empty State
// =========================================================

function EmptyState({
  message,
}) {
  return (
    <div
      className="
        mt-4
        rounded-lg
        border
        border-dashed
        border-slate-800
        p-5
        text-center
      "
    >
      <p className="text-sm text-slate-600">
        {message}
      </p>
    </div>
  );
}

// =========================================================
// Source formatter
// =========================================================

function formatSource(source) {
  const sourceNames = {
    rss: "RSS",
    hackernews: "Hacker News",
    stackexchange: "Stack Exchange",
    reddit: "Reddit",
  };

  return (
    sourceNames[source] ||
    source ||
    "Unknown"
  );
}

// =========================================================
// Export
// =========================================================

export default Competitors;