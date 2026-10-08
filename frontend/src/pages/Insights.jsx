import { useEffect, useState } from "react";
import axios from "axios";
import { useSearch } from "../context/useSearch";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

// ============================================================
// Evidence badge
// ============================================================

function EvidenceBadge({ id }) {
  return (
    <span className="rounded-md bg-slate-800 px-2 py-1 text-xs text-slate-300">
      Evidence #{id}
    </span>
  );
}

// ============================================================
// Source formatter
// ============================================================

function formatSource(source) {
  const sourceNames = {
    rss: "RSS",
    hackernews: "Hacker News",
    stackexchange: "Stack Exchange",
    reddit: "Reddit",
  };

  return sourceNames[source] || source || "Unknown";
}

// ============================================================
// Safe text helper
// ============================================================

function getText(value, fallback = "") {
  if (value === null || value === undefined) {
    return fallback;
  }

  if (typeof value === "string") {
    return value;
  }

  return String(value);
}

// ============================================================
// Main component
// ============================================================

function Insights() {
  const { activeSearch } = useSearch();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(
    Boolean(activeSearch?.id)
  );
  const [error, setError] = useState("");

  // ==========================================================
  // Load insights
  // ==========================================================

  useEffect(() => {
    if (!activeSearch?.id) {
      return;
    }

    let cancelled = false;

    async function loadInsights() {
      try {
        setLoading(true);
        setError("");

        const response = await axios.get(
          `${API_BASE_URL}/api/searches/${activeSearch.id}/insights`
        );

        if (cancelled) {
          return;
        }

        console.log(
          "[Insights] API response:",
          response.data
        );

        setData(response.data);
      } catch (err) {
        console.error(
          "Failed to load AI insights:",
          err
        );

        if (!cancelled) {
          setError(
            err.response?.data?.detail ||
              "Failed to load AI insights."
          );

          setData(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadInsights();

    return () => {
      cancelled = true;
    };
  }, [activeSearch?.id]);

  // ==========================================================
  // No active search
  // ==========================================================

  if (!activeSearch?.id) {
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

  // ==========================================================
  // Loading
  // ==========================================================

  if (loading) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
        <div className="flex items-center gap-3">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-slate-600 border-t-blue-400" />

          <div>
            <h2 className="text-lg font-semibold text-white">
              Generating AI insights
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Analyzing the collected mentions and evidence...
            </p>
          </div>
        </div>
      </div>
    );
  }

  // ==========================================================
  // Error
  // ==========================================================

  if (error) {
    return (
      <div className="rounded-xl border border-red-900/50 bg-red-950/20 p-6">
        <h2 className="text-lg font-semibold text-red-300">
          Failed to load AI insights
        </h2>

        <p className="mt-2 text-sm text-red-200">
          {error}
        </p>
      </div>
    );
  }

  // ==========================================================
  // No response
  // ==========================================================

  if (!data) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
        <h2 className="text-lg font-semibold text-white">
          No insights available
        </h2>

        <p className="mt-2 text-sm text-slate-400">
          There is currently no insight data available for
          this search.
        </p>
      </div>
    );
  }

  // ==========================================================
  // IMPORTANT:
  //
  // Backend response is:
  //
  // data
  // ├── evidence
  // └── ai_insights
  //
  // We must read those nested objects.
  // ==========================================================

  const evidence = data.evidence || {};

  const aiInsights = data.ai_insights || {};

  // ==========================================================
  // Evidence data
  // ==========================================================

  const totalEvidence = Number(
    evidence.total_mentions || 0
  );

  const relevantEvidence = totalEvidence;

  const searchCount = Number(
    evidence.search_count || 0
  );

  const negativeMentionCount = Number(
    evidence.negative_mention_count || 0
  );

  const searchIds = Array.isArray(
    evidence.search_ids
  )
    ? evidence.search_ids
    : [];

  // ==========================================================
  // Source distribution
  // ==========================================================

  const sourceDistribution = Array.isArray(
    evidence.source_distribution
  )
    ? evidence.source_distribution
    : [];

  // ==========================================================
  // Sentiment distribution
  // ==========================================================

  const sentimentDistribution = Array.isArray(
    evidence.sentiment_distribution
  )
    ? evidence.sentiment_distribution
    : [];

  // ==========================================================
  // Topic distribution
  // ==========================================================

  const topicDistribution = Array.isArray(
    evidence.topic_distribution
  )
    ? evidence.topic_distribution
    : [];

  // ==========================================================
  // Representative mentions
  //
  // These become Supporting Evidence on the page.
  // ==========================================================

  const supportingEvidence = Array.isArray(
    evidence.representative_mentions
  )
    ? evidence.representative_mentions
    : [];

  // ==========================================================
  // AI generated sections
  // ==========================================================

  const summary =
    aiInsights.summary ||
    "No AI summary available.";

  const keyThemes = Array.isArray(
    aiInsights.key_themes
  )
    ? aiInsights.key_themes
    : [];

  const painPoints = Array.isArray(
    aiInsights.pain_points
  )
    ? aiInsights.pain_points
    : [];

  const opportunities = Array.isArray(
    aiInsights.opportunities
  )
    ? aiInsights.opportunities
    : [];

  const recommendedActions = Array.isArray(
    aiInsights.recommended_actions
  )
    ? aiInsights.recommended_actions
    : [];

  const limitations = Array.isArray(
    aiInsights.limitations
  )
    ? aiInsights.limitations
    : [];

  // ==========================================================
  // Main UI
  // ==========================================================

  return (
    <div className="space-y-6">

      {/* ======================================================
          Header
      ====================================================== */}

      <div>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-bold text-white">
            AI Insights
          </h1>

          <span className="rounded-full bg-blue-500/10 px-3 py-1 text-xs font-medium text-blue-300">
            AI Generated
          </span>
        </div>

        <p className="mt-2 text-sm text-slate-400">
          Evidence-grounded analysis for{" "}
          <span className="font-medium text-slate-200">
            {data.keyword || activeSearch.keyword}
          </span>
        </p>
      </div>

      {/* ======================================================
          Back to Dashboard
      ====================================================== */}

      <div>
        <a
          href={`/dashboard?search_id=${activeSearch.id}`}
          className="inline-flex items-center rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-xs font-medium text-slate-300 transition hover:border-blue-500 hover:text-white"
        >
          ← Back to Dashboard
        </a>
      </div>

      {/* ======================================================
          Accumulated Evidence
      ====================================================== */}

      <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">

        <div className="flex flex-wrap items-center justify-between gap-3">

          <div>
            <h2 className="text-lg font-semibold text-white">
              Accumulated Keyword Evidence
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Evidence collected across completed searches
              for this keyword.
            </p>
          </div>

          <div className="rounded-lg bg-slate-800 px-4 py-2 text-sm text-slate-300">
            {totalEvidence} evidence{" "}
            {totalEvidence === 1 ? "item" : "items"}
          </div>
        </div>

        <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">

          {/* Total Evidence */}

          <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">
              Total Evidence
            </p>

            <p className="mt-2 text-2xl font-bold text-white">
              {totalEvidence}
            </p>

            <p className="mt-1 text-xs text-slate-600">
              Unique relevant mentions
            </p>
          </div>

          {/* Relevant Evidence */}

          <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">
              Relevant Evidence
            </p>

            <p className="mt-2 text-2xl font-bold text-white">
              {relevantEvidence}
            </p>

            <p className="mt-1 text-xs text-slate-600">
              Relevant and non-duplicate
            </p>
          </div>

          {/* Sources */}

          <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
            <p className="text-xs uppercase tracking-wide text-slate-500">
              Sources
            </p>

            <p className="mt-2 text-2xl font-bold text-white">
              {sourceDistribution.length}
            </p>

            <p className="mt-1 text-xs text-slate-600">
              Public source types
            </p>
          </div>

        </div>
      </div>

      {/* ======================================================
          AI Summary
      ====================================================== */}

      <div className="rounded-xl border border-blue-900/40 bg-blue-950/10 p-6">

        <div className="flex items-center gap-3">

          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-500/10 text-blue-300">
            ✦
          </div>

          <div>
            <h2 className="text-lg font-semibold text-white">
              AI Summary
            </h2>

            <p className="text-xs text-slate-500">
              Generated from collected evidence
            </p>
          </div>

        </div>

        <p className="mt-5 whitespace-pre-line text-sm leading-7 text-slate-300">
          {summary}
        </p>

      </div>

      {/* ======================================================
          Evidence Overview + Source Coverage
      ====================================================== */}

      <div className="grid gap-6 lg:grid-cols-2">

        {/* Evidence Overview */}

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">

          <h2 className="text-lg font-semibold text-white">
            Evidence Overview
          </h2>

          <div className="mt-5 space-y-4">

            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <span className="text-sm text-slate-400">
                Keyword
              </span>

              <span className="text-sm font-semibold text-white">
                {data.keyword || activeSearch.keyword}
              </span>
            </div>

            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <span className="text-sm text-slate-400">
                Completed Searches
              </span>

              <span className="text-sm font-semibold text-white">
                {searchCount}
              </span>
            </div>

            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <span className="text-sm text-slate-400">
                Unique Evidence
              </span>

              <span className="text-sm font-semibold text-white">
                {totalEvidence}
              </span>
            </div>

            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <span className="text-sm text-slate-400">
                Negative Mentions
              </span>

              <span className="text-sm font-semibold text-white">
                {negativeMentionCount}
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">
                Search IDs
              </span>

              <span className="max-w-[60%] text-right text-sm font-semibold text-white">
                {searchIds.length > 0
                  ? searchIds.join(", ")
                  : "None"}
              </span>
            </div>

          </div>
        </div>

        {/* Source Coverage */}

        <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">

          <h2 className="text-lg font-semibold text-white">
            Source Coverage
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Distribution of unique evidence across sources.
          </p>

          {sourceDistribution.length === 0 ? (
            <p className="mt-4 text-sm text-slate-500">
              No source coverage information available.
            </p>
          ) : (
            <div className="mt-5 space-y-3">

              {sourceDistribution.map(
                (item, index) => (
                  <div
                    key={`${item.source}-${index}`}
                    className="flex items-center justify-between rounded-lg bg-slate-950 px-4 py-3"
                  >
                    <span className="text-sm text-slate-300">
                      {formatSource(item.source)}
                    </span>

                    <span className="font-semibold text-white">
                      {item.count || 0}
                    </span>
                  </div>
                )
              )}

            </div>
          )}
        </div>

      </div>

      {/* ======================================================
          Sentiment Distribution
      ====================================================== */}

      <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">

        <h2 className="text-lg font-semibold text-white">
          Sentiment Distribution
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Sentiment classification across the evidence.
        </p>

        {sentimentDistribution.length === 0 ? (
          <p className="mt-5 text-sm text-slate-500">
            No sentiment distribution available.
          </p>
        ) : (
          <div className="mt-5 grid gap-3 sm:grid-cols-3">

            {sentimentDistribution.map(
              (item, index) => {

                const sentiment =
                  item.sentiment || "neutral";

                const isPositive =
                  sentiment === "positive";

                const isNegative =
                  sentiment === "negative";

                return (
                  <div
                    key={`${sentiment}-${index}`}
                    className="rounded-lg border border-slate-800 bg-slate-950 p-4"
                  >
                    <p
                      className={`text-xs uppercase tracking-wide ${
                        isPositive
                          ? "text-emerald-400"
                          : isNegative
                            ? "text-red-400"
                            : "text-slate-400"
                      }`}
                    >
                      {sentiment}
                    </p>

                    <p className="mt-2 text-2xl font-bold text-white">
                      {item.count || 0}
                    </p>
                  </div>
                );
              }
            )}

          </div>
        )}
      </div>

      {/* ======================================================
          Topic Distribution
      ====================================================== */}

      <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">

        <h2 className="text-lg font-semibold text-white">
          Topic Distribution
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Main topics identified across the collected evidence.
        </p>

        {topicDistribution.length === 0 ? (
          <p className="mt-5 text-sm text-slate-500">
            No topic distribution available.
          </p>
        ) : (
          <div className="mt-5 space-y-3">

            {topicDistribution.map(
              (item, index) => {

                const maxCount =
                  Math.max(
                    ...topicDistribution.map(
                      (topic) =>
                        Number(topic.count || 0)
                    ),
                    1
                  );

                const count =
                  Number(item.count || 0);

                const width =
                  `${Math.max(
                    (count / maxCount) * 100,
                    4
                  )}%`;

                return (
                  <div
                    key={`${item.topic}-${index}`}
                    className="space-y-1"
                  >

                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-300">
                        {item.topic || "Other"}
                      </span>

                      <span className="text-xs font-medium text-slate-400">
                        {count}
                      </span>
                    </div>

                    <div className="h-2 overflow-hidden rounded-full bg-slate-800">
                      <div
                        className="h-full rounded-full bg-blue-500"
                        style={{
                          width,
                        }}
                      />
                    </div>

                  </div>
                );
              }
            )}

          </div>
        )}
      </div>

      {/* ======================================================
          Key Themes
      ====================================================== */}

      <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">

        <h2 className="text-lg font-semibold text-white">
          Key Themes
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Main themes identified from the collected evidence.
        </p>

        {keyThemes.length === 0 ? (
          <p className="mt-5 text-sm text-slate-500">
            No key themes available.
          </p>
        ) : (
          <div className="mt-5 grid gap-4 md:grid-cols-2">

            {keyThemes.map(
              (theme, index) => {

                const name =
                  theme.theme ||
                  theme.name ||
                  theme.topic ||
                  `Theme ${index + 1}`;

                const description =
                  theme.description ||
                  theme.summary ||
                  "";

                const evidenceIds =
                  Array.isArray(
                    theme.evidence_ids
                  )
                    ? theme.evidence_ids
                    : [];

                return (
                  <div
                    key={index}
                    className="rounded-lg border border-slate-800 bg-slate-950 p-4"
                  >

                    <h3 className="font-medium text-white">
                      {name}
                    </h3>

                    {description && (
                      <p className="mt-2 text-sm leading-6 text-slate-400">
                        {description}
                      </p>
                    )}

                    {evidenceIds.length > 0 && (
                      <div className="mt-4 flex flex-wrap gap-2">

                        {evidenceIds.map(
                          (id) => (
                            <EvidenceBadge
                              key={id}
                              id={id}
                            />
                          )
                        )}

                      </div>
                    )}

                  </div>
                );
              }
            )}

          </div>
        )}
      </div>

      {/* ======================================================
          Pain Points
      ====================================================== */}

      <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">

        <h2 className="text-lg font-semibold text-white">
          Pain Points
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Problems or complaints identified from the evidence.
        </p>

        {painPoints.length === 0 ? (
          <p className="mt-5 text-sm text-slate-500">
            No significant pain points identified.
          </p>
        ) : (
          <div className="mt-5 space-y-3">

            {painPoints.map(
              (point, index) => {

                const title =
                  point.title ||
                  point.issue ||
                  "Potential concern";

                const description =
                  point.description ||
                  point.text ||
                  "";

                const evidenceIds =
                  Array.isArray(
                    point.evidence_ids
                  )
                    ? point.evidence_ids
                    : [];

                return (
                  <div
                    key={index}
                    className="rounded-lg border border-red-900/30 bg-red-950/10 p-4"
                  >

                    <div className="flex gap-3">

                      <span className="mt-0.5 text-red-400">
                        •
                      </span>

                      <div>

                        <h3 className="font-medium text-white">
                          {title}
                        </h3>

                        {description && (
                          <p className="mt-2 text-sm leading-6 text-slate-300">
                            {description}
                          </p>
                        )}

                        {evidenceIds.length > 0 && (
                          <div className="mt-3 flex flex-wrap gap-2">

                            {evidenceIds.map(
                              (id) => (
                                <EvidenceBadge
                                  key={id}
                                  id={id}
                                />
                              )
                            )}

                          </div>
                        )}

                      </div>

                    </div>

                  </div>
                );
              }
            )}

          </div>
        )}
      </div>

      {/* ======================================================
          Potential Opportunities
      ====================================================== */}

      <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">

        <h2 className="text-lg font-semibold text-white">
          Potential Opportunities
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Potential areas worth investigating based on the evidence.
        </p>

        {opportunities.length === 0 ? (
          <p className="mt-5 text-sm text-slate-500">
            No opportunities identified.
          </p>
        ) : (
          <div className="mt-5 space-y-3">

            {opportunities.map(
              (opportunity, index) => {

                const title =
                  opportunity.title ||
                  opportunity.name ||
                  "Potential opportunity";

                const description =
                  opportunity.description ||
                  opportunity.text ||
                  "";

                const evidenceIds =
                  Array.isArray(
                    opportunity.evidence_ids
                  )
                    ? opportunity.evidence_ids
                    : [];

                return (
                  <div
                    key={index}
                    className="rounded-lg border border-emerald-900/30 bg-emerald-950/10 p-4"
                  >

                    <div className="flex gap-3">

                      <span className="mt-0.5 text-emerald-400">
                        •
                      </span>

                      <div>

                        <h3 className="font-medium text-white">
                          {title}
                        </h3>

                        {description && (
                          <p className="mt-2 text-sm leading-6 text-slate-300">
                            {description}
                          </p>
                        )}

                        {evidenceIds.length > 0 && (
                          <div className="mt-3 flex flex-wrap gap-2">

                            {evidenceIds.map(
                              (id) => (
                                <EvidenceBadge
                                  key={id}
                                  id={id}
                                />
                              )
                            )}

                          </div>
                        )}

                      </div>

                    </div>

                  </div>
                );
              }
            )}

          </div>
        )}
      </div>

      {/* ======================================================
          Supporting Evidence
      ====================================================== */}

      <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">

        <div>
          <h2 className="text-lg font-semibold text-white">
            Supporting Evidence
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Representative mentions supporting the generated insights.
          </p>
        </div>

        {supportingEvidence.length === 0 ? (
          <p className="mt-5 text-sm text-slate-500">
            No supporting evidence available.
          </p>
        ) : (
          <div className="mt-5 space-y-4">

            {supportingEvidence.map(
              (item, index) => {

                const id =
                  item.id ??
                  index + 1;

                const title =
                  item.title ||
                  "Untitled mention";

                const content =
                  item.content ||
                  "";

                const source =
                  item.source ||
                  "Unknown";

                const url =
                  item.url ||
                  "";

                return (
                  <div
                    key={`${id}-${index}`}
                    className="rounded-lg border border-slate-800 bg-slate-950 p-5"
                  >

                    <div className="flex flex-wrap items-center gap-2">

                      <EvidenceBadge id={id} />

                      <span className="rounded-md bg-slate-800 px-2 py-1 text-xs text-slate-400">
                        {formatSource(source)}
                      </span>

                      {item.sentiment && (
                        <span className="rounded-md bg-slate-800 px-2 py-1 text-xs text-slate-400">
                          {item.sentiment}
                        </span>
                      )}

                      {item.topic && (
                        <span className="rounded-md bg-slate-800 px-2 py-1 text-xs text-slate-400">
                          {item.topic}
                        </span>
                      )}

                    </div>

                    <h3 className="mt-4 font-medium text-white">
                      {getText(
                        title,
                        "Untitled mention"
                      )}
                    </h3>

                    {content && (
                      <p className="mt-2 text-sm leading-6 text-slate-400">
                        {content}
                      </p>
                    )}

                    {url && (
                      <a
                        href={url}
                        target="_blank"
                        rel="noreferrer"
                        className="mt-4 inline-block text-sm text-blue-400 hover:text-blue-300"
                      >
                        View source →
                      </a>
                    )}

                  </div>
                );
              }
            )}

          </div>
        )}
      </div>

      {/* ======================================================
          Recommended Actions
      ====================================================== */}

      <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">

        <h2 className="text-lg font-semibold text-white">
          Recommended Actions
        </h2>

        {recommendedActions.length === 0 ? (
          <p className="mt-4 text-sm text-slate-500">
            No recommended actions available.
          </p>
        ) : (
          <ol className="mt-5 space-y-3">

            {recommendedActions.map(
              (action, index) => {

                const text =
                  typeof action === "string"
                    ? action
                    : action.action ||
                      action.description ||
                      action.text ||
                      JSON.stringify(action);

                return (
                  <li
                    key={index}
                    className="flex gap-4 rounded-lg bg-slate-950 p-4"
                  >

                    <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-blue-500/10 text-sm font-semibold text-blue-300">
                      {index + 1}
                    </span>

                    <p className="text-sm leading-6 text-slate-300">
                      {text}
                    </p>

                  </li>
                );
              }
            )}

          </ol>
        )}
      </div>

      {/* ======================================================
          Limitations
      ====================================================== */}

      <div className="rounded-xl border border-amber-900/30 bg-amber-950/10 p-6">

        <h2 className="text-lg font-semibold text-amber-200">
          Limitations
        </h2>

        {limitations.length === 0 ? (
          <p className="mt-4 text-sm text-slate-400">
            No additional limitations reported.
          </p>
        ) : (
          <ul className="mt-4 space-y-2">

            {limitations.map(
              (limitation, index) => {

                const text =
                  typeof limitation === "string"
                    ? limitation
                    : limitation.description ||
                      limitation.text ||
                      JSON.stringify(limitation);

                return (
                  <li
                    key={index}
                    className="flex gap-3 text-sm leading-6 text-slate-400"
                  >
                    <span>•</span>

                    <span>
                      {text}
                    </span>
                  </li>
                );
              }
            )}

          </ul>
        )}
      </div>

      {/* ======================================================
          Disclaimer
      ====================================================== */}

      <div className="rounded-xl border border-slate-800 bg-slate-950 p-5">

        <p className="text-xs leading-5 text-slate-500">
          AI-generated insights are based on the collected
          public mentions and the evidence available to the
          platform. They should be treated as analytical
          assistance rather than independently verified facts.
        </p>

      </div>

    </div>
  );
}

export default Insights;