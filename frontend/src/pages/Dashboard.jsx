import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  createSearch,
  getAnalytics,
  getMentions,
} from "../services/api";

import { useSearch } from "../context/useSearch";

import {
  Link,
  useSearchParams,
} from "react-router-dom";

// =========================================================
// API
// =========================================================

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

// =========================================================
// Browser Reload Detection
// =========================================================
//
// React Router navigation does NOT trigger beforeunload.
//
// Real browser reload DOES trigger beforeunload.
//
// We store a temporary sessionStorage flag before the
// browser reloads. When the application starts again,
// the flag is consumed and the selected dashboard is reset.
//
// =========================================================

const RELOAD_FLAG =
  "social_listening_browser_reload";

function consumeBrowserReloadFlag() {
  try {
    const wasReload =
      sessionStorage.getItem(
        RELOAD_FLAG
      ) === "1";

    if (wasReload) {
      sessionStorage.removeItem(
        RELOAD_FLAG
      );
    }

    return wasReload;
  } catch (error) {
    console.warn(
      "Unable to read browser reload flag:",
      error
    );

    return false;
  }
}

// =========================================================
// Dashboard
// =========================================================

function Dashboard() {
  const {
    activeSearch,
    setActiveSearch,
    clearActiveSearch,
  } = useSearch();

  const [
    searchParams,
    setSearchParams,
  ] = useSearchParams();

  // =========================================================
  // Detect whether this page load was caused by a real
  // browser reload.
  // =========================================================

  const browserReloadRef =
    useRef(null);

  if (
    browserReloadRef.current ===
    null
  ) {
    browserReloadRef.current =
      consumeBrowserReloadFlag();
  }

  // =========================================================
  // Search input
  // =========================================================

  const [
    keyword,
    setKeyword,
  ] = useState(
    activeSearch?.keyword || ""
  );

  // =========================================================
  // URL search ID
  //
  // /dashboard
  //     -> Landing page
  //
  // /dashboard?search_id=223
  //     -> Selected search dashboard
  // =========================================================

  const urlSearchIdValue =
    searchParams.get(
      "search_id"
    );

  const urlSearchId =
    urlSearchIdValue
      ? Number(urlSearchIdValue)
      : null;

  const searchId =
    Number.isInteger(urlSearchId) &&
    urlSearchId > 0
      ? urlSearchId
      : null;

  // =========================================================
  // Dashboard state
  // =========================================================

  const [
    analytics,
    setAnalytics,
  ] = useState(null);

  const [
    mentions,
    setMentions,
  ] = useState([]);

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    searching,
    setSearching,
  ] = useState(false);

  const [
    loadingHistoricalSearch,
    setLoadingHistoricalSearch,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState("");

  // =========================================================
  // Request control
  // =========================================================

  const requestVersionRef =
    useRef(0);

  const activeSearchIdRef =
    useRef(null);

  const creatingSearchRef =
    useRef(false);

  const latestCreatedSearchIdRef =
    useRef(null);

  const lastHandledUrlSearchIdRef =
    useRef(null);

  // =========================================================
  // RECORD REAL BROWSER RELOAD
  // =========================================================
  //
  // This runs when the current document is actually being
  // unloaded.
  //
  // React Router navigation:
  //
  // Dashboard → Mentions
  //
  // does NOT trigger this.
  //
  // Browser reload:
  //
  // Ctrl + R
  //
  // DOES trigger this.
  //
  // =========================================================

  useEffect(() => {
    const handleBeforeUnload = () => {
      try {
        sessionStorage.setItem(
          RELOAD_FLAG,
          "1"
        );
      } catch (error) {
        console.warn(
          "Unable to save browser reload flag:",
          error
        );
      }
    };

    window.addEventListener(
      "beforeunload",
      handleBeforeUnload
    );

    return () => {
      window.removeEventListener(
        "beforeunload",
        handleBeforeUnload
      );
    };
  }, []);

  // =========================================================
  // RESET AFTER REAL BROWSER RELOAD
  // =========================================================
  //
  // Example:
  //
  // Before:
  // /dashboard?search_id=223
  //
  // After Ctrl + R:
  // /dashboard
  //
  // Normal React Router navigation is NOT affected.
  //
  // =========================================================

  useEffect(() => {
    if (!browserReloadRef.current) {
      return;
    }

    if (
      !searchParams.has(
        "search_id"
      )
    ) {
      browserReloadRef.current =
        false;

      return;
    }

    const timer = setTimeout(() => {
      // Invalidate all previous requests.
      ++requestVersionRef.current;

      // Clear dashboard data.
      setAnalytics(null);
      setMentions([]);

      setLoading(false);
      setLoadingHistoricalSearch(
        false
      );

      setSearching(false);

      setError("");
      setKeyword("");

      // Clear active search from context.
      clearActiveSearch();

      // Clear selected search from URL.
      //
      // /dashboard?search_id=223
      //
      // becomes:
      //
      // /dashboard
      //
      setSearchParams(
        {},
        {
          replace: true,
        }
      );

      // Clear internal search references.
      activeSearchIdRef.current =
        null;

      lastHandledUrlSearchIdRef.current =
        null;

      latestCreatedSearchIdRef.current =
        null;

      // Allow normal operation again.
      browserReloadRef.current =
        false;
    }, 0);

    return () => {
      clearTimeout(timer);
    };
  }, [
    searchParams,
    setSearchParams,
    clearActiveSearch,
  ]);

  // =========================================================
  // Keep active search ref synchronized
  // =========================================================

  useEffect(() => {
    activeSearchIdRef.current =
      activeSearch?.id
        ? Number(activeSearch.id)
        : null;
  }, [
    activeSearch?.id,
  ]);

  // =========================================================
  // Synchronize keyword with active search
  // =========================================================

  useEffect(() => {
    if (
      !activeSearch?.keyword
    ) {
      return;
    }

    const timer = setTimeout(() => {
      setKeyword(
        (currentKeyword) => {
          if (
            currentKeyword ===
            activeSearch.keyword
          ) {
            return currentKeyword;
          }

          return activeSearch.keyword;
        }
      );
    }, 0);

    return () => {
      clearTimeout(timer);
    };
  }, [
    activeSearch?.id,
    activeSearch?.keyword,
  ]);

  // =========================================================
  // Load historical search from URL
  // =========================================================

  useEffect(() => {
    // Do NOT load the old search while handling a
    // browser reload.
    if (browserReloadRef.current) {
      return;
    }

    if (!urlSearchIdValue) {
      return;
    }

    if (
      !Number.isInteger(
        urlSearchId
      ) ||
      urlSearchId <= 0
    ) {
      return;
    }

    // Already active.
    if (
      Number(
        activeSearchIdRef.current
      ) === urlSearchId
    ) {
      lastHandledUrlSearchIdRef.current =
        urlSearchId;

      return;
    }

    // Search creation currently running.
    if (
      creatingSearchRef.current
    ) {
      return;
    }

    // Newly created search.
    if (
      Number(
        latestCreatedSearchIdRef.current
      ) === urlSearchId
    ) {
      lastHandledUrlSearchIdRef.current =
        urlSearchId;

      return;
    }

    // Already handled.
    if (
      lastHandledUrlSearchIdRef.current ===
      urlSearchId
    ) {
      return;
    }

    let cancelled = false;

    async function loadHistoricalSearch() {
      const currentRequestVersion =
        ++requestVersionRef.current;

      try {
        setLoadingHistoricalSearch(
          true
        );

        setLoading(true);
        setError("");

        setAnalytics(null);
        setMentions([]);

        const response =
          await fetch(
            `${API_BASE_URL}/api/searches/${urlSearchId}`
          );

        if (!response.ok) {
          let errorMessage =
            "Failed to load the selected search.";

          try {
            const errorData =
              await response.json();

            errorMessage =
              errorData.detail ||
              errorMessage;
          } catch {
            // Keep default message.
          }

          throw new Error(
            errorMessage
          );
        }

        const search =
          await response.json();

        if (
          cancelled ||
          currentRequestVersion !==
            requestVersionRef.current
        ) {
          return;
        }

        if (
          !search ||
          !search.id ||
          !search.keyword
        ) {
          throw new Error(
            "The selected search returned invalid data."
          );
        }

        const historicalSearch = {
          id: Number(
            search.id
          ),

          keyword: String(
            search.keyword
          ),
        };

        lastHandledUrlSearchIdRef.current =
          historicalSearch.id;

        setActiveSearch(
          historicalSearch
        );

        setKeyword(
          historicalSearch.keyword
        );
      } catch (loadError) {
        if (cancelled) {
          return;
        }

        console.error(
          "Historical search loading error:",
          loadError
        );

        setError(
          loadError.message ||
            "Failed to load the selected search."
        );

        setLoading(false);
      } finally {
        if (!cancelled) {
          setLoadingHistoricalSearch(
            false
          );
        }
      }
    }

    loadHistoricalSearch();

    return () => {
      cancelled = true;
    };
  }, [
    urlSearchIdValue,
    urlSearchId,
    setActiveSearch,
  ]);

  // =========================================================
  // Load dashboard data
  // =========================================================

  const loadDashboard =
    useCallback(
      async (id) => {
        const numericId =
          Number(id);

        if (
          !Number.isInteger(
            numericId
          ) ||
          numericId <= 0
        ) {
          return;
        }

        const currentRequestVersion =
          ++requestVersionRef.current;

        try {
          setLoading(true);
          setError("");

          const [
            analyticsData,
            mentionsData,
          ] = await Promise.all([
            getAnalytics(
              numericId
            ),

            getMentions(
              numericId,
              {
                page: 1,
                page_size: 5,
              }
            ),
          ]);

          if (
            currentRequestVersion !==
            requestVersionRef.current
          ) {
            return;
          }

          // Make sure the analytics response belongs
          // to the requested search.
          if (
            analyticsData?.search_id &&
            Number(
              analyticsData.search_id
            ) !== numericId
          ) {
            console.warn(
              "Ignoring analytics response for another search.",
              {
                expected:
                  numericId,

                received:
                  analyticsData.search_id,
              }
            );

            return;
          }

          setAnalytics(
            analyticsData
          );

          setMentions(
            mentionsData?.items ||
              []
          );
        } catch (loadError) {
          if (
            currentRequestVersion !==
            requestVersionRef.current
          ) {
            return;
          }

          console.error(
            "Dashboard loading error:",
            loadError
          );

          setError(
            loadError.response
              ?.data?.detail ||
              loadError.message ||
              "Failed to load dashboard data."
          );
        } finally {
          if (
            currentRequestVersion ===
            requestVersionRef.current
          ) {
            setLoading(false);
          }
        }
      },
      []
    );

  // =========================================================
  // Load dashboard when URL search changes
  // =========================================================

  useEffect(() => {
    // Do NOT reload the old dashboard while handling
    // a real browser reload.
    if (browserReloadRef.current) {
      return;
    }

    if (!searchId) {
      return;
    }

    const timer = setTimeout(() => {
      loadDashboard(
        searchId
      );
    }, 0);

    return () => {
      clearTimeout(timer);
    };
  }, [
    searchId,
    loadDashboard,
  ]);

  // =========================================================
  // Create new search
  // =========================================================

  const handleSearch =
    async (event) => {
      event.preventDefault();

      const trimmedKeyword =
        keyword.trim();

      if (!trimmedKeyword) {
        setError(
          "Please enter a keyword to monitor."
        );

        return;
      }

      if (searching) {
        return;
      }

      try {
        creatingSearchRef.current =
          true;

        setSearching(true);
        setError("");

        ++requestVersionRef.current;

        setAnalytics(null);
        setMentions([]);

        setLoading(true);

        const result =
          await createSearch(
            trimmedKeyword
          );

        if (
          !result ||
          !result.id ||
          !result.keyword
        ) {
          throw new Error(
            "The search API returned invalid search data."
          );
        }

        const newSearch = {
          id: Number(
            result.id
          ),

          keyword: String(
            result.keyword
          ),
        };

        latestCreatedSearchIdRef.current =
          newSearch.id;

        lastHandledUrlSearchIdRef.current =
          newSearch.id;

        setActiveSearch(
          newSearch
        );

        setKeyword(
          newSearch.keyword
        );

        // Move from landing page to selected
        // dashboard.
        setSearchParams(
          {
            search_id:
              String(
                newSearch.id
              ),
          },
          {
            replace: true,
          }
        );
      } catch (searchError) {
        console.error(
          "Search error:",
          searchError
        );

        setError(
          searchError.response
            ?.data?.detail ||
            searchError.message ||
            "Search failed."
        );

        setLoading(false);
      } finally {
        creatingSearchRef.current =
          false;

        setSearching(false);
      }
    };

  // =========================================================
  // Loading selected search
  // =========================================================

  if (
    loading &&
    !analytics &&
    searchId
  ) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center">
        <div className="text-center">

          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-700 border-t-blue-500" />

          <p className="mt-4 text-sm text-slate-400">
            {searching
              ? "Collecting and processing new mentions..."
              : loadingHistoricalSearch
                ? "Loading selected search..."
                : "Loading social listening data..."}
          </p>

          {activeSearch?.keyword && (
            <p className="mt-2 text-xs text-slate-600">
              {activeSearch.keyword}
            </p>
          )}

        </div>
      </div>
    );
  }

  // =========================================================
  // Error state
  // =========================================================

  if (
    error &&
    !analytics &&
    searchId
  ) {
    return (
      <div className="rounded-xl border border-red-900/50 bg-red-950/30 p-6">

        <h2 className="text-lg font-semibold text-red-400">
          Dashboard Error
        </h2>

        <p className="mt-2 text-sm text-slate-300">
          {error}
        </p>

        <button
          type="button"
          onClick={() =>
            loadDashboard(
              searchId
            )
          }
          className="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-500"
        >
          Try again
        </button>

      </div>
    );
  }

  // =========================================================
  // LANDING PAGE
  //
  // /dashboard
  // =========================================================

  if (!searchId) {
    return (
      <div className="flex min-h-[calc(100vh-120px)] items-center justify-center px-4">

        <div className="w-full max-w-3xl text-center">

          <div className="mb-6 inline-flex items-center rounded-full border border-blue-500/20 bg-blue-500/10 px-4 py-2 text-xs font-medium text-blue-400">
            Open-source intelligence platform
          </div>

          <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl lg:text-6xl">
            Social Listening
          </h1>

          <p className="mx-auto mt-5 max-w-2xl text-base leading-7 text-slate-400 sm:text-lg">
            Monitor public conversations across
            multiple sources, analyze sentiment and
            topics, and turn online discussions into
            actionable insights.
          </p>

          <form
            onSubmit={handleSearch}
            className="mx-auto mt-10 w-full max-w-2xl"
          >

            <div className="flex flex-col gap-3 sm:flex-row">

              <input
                type="text"
                value={keyword}
                onChange={(event) => {
                  setKeyword(
                    event.target.value
                  );

                  if (error) {
                    setError("");
                  }
                }}
                placeholder="Enter a brand, product, or keyword..."
                autoFocus
                disabled={searching}
                className="min-w-0 flex-1 rounded-xl border border-slate-700 bg-slate-900 px-5 py-4 text-sm text-white shadow-lg outline-none placeholder:text-slate-500 transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 disabled:cursor-not-allowed disabled:opacity-60"
              />

              <button
                type="submit"
                disabled={searching}
                className="rounded-xl bg-blue-600 px-8 py-4 text-sm font-semibold text-white shadow-lg shadow-blue-600/10 transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {searching
                  ? "Searching..."
                  : "Search"}
              </button>

            </div>

          </form>

          {error && (
            <div className="mx-auto mt-4 max-w-2xl rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-left text-sm text-red-300">
              {error}
            </div>
          )}

          <p className="mt-5 text-xs text-slate-600">
            Try searching for a product, company,
            technology, or brand.
          </p>

          <div className="mt-12 grid grid-cols-1 gap-4 text-left sm:grid-cols-3">

            <LandingFeature
              title="Public Sources"
              description="Collect mentions from supported public web sources."
            />

            <LandingFeature
              title="NLP Analysis"
              description="Analyze sentiment, relevance, duplicates, and topics."
            />

            <LandingFeature
              title="Actionable Insights"
              description="Explore trends, themes, pain points, and opportunities."
            />

          </div>

        </div>

      </div>
    );
  }

  // =========================================================
  // Safety fallback
  // =========================================================

  if (!analytics) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center">

        <div className="text-center">

          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-700 border-t-blue-500" />

          <p className="mt-4 text-sm text-slate-400">
            Loading dashboard...
          </p>

        </div>

      </div>
    );
  }

  // =========================================================
  // Prepare chart data
  // =========================================================

  const sentimentData =
    analytics.sentiment_distribution ||
    [];

  const topicData =
    analytics.topic_distribution ||
    [];

  const sourceData =
    analytics.source_distribution ||
    [];

  const rawTrendData =
    analytics.mentions_over_time ||
    [];

  const trendData =
    rawTrendData.map(
      (item) => ({
        ...item,

        displayDate:
          formatTrendDate(
            item.date
          ),

        fullDate:
          formatTrendTooltipDate(
            item.date
          ),
      })
    );

  // =========================================================
  // Sentiment colors
  // =========================================================

  const sentimentColors = {
    positive: "#22c55e",
    neutral: "#94a3b8",
    negative: "#ef4444",
  };

  // =========================================================
  // Sentiment counts
  // =========================================================

  const getSentimentCount =
    (sentiment) => {
      const item =
        sentimentData.find(
          (entry) =>
            entry.sentiment ===
            sentiment
        );

      return item?.count || 0;
    };

  const positiveCount =
    getSentimentCount(
      "positive"
    );

  const neutralCount =
    getSentimentCount(
      "neutral"
    );

  const negativeCount =
    getSentimentCount(
      "negative"
    );

  // =========================================================
  // Dashboard Render
  // =========================================================

  return (
    <div className="space-y-8">

      {/* Header */}

      <div>

        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">

          <div>

            <p className="text-sm font-medium text-blue-400">
              Social Listening Dashboard
            </p>

            <h1 className="mt-1 text-3xl font-bold tracking-tight text-white">
              {analytics.keyword}
            </h1>

            <p className="mt-2 text-sm text-slate-400">
              Monitor public conversations,
              sentiment, topics, and trends.
            </p>

            {activeSearch?.id && (
              <p className="mt-2 text-xs text-slate-600">
                Search #{activeSearch.id}
              </p>
            )}

          </div>

          <form
            onSubmit={handleSearch}
            className="flex w-full max-w-xl gap-2"
          >

            <input
              type="text"
              value={keyword}
              onChange={(event) =>
                setKeyword(
                  event.target.value
                )
              }
              placeholder="Brand, product, or keyword..."
              className="min-w-0 flex-1 rounded-lg border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500 focus:border-blue-500"
            />

            <button
              type="submit"
              disabled={searching}
              className="rounded-lg bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {searching
                ? "Searching..."
                : "Search"}
            </button>

          </form>

        </div>

        {error && (
          <div className="mt-4 rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

      </div>

      {/* KPI Cards */}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-6">

        <MetricCard
          label="Collected"
          value={
            analytics.total_collected
          }
          description="Raw mentions collected"
        />

        <MetricCard
          label="New Mentions"
          value={
            analytics.total_processed
          }
          description="Relevant, non-duplicate mentions saved"
        />

        <MetricCard
          label="Total Mentions"
          value={
            analytics.total_mentions
          }
          description="Accumulated unique listening data"
        />

        <MetricCard
          label="Positive"
          value={positiveCount}
          description="Positive mentions"
        />

        <MetricCard
          label="Neutral"
          value={neutralCount}
          description="Neutral mentions"
        />

        <MetricCard
          label="Negative"
          value={negativeCount}
          description="Negative mentions"
        />

      </div>

      {/* Sentiment + Topics */}

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">

        <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">

          <div className="mb-5">

            <h2 className="text-lg font-semibold text-white">
              Sentiment Distribution
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Distribution of analyzed mentions.
            </p>

          </div>

          {sentimentData.length === 0 ? (
            <EmptyChart />
          ) : (
            <div className="h-72">

              <ResponsiveContainer
                width="100%"
                height="100%"
              >

                <PieChart>

                  <Pie
                    data={sentimentData}
                    dataKey="count"
                    nameKey="sentiment"
                    cx="50%"
                    cy="50%"
                    outerRadius={95}
                    innerRadius={55}
                    paddingAngle={3}
                  >

                    {sentimentData.map(
                      (entry) => (
                        <Cell
                          key={
                            entry.sentiment
                          }
                          fill={
                            sentimentColors[
                              entry.sentiment
                            ] ||
                            "#64748b"
                          }
                        />
                      )
                    )}

                  </Pie>

                  <Tooltip
                    contentStyle={{
                      backgroundColor:
                        "#0f172a",

                      border:
                        "1px solid #334155",

                      borderRadius:
                        "8px",
                    }}
                  />

                </PieChart>

              </ResponsiveContainer>

            </div>
          )}

        </section>

        <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">

          <div className="mb-5">

            <h2 className="text-lg font-semibold text-white">
              Top Topics
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Topics identified in relevant
              mentions.
            </p>

          </div>

          {topicData.length === 0 ? (
            <EmptyChart />
          ) : (
            <div className="h-72">

              <ResponsiveContainer
                width="100%"
                height="100%"
              >

                <BarChart
                  data={topicData}
                  layout="vertical"
                  margin={{
                    top: 5,
                    right: 20,
                    left: 30,
                    bottom: 5,
                  }}
                >

                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#1e293b"
                  />

                  <XAxis
                    type="number"
                    stroke="#64748b"
                    allowDecimals={false}
                  />

                  <YAxis
                    type="category"
                    dataKey="topic"
                    stroke="#64748b"
                    width={100}
                  />

                  <Tooltip
                    contentStyle={{
                      backgroundColor:
                        "#0f172a",

                      border:
                        "1px solid #334155",

                      borderRadius:
                        "8px",
                    }}
                  />

                  <Bar
                    dataKey="count"
                    fill="#3b82f6"
                    radius={[
                      0,
                      5,
                      5,
                      0,
                    ]}
                  />

                </BarChart>

              </ResponsiveContainer>

            </div>
          )}

        </section>

      </div>

      {/* Source Distribution */}

      <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">

        <div className="mb-5">

          <h2 className="text-lg font-semibold text-white">
            Sources
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Distribution of relevant mentions by
            data source.
          </p>

        </div>

        {sourceData.length === 0 ? (
          <EmptyChart />
        ) : (
          <div className="h-72">

            <ResponsiveContainer
              width="100%"
              height="100%"
            >

              <BarChart
                data={sourceData}
                margin={{
                  top: 10,
                  right: 20,
                  left: 0,
                  bottom: 10,
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#1e293b"
                />

                <XAxis
                  dataKey="source"
                  stroke="#64748b"
                  tickFormatter={
                    formatSource
                  }
                />

                <YAxis
                  allowDecimals={false}
                  stroke="#64748b"
                />

                <Tooltip
                  contentStyle={{
                    backgroundColor:
                      "#0f172a",

                    border:
                      "1px solid #334155",

                    borderRadius:
                      "8px",
                  }}
                  labelFormatter={
                    formatSource
                  }
                />

                <Bar
                  dataKey="count"
                  fill="#3b82f6"
                  radius={[
                    5,
                    5,
                    0,
                    0,
                  ]}
                />

              </BarChart>

            </ResponsiveContainer>

          </div>
        )}

      </section>

      {/* Mentions Over Time */}

      <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">

        <div className="mb-5">

          <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">

            <div>

              <h2 className="text-lg font-semibold text-white">
                Mentions Over Time
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Number of relevant mentions by
                publication date.
              </p>

            </div>

            {trendData.length > 0 && (
              <span className="text-xs text-slate-600">
                {trendData.length} date
                {trendData.length === 1
                  ? ""
                  : "s"}{" "}
                represented
              </span>
            )}

          </div>

        </div>

        {trendData.length === 0 ? (
          <EmptyChart />
        ) : (
          <div className="h-80">

            <ResponsiveContainer
              width="100%"
              height="100%"
            >

              <LineChart
                data={trendData}
                margin={{
                  top: 10,
                  right: 20,
                  left: 0,
                  bottom: 20,
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#1e293b"
                />

                <XAxis
                  dataKey="date"
                  stroke="#64748b"
                  tickFormatter={
                    formatTrendDate
                  }
                  interval="preserveStartEnd"
                  minTickGap={35}
                  tick={{
                    fontSize: 11,
                  }}
                />

                <YAxis
                  allowDecimals={false}
                  stroke="#64748b"
                  tick={{
                    fontSize: 11,
                  }}
                  width={35}
                />

                <Tooltip
                  contentStyle={{
                    backgroundColor:
                      "#0f172a",

                    border:
                      "1px solid #334155",

                    borderRadius:
                      "8px",
                  }}
                  labelFormatter={
                    formatTrendTooltipDate
                  }
                  formatter={(value) => [
                    value,
                    "Mentions",
                  ]}
                />

                <Line
                  type="monotone"
                  dataKey="count"
                  stroke="#3b82f6"
                  strokeWidth={3}
                  dot={{
                    r: 4,
                  }}
                  activeDot={{
                    r: 6,
                  }}
                />

              </LineChart>

            </ResponsiveContainer>

          </div>
        )}

      </section>

      {/* AI Insights Preview */}

      <section className="rounded-xl border border-blue-900/40 bg-gradient-to-br from-slate-900 to-blue-950/20 p-6">

        <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">

          <div>

            <p className="text-xs font-semibold uppercase tracking-wider text-blue-400">
              AI Analysis
            </p>

            <h2 className="mt-2 text-xl font-semibold text-white">
              AI Insights
            </h2>

            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              Generate an evidence-grounded
              summary of the conversations,
              key themes, pain points,
              opportunities, and supporting
              mentions for this search.
            </p>

            <div className="mt-4 flex flex-wrap gap-2">

              <InsightTag>
                Key themes
              </InsightTag>

              <InsightTag>
                Pain points
              </InsightTag>

              <InsightTag>
                Opportunities
              </InsightTag>

              <InsightTag>
                Evidence
              </InsightTag>

            </div>

          </div>

          <Link
            to={`/insights?search_id=${searchId}`}
            className="inline-flex shrink-0 items-center justify-center rounded-lg bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-500"
          >
            View AI Insights
          </Link>

        </div>

      </section>

      {/* Recent Mentions */}

      <section className="rounded-xl border border-slate-800 bg-slate-900">

        <div className="border-b border-slate-800 px-6 py-5">

          <div className="flex items-center justify-between">

            <div>

              <h2 className="text-lg font-semibold text-white">
                Recent Mentions
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Latest relevant conversations
                found for this search.
              </p>

            </div>

            <Link
              to={`/mentions?search_id=${searchId}`}
              className="text-sm font-medium text-blue-400 hover:text-blue-300"
            >
              View all
            </Link>

          </div>

        </div>

        <div className="overflow-x-auto">

          <table className="w-full min-w-[900px] text-left">

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
                  Date
                </th>

              </tr>

            </thead>

            <tbody className="divide-y divide-slate-800">

              {mentions.length > 0 ? (
                mentions.map(
                  (mention) => (
                    <tr
                      key={
                        mention.id
                      }
                      className="transition hover:bg-slate-800/40"
                    >

                      <td className="px-6 py-4">

                        <span className="rounded-md bg-slate-800 px-2.5 py-1 text-xs font-medium text-slate-300">
                          {formatSource(
                            mention.source
                          )}
                        </span>

                      </td>

                      <td className="max-w-xl px-6 py-4">

                        {mention.url ? (
                          <a
                            href={
                              mention.url
                            }
                            target="_blank"
                            rel="noopener noreferrer"
                            className="line-clamp-2 text-sm font-medium text-slate-200 hover:text-blue-400"
                          >
                            {mention.title ||
                              mention.content ||
                              "Untitled mention"}
                          </a>
                        ) : (
                          <p className="line-clamp-2 text-sm font-medium text-slate-200">
                            {mention.title ||
                              mention.content ||
                              "Untitled mention"}
                          </p>
                        )}

                        {mention.content && (
                          <p className="mt-1 line-clamp-2 text-xs text-slate-500">
                            {mention.content}
                          </p>
                        )}

                      </td>

                      <td className="px-6 py-4">

                        <SentimentBadge
                          sentiment={
                            mention.sentiment
                          }
                        />

                      </td>

                      <td className="px-6 py-4">

                        <span className="text-sm text-slate-300">
                          {mention.topic ||
                            "Other"}
                        </span>

                      </td>

                      <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-500">
                        {formatDate(
                          mention.published_at
                        )}
                      </td>

                    </tr>
                  )
                )
              ) : (
                <tr>

                  <td
                    colSpan={5}
                    className="px-6 py-10 text-center text-sm text-slate-500"
                  >
                    No relevant mentions
                    found.
                  </td>

                </tr>
              )}

            </tbody>

          </table>

        </div>

      </section>

    </div>
  );
}

// =========================================================
// Landing Feature
// =========================================================

function LandingFeature({
  title,
  description,
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-5">

      <div className="mb-3 h-2 w-8 rounded-full bg-blue-500" />

      <h3 className="text-sm font-semibold text-white">
        {title}
      </h3>

      <p className="mt-2 text-xs leading-5 text-slate-500">
        {description}
      </p>

    </div>
  );
}

// =========================================================
// Metric Card
// =========================================================

function MetricCard({
  label,
  value,
  description,
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">

      <p className="text-sm font-medium text-slate-400">
        {label}
      </p>

      <p className="mt-2 text-3xl font-bold tracking-tight text-white">
        {formatNumber(value)}
      </p>

      <p className="mt-2 text-xs text-slate-600">
        {description}
      </p>

    </div>
  );
}

// =========================================================
// Insight Tag
// =========================================================

function InsightTag({
  children,
}) {
  return (
    <span className="rounded-md border border-slate-700 bg-slate-950/50 px-2.5 py-1 text-xs text-slate-400">
      {children}
    </span>
  );
}

// =========================================================
// Sentiment Badge
// =========================================================

function SentimentBadge({
  sentiment,
}) {
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
      className={`rounded-md border px-2.5 py-1 text-xs font-medium capitalize ${
        styles[sentiment] ||
        styles.neutral
      }`}
    >
      {sentiment || "neutral"}
    </span>
  );
}

// =========================================================
// Source Formatter
// =========================================================

function formatSource(source) {
  const sourceNames = {
    rss: "RSS",
    hackernews: "Hacker News",
    stackexchange:
      "Stack Exchange",
    reddit: "Reddit",
  };

  if (!source) {
    return "Unknown";
  }

  return (
    sourceNames[
      String(source).toLowerCase()
    ] || source
  );
}

// =========================================================
// Empty Chart
// =========================================================

function EmptyChart() {
  return (
    <div className="flex h-full min-h-64 items-center justify-center">

      <p className="text-sm text-slate-600">
        No data available.
      </p>

    </div>
  );
}

// =========================================================
// Number Formatter
// =========================================================

function formatNumber(value) {
  if (
    value === null ||
    value === undefined
  ) {
    return "0";
  }

  const numericValue =
    Number(value);

  if (
    Number.isNaN(
      numericValue
    )
  ) {
    return "0";
  }

  return numericValue.toLocaleString(
    "en-IN"
  );
}

// =========================================================
// Standard Date Formatter
// =========================================================

function formatDate(value) {
  if (!value) {
    return "Unknown";
  }

  const date =
    new Date(value);

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
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

// =========================================================
// Trend Date Formatter
// =========================================================

function formatTrendDate(value) {
  if (!value) {
    return "";
  }

  const date =
    new Date(value);

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return String(value);
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

// =========================================================
// Trend Tooltip Date Formatter
// =========================================================

function formatTrendTooltipDate(
  value
) {
  if (!value) {
    return "Unknown date";
  }

  const date =
    new Date(value);

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return String(value);
  }

  return date.toLocaleDateString(
    "en-IN",
    {
      day: "2-digit",
      month: "long",
      year: "numeric",
    }
  );
}

// =========================================================
// Export
// =========================================================

export default Dashboard;