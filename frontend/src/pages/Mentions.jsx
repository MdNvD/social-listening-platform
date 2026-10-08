import { useEffect, useRef, useState } from "react";

import { getMentions } from "../services/api";
import { useSearch } from "../context/useSearch";

function Mentions() {
  // ---------------------------------------------------------
  // Active search
  // ---------------------------------------------------------

  const { activeSearch } = useSearch();

  const searchId = activeSearch?.id;

  // ---------------------------------------------------------
  // State
  // ---------------------------------------------------------

  const [mentions, setMentions] = useState([]);

  const [loading, setLoading] = useState(
    Boolean(searchId)
  );

  const [error, setError] = useState(null);

  const [page, setPage] = useState(1);

  const [pageSize] = useState(20);

  const [total, setTotal] = useState(0);

  const [totalPages, setTotalPages] = useState(0);

  const [reloadKey, setReloadKey] = useState(0);

  // ---------------------------------------------------------
  // Filters
  // ---------------------------------------------------------

  const [searchText, setSearchText] = useState("");

  const [source, setSource] = useState("");

  const [sentiment, setSentiment] = useState("");

  const [topic, setTopic] = useState("");

  const [startDate, setStartDate] = useState("");

  const [endDate, setEndDate] = useState("");

  // ---------------------------------------------------------
  // Request protection
  // ---------------------------------------------------------

  const requestIdRef = useRef(0);

  // ---------------------------------------------------------
  // Reset when active search changes
  // ---------------------------------------------------------

  useEffect(() => {
    const timer = setTimeout(() => {
      setPage(1);

      setMentions([]);

      setTotal(0);

      setTotalPages(0);

      setError(null);

      setSearchText("");

      setSource("");

      setSentiment("");

      setTopic("");

      setStartDate("");

      setEndDate("");

      setLoading(Boolean(searchId));
    }, 0);

    return () => {
      clearTimeout(timer);
    };
  }, [searchId]);

  // ---------------------------------------------------------
  // Load mentions
  //
  // Search text is debounced by 400ms.
  // Other filters load immediately.
  // ---------------------------------------------------------

  useEffect(() => {
    if (!searchId) {
      return;
    }

    const currentRequestId =
      ++requestIdRef.current;

    const timer = setTimeout(() => {
      const load = async () => {
        try {
          setLoading(true);

          setError(null);

          const params = {
            page,
            page_size: pageSize,
          };

          // -------------------------------------------------
          // Search text
          // -------------------------------------------------

          if (searchText.trim()) {
            params.search_text =
              searchText.trim();
          }

          // -------------------------------------------------
          // Source
          // -------------------------------------------------

          if (source) {
            params.source = source;
          }

          // -------------------------------------------------
          // Sentiment
          // -------------------------------------------------

          if (sentiment) {
            params.sentiment = sentiment;
          }

          // -------------------------------------------------
          // Topic
          // -------------------------------------------------

          if (topic) {
            params.topic = topic;
          }

          // -------------------------------------------------
          // Start date
          // -------------------------------------------------

          if (startDate) {
            params.start_date =
              `${startDate}T00:00:00`;
          }

          // -------------------------------------------------
          // End date
          // -------------------------------------------------

          if (endDate) {
            params.end_date =
              `${endDate}T23:59:59`;
          }

          const result =
            await getMentions(
              searchId,
              params
            );

          // -------------------------------------------------
          // Ignore stale response
          // -------------------------------------------------

          if (
            currentRequestId !==
            requestIdRef.current
          ) {
            return;
          }

          setMentions(
            result.items || []
          );

          setTotal(
            result.total || 0
          );

          setTotalPages(
            result.total_pages || 0
          );
        } catch (requestError) {
          // -----------------------------------------------
          // Ignore stale errors
          // -----------------------------------------------

          if (
            currentRequestId !==
            requestIdRef.current
          ) {
            return;
          }

          console.error(
            "Mentions loading error:",
            requestError
          );

          setError(
            requestError.response?.data?.detail ||
              requestError.message ||
              "Failed to load mentions."
          );
        } finally {
          if (
            currentRequestId ===
            requestIdRef.current
          ) {
            setLoading(false);
          }
        }
      };

      load();
    }, 400);

    // -------------------------------------------------------
    // Cancel debounce timer when dependencies change
    // -------------------------------------------------------

    return () => {
      clearTimeout(timer);
    };
  }, [
    searchId,
    page,
    pageSize,
    source,
    sentiment,
    topic,
    startDate,
    endDate,
    searchText,
    reloadKey,
  ]);

  // ---------------------------------------------------------
  // Reset filters
  // ---------------------------------------------------------

  const clearFilters = () => {
    setSearchText("");

    setSource("");

    setSentiment("");

    setTopic("");

    setStartDate("");

    setEndDate("");

    setPage(1);
  };

  // ---------------------------------------------------------
  // Change filter
  // ---------------------------------------------------------

  const handleFilterChange = (
    setter,
    value
  ) => {
    setter(value);

    setPage(1);
  };

  // ---------------------------------------------------------
  // Retry loading
  // ---------------------------------------------------------

  const handleRetry = () => {
    setError(null);

    setReloadKey(
      (value) => value + 1
    );
  };

  // ---------------------------------------------------------
  // No active search
  // ---------------------------------------------------------

  if (!searchId) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
        <h2 className="text-lg font-semibold text-white">
          No active search selected
        </h2>

        <p className="mt-2 text-sm text-slate-400">
          Return to the Dashboard and run a search first.
        </p>
      </div>
    );
  }

  // ---------------------------------------------------------
  // Loading state
  // ---------------------------------------------------------

  if (
    loading &&
    mentions.length === 0
  ) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-700 border-t-blue-500" />

          <p className="mt-4 text-sm text-slate-400">
            Loading mentions...
          </p>
        </div>
      </div>
    );
  }

  // ---------------------------------------------------------
  // Error state
  // ---------------------------------------------------------

  if (
    error &&
    mentions.length === 0
  ) {
    return (
      <div className="rounded-xl border border-red-900/50 bg-red-950/30 p-6">
        <h2 className="text-lg font-semibold text-red-400">
          Mentions Error
        </h2>

        <p className="mt-2 text-sm text-slate-300">
          {error}
        </p>

        <button
          type="button"
          onClick={handleRetry}
          className="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500"
        >
          Try again
        </button>
      </div>
    );
  }

  // ---------------------------------------------------------
  // Render
  // ---------------------------------------------------------

  return (
    <div className="space-y-6">
      {/* ===================================================
          Header
      =================================================== */}

      <div>
        <p className="text-sm font-medium text-blue-400">
          Social Listening
        </p>

        <h1 className="mt-1 text-3xl font-bold tracking-tight text-white">
          Mentions Explorer
        </h1>

        <p className="mt-2 text-sm text-slate-400">
          Search, filter, and inspect collected public mentions.
        </p>
      </div>

      {/* ===================================================
          Active Search
      =================================================== */}

      <div className="rounded-xl border border-slate-800 bg-slate-900 px-5 py-4">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
              Active search
            </p>

            <p className="mt-1 text-lg font-semibold text-white">
              {activeSearch?.keyword ||
                "No search selected"}
            </p>
          </div>

          <div className="text-sm text-slate-500">
            Search ID:{" "}
            <span className="font-medium text-slate-300">
              {searchId || "—"}
            </span>
          </div>
        </div>
      </div>

      {/* ===================================================
          Filters
      =================================================== */}

      <section className="rounded-xl border border-slate-800 bg-slate-900 p-5">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          {/* Search */}

          <div className="xl:col-span-2">
            <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500">
              Search
            </label>

            <input
              type="text"
              value={searchText}
              onChange={(event) =>
                handleFilterChange(
                  setSearchText,
                  event.target.value
                )
              }
              placeholder="Search mention title or content..."
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-blue-500"
            />
          </div>

          {/* Source */}

          <div>
            <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500">
              Source
            </label>

            <select
              value={source}
              onChange={(event) =>
                handleFilterChange(
                  setSource,
                  event.target.value
                )
              }
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none focus:border-blue-500"
            >
              <option value="">
                All sources
              </option>

              <option value="rss">
                RSS
              </option>

              <option value="hackernews">
                Hacker News
              </option>

              <option value="stackexchange">
                Stack Exchange
              </option>

              <option value="reddit">
                Reddit
              </option>
            </select>
          </div>

          {/* Sentiment */}

          <div>
            <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500">
              Sentiment
            </label>

            <select
              value={sentiment}
              onChange={(event) =>
                handleFilterChange(
                  setSentiment,
                  event.target.value
                )
              }
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none focus:border-blue-500"
            >
              <option value="">
                All sentiments
              </option>

              <option value="positive">
                Positive
              </option>

              <option value="neutral">
                Neutral
              </option>

              <option value="negative">
                Negative
              </option>
            </select>
          </div>

          {/* Topic */}

          <div>
            <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500">
              Topic
            </label>

            <select
              value={topic}
              onChange={(event) =>
                handleFilterChange(
                  setTopic,
                  event.target.value
                )
              }
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none focus:border-blue-500"
            >
              <option value="">
                All topics
              </option>

              <option value="Product">
                Product
              </option>

              <option value="Pricing">
                Pricing
              </option>

              <option value="Customer service">
                Customer service
              </option>

              <option value="Quality">
                Quality
              </option>

              <option value="Competitors">
                Competitors
              </option>

              <option value="Complaints">
                Complaints
              </option>

              <option value="Features">
                Features
              </option>

              <option value="Security">
                Security
              </option>

              <option value="Other">
                Other
              </option>
            </select>
          </div>

          {/* Start Date */}

          <div>
            <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500">
              From date
            </label>

            <input
              type="date"
              value={startDate}
              max={endDate || undefined}
              onChange={(event) =>
                handleFilterChange(
                  setStartDate,
                  event.target.value
                )
              }
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none focus:border-blue-500"
            />
          </div>

          {/* End Date */}

          <div>
            <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500">
              To date
            </label>

            <input
              type="date"
              value={endDate}
              min={startDate || undefined}
              onChange={(event) =>
                handleFilterChange(
                  setEndDate,
                  event.target.value
                )
              }
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {/* Filter footer */}

        <div className="mt-5 flex flex-col gap-3 border-t border-slate-800 pt-4 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-slate-500">
            {loading
              ? "Updating results..."
              : `${total} ${
                  total === 1
                    ? "mention"
                    : "mentions"
                } found`}
          </p>

          <button
            type="button"
            onClick={clearFilters}
            className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 transition hover:border-slate-600 hover:bg-slate-800 hover:text-white"
          >
            Clear filters
          </button>
        </div>
      </section>

      {/* ===================================================
          Refresh error
      =================================================== */}

      {error && (
        <div className="rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* ===================================================
          Results
      =================================================== */}

      <section className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900">
        <div className="border-b border-slate-800 px-6 py-5">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-lg font-semibold text-white">
                Collected Mentions
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Search ID: {searchId || "—"}
              </p>
            </div>

            {loading && (
              <span className="text-xs text-blue-400">
                Refreshing...
              </span>
            )}
          </div>
        </div>

        {/* =================================================
            Table
        ================================================= */}

        <div className="overflow-x-auto">
          <table className="w-full min-w-[1150px] text-left">
            <thead className="border-b border-slate-800 bg-slate-950/50">
              <tr>
                <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Source
                </th>

                <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Mention
                </th>

                <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Sentiment
                </th>

                <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Topic
                </th>

                <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Relevance
                </th>

                <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Date
                </th>

                <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Link
                </th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-800">
              {mentions.length === 0 ? (
                <tr>
                  <td
                    colSpan={7}
                    className="px-6 py-16 text-center"
                  >
                    <p className="text-sm font-medium text-slate-400">
                      No mentions found.
                    </p>

                    <p className="mt-1 text-xs text-slate-600">
                      Try changing or clearing your filters.
                    </p>
                  </td>
                </tr>
              ) : (
                mentions.map((mention) => (
                  <tr
                    key={mention.id}
                    className="transition hover:bg-slate-800/40"
                  >
                    {/* Source */}

                    <td className="px-6 py-5 align-top">
                      <span className="inline-flex rounded-md bg-slate-800 px-2.5 py-1 text-xs font-medium text-slate-300">
                        {formatSource(
                          mention.source
                        )}
                      </span>
                    </td>

                    {/* Mention */}

                    <td className="max-w-2xl px-6 py-5 align-top">
                      {mention.url ? (
                        <a
                          href={mention.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="line-clamp-2 text-sm font-semibold text-slate-200 hover:text-blue-400"
                        >
                          {mention.title ||
                            mention.content ||
                            "Untitled mention"}
                        </a>
                      ) : (
                        <p className="line-clamp-2 text-sm font-semibold text-slate-200">
                          {mention.title ||
                            mention.content ||
                            "Untitled mention"}
                        </p>
                      )}

                      {mention.content && (
                        <p className="mt-2 line-clamp-3 text-xs leading-5 text-slate-500">
                          {mention.content}
                        </p>
                      )}

                      {mention.author && (
                        <p className="mt-2 text-xs text-slate-600">
                          by {mention.author}
                        </p>
                      )}
                    </td>

                    {/* Sentiment */}

                    <td className="px-6 py-5 align-top">
                      <SentimentBadge
                        sentiment={
                          mention.sentiment
                        }
                      />

                      <p className="mt-2 text-xs text-slate-500">
                        Confidence:{" "}
                        {formatConfidence(
                          mention.sentiment_confidence
                        )}
                      </p>
                    </td>

                    {/* Topic */}

                    <td className="px-6 py-5 align-top">
                      <span className="text-sm text-slate-300">
                        {mention.topic ||
                          "Other"}
                      </span>

                      <p className="mt-2 text-xs text-slate-500">
                        Confidence:{" "}
                        {formatConfidence(
                          mention.topic_confidence
                        )}
                      </p>
                    </td>

                    {/* Relevance */}

                    <td className="px-6 py-5 align-top">
                      <ConfidenceBar
                        value={
                          mention.relevance_score
                        }
                      />
                    </td>

                    {/* Date */}

                    <td className="whitespace-nowrap px-6 py-5 align-top text-sm text-slate-500">
                      {formatDate(
                        mention.published_at
                      )}
                    </td>

                    {/* Link */}

                    <td className="px-6 py-5 align-top">
                      {mention.url ? (
                        <a
                          href={mention.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex rounded-lg border border-slate-700 px-3 py-2 text-xs font-medium text-slate-300 transition hover:border-blue-500 hover:text-blue-400"
                        >
                          View
                        </a>
                      ) : (
                        <span className="text-xs text-slate-600">
                          No link
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* =================================================
            Pagination
        ================================================= */}

        <div className="flex flex-col gap-3 border-t border-slate-800 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-slate-500">
            {total === 0 ? (
              "No results"
            ) : (
              <>
                Page{" "}
                <span className="font-medium text-slate-300">
                  {page}
                </span>{" "}
                of{" "}
                <span className="font-medium text-slate-300">
                  {totalPages}
                </span>
              </>
            )}
          </p>

          <div className="flex gap-2">
            <button
              type="button"
              disabled={
                page <= 1 ||
                loading ||
                totalPages === 0
              }
              onClick={() =>
                setPage(
                  (currentPage) =>
                    Math.max(
                      1,
                      currentPage - 1
                    )
                )
              }
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Previous
            </button>

            <button
              type="button"
              disabled={
                page >= totalPages ||
                loading ||
                totalPages === 0
              }
              onClick={() =>
                setPage(
                  (currentPage) =>
                    Math.min(
                      totalPages,
                      currentPage + 1
                    )
                )
              }
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>
      </section>
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

  if (!source) {
    return "Unknown";
  }

  return (
    sourceNames[source.toLowerCase()] ||
    source
  );
}

// =========================================================
// Sentiment badge
// =========================================================

function SentimentBadge({ sentiment }) {
  const styles = {
    positive:
      "bg-green-500/10 text-green-400 border-green-500/20",

    neutral:
      "bg-slate-500/10 text-slate-400 border-slate-500/20",

    negative:
      "bg-red-500/10 text-red-400 border-red-500/20",
  };

  return (
    <span
      className={`inline-flex rounded-md border px-2.5 py-1 text-xs font-medium capitalize ${
        styles[sentiment] ||
        styles.neutral
      }`}
    >
      {sentiment || "neutral"}
    </span>
  );
}

// =========================================================
// Confidence bar
// =========================================================

function ConfidenceBar({ value }) {
  const percentage = Math.max(
    0,
    Math.min(
      100,
      Math.round((value || 0) * 100)
    )
  );

  return (
    <div className="w-24">
      <div className="h-1.5 overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full rounded-full bg-blue-500 transition-all"
          style={{
            width: `${percentage}%`,
          }}
        />
      </div>

      <p className="mt-1 text-xs text-slate-500">
        {percentage}%
      </p>
    </div>
  );
}

// =========================================================
// Confidence formatter
// =========================================================

function formatConfidence(value) {
  if (
    value === null ||
    value === undefined
  ) {
    return "—";
  }

  return `${Math.round(
    value * 100
  )}%`;
}

// =========================================================
// Date formatter
// =========================================================

function formatDate(value) {
  if (!value) {
    return "Unknown";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Unknown";
  }

  return date.toLocaleDateString(
    "en-IN",
    {
      day: "2-digit",
      month: "short",
      year: "numeric",
    }
  );
}

export default Mentions;