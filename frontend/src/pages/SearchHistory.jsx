import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

import { useSearch } from "../context/useSearch";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

function formatDateTime(value) {
  if (!value) {
    return "Unknown";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Unknown";
  }

  return date.toLocaleString();
}

function getStatusClasses(status) {
  switch (status) {
    case "completed":
      return "bg-emerald-500/10 text-emerald-400";

    case "running":
      return "bg-blue-500/10 text-blue-400";

    case "failed":
      return "bg-red-500/10 text-red-400";

    case "pending":
      return "bg-amber-500/10 text-amber-400";

    default:
      return "bg-slate-700 text-slate-400";
  }
}

function getStatusLabel(status) {
  if (!status) {
    return "Unknown";
  }

  return (
    status.charAt(0).toUpperCase() +
    status.slice(1)
  );
}

function SearchHistory() {
  const navigate = useNavigate();

  const {
    activeSearch,
    setActiveSearch,
  } = useSearch();

  const [searches, setSearches] = useState([]);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");

  // ============================================================
  // LOAD SEARCH HISTORY
  // ============================================================

  async function loadSearchHistory() {
    try {
      setLoading(true);
      setError("");

      const response = await axios.get(
        `${API_BASE_URL}/api/searches`
      );

      setSearches(response.data);
    } catch (err) {
      console.error(
        "Failed to load search history:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Failed to load search history."
      );
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // INITIAL LOAD
  // ============================================================

  useEffect(() => {
    const timer = setTimeout(() => {
      loadSearchHistory();
    }, 0);

    return () => {
      clearTimeout(timer);
    };
  }, []);

  // ============================================================
  // OPEN HISTORICAL SEARCH
  // ============================================================

  function openSearch(search) {
    if (!search || !search.id || !search.keyword) {
      return;
    }

    /*
     * Make the selected historical search the global
     * active search.
     *
     * This updates:
     *
     *   SearchContext
     *   localStorage
     *
     * so Dashboard, Mentions, Insights, and other
     * pages can use the same selected search.
     */

    setActiveSearch({
      id: search.id,
      keyword: search.keyword,
    });

    /*
     * Keep the search ID in the URL as well.
     *
     * This makes the selected historical search
     * directly identifiable from the browser URL.
     */

    navigate(
      `/dashboard?search_id=${search.id}`
    );
  }

  return (
    <div className="space-y-8">
      {/* ======================================================
          HEADER
      ====================================================== */}

      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-3xl font-bold text-white">
              Search History
            </h1>

            <span className="rounded-full bg-blue-500/10 px-3 py-1 text-xs font-medium text-blue-400">
              Collection History
            </span>
          </div>

          <p className="mt-2 max-w-3xl text-slate-400">
            View previous keyword searches and scheduled
            monitoring runs collected by the platform.
          </p>
        </div>

        <button
          type="button"
          onClick={loadSearchHistory}
          disabled={loading}
          className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-sm font-medium text-slate-300 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Refresh
        </button>
      </div>

      {/* ======================================================
          ACTIVE SEARCH
      ====================================================== */}

      {activeSearch && (
        <div className="rounded-lg border border-blue-900/50 bg-blue-950/20 px-5 py-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-medium uppercase tracking-wide text-blue-400">
              Active Search
            </span>

            <span className="text-sm text-slate-300">
              #{activeSearch.id}
            </span>

            <span className="text-slate-600">
              •
            </span>

            <span className="text-sm font-medium text-white">
              {activeSearch.keyword}
            </span>
          </div>

          <p className="mt-1 text-xs text-slate-500">
            Selecting a search makes it available to the
            platform&apos;s analysis pages.
          </p>
        </div>
      )}

      {/* ======================================================
          ERROR
      ====================================================== */}

      {error && (
        <div className="rounded-lg border border-red-900/60 bg-red-950/30 px-5 py-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* ======================================================
          SUMMARY CARDS
      ====================================================== */}

      {!loading &&
        !error &&
        searches.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
              <p className="text-xs uppercase tracking-wide text-slate-500">
                Total Searches
              </p>

              <p className="mt-2 text-2xl font-bold text-white">
                {searches.length}
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
              <p className="text-xs uppercase tracking-wide text-slate-500">
                Completed
              </p>

              <p className="mt-2 text-2xl font-bold text-emerald-400">
                {
                  searches.filter(
                    (search) =>
                      search.status === "completed"
                  ).length
                }
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
              <p className="text-xs uppercase tracking-wide text-slate-500">
                Running
              </p>

              <p className="mt-2 text-2xl font-bold text-blue-400">
                {
                  searches.filter(
                    (search) =>
                      search.status === "running"
                  ).length
                }
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
              <p className="text-xs uppercase tracking-wide text-slate-500">
                Failed
              </p>

              <p className="mt-2 text-2xl font-bold text-red-400">
                {
                  searches.filter(
                    (search) =>
                      search.status === "failed"
                  ).length
                }
              </p>
            </div>
          </div>
        )}

      {/* ======================================================
          LOADING
      ====================================================== */}

      {loading && (
        <div className="flex min-h-[280px] items-center justify-center rounded-xl border border-slate-800 bg-slate-900">
          <div className="text-center">
            <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-4 border-slate-700 border-t-white" />

            <p className="text-sm text-slate-400">
              Loading search history...
            </p>
          </div>
        </div>
      )}

      {/* ======================================================
          EMPTY STATE
      ====================================================== */}

      {!loading &&
        !error &&
        searches.length === 0 && (
          <div className="rounded-xl border border-dashed border-slate-700 bg-slate-900 p-12 text-center">
            <h2 className="text-lg font-semibold text-white">
              No search history
            </h2>

            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-400">
              Searches and scheduled monitoring runs will
              appear here after data collection has started.
            </p>
          </div>
        )}

      {/* ======================================================
          SEARCH TABLE
      ====================================================== */}

      {!loading &&
        !error &&
        searches.length > 0 && (
          <section className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900">
            {/* TABLE HEADER */}

            <div className="border-b border-slate-800 px-6 py-5">
              <h2 className="text-lg font-semibold text-white">
                Previous Searches
              </h2>

              <p className="mt-1 text-sm text-slate-400">
                Newest searches are shown first.
              </p>
            </div>

            {/* ==================================================
                DESKTOP TABLE
            ================================================== */}

            <div className="hidden overflow-x-auto md:block">
              <table className="w-full text-left">
                <thead className="border-b border-slate-800 bg-slate-950/60">
                  <tr>
                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      ID
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Keyword
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Status
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Created
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Collected
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Processed
                    </th>

                    <th className="px-6 py-4 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Action
                    </th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-slate-800">
                  {searches.map((search) => (
                    <tr
                      key={search.id}
                      className="transition hover:bg-slate-800/30"
                    >
                      <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-slate-500">
                        #{search.id}
                      </td>

                      <td className="max-w-[260px] px-6 py-4">
                        <p className="truncate text-sm font-medium text-white">
                          {search.keyword}
                        </p>
                      </td>

                      <td className="whitespace-nowrap px-6 py-4">
                        <span
                          className={`rounded-full px-3 py-1 text-xs font-medium ${getStatusClasses(
                            search.status
                          )}`}
                        >
                          {getStatusLabel(
                            search.status
                          )}
                        </span>
                      </td>

                      <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-400">
                        {formatDateTime(
                          search.created_at
                        )}
                      </td>

                      <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-300">
                        {search.total_collected}
                      </td>

                      <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-300">
                        {search.total_processed}
                      </td>

                      <td className="whitespace-nowrap px-6 py-4 text-right">
                        <button
                          type="button"
                          onClick={() =>
                            openSearch(search)
                          }
                          className="rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-medium text-slate-300 transition hover:bg-slate-700 hover:text-white"
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* ==================================================
                MOBILE CARDS
            ================================================== */}

            <div className="divide-y divide-slate-800 md:hidden">
              {searches.map((search) => (
                <article
                  key={search.id}
                  className="p-5"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0">
                      <p className="text-xs text-slate-600">
                        Search #{search.id}
                      </p>

                      <h3 className="mt-1 break-words text-sm font-semibold text-white">
                        {search.keyword}
                      </h3>
                    </div>

                    <span
                      className={`shrink-0 rounded-full px-3 py-1 text-xs font-medium ${getStatusClasses(
                        search.status
                      )}`}
                    >
                      {getStatusLabel(
                        search.status
                      )}
                    </span>
                  </div>

                  <div className="mt-5 grid grid-cols-2 gap-3">
                    <div className="rounded-lg bg-slate-950 p-3">
                      <p className="text-xs text-slate-600">
                        Collected
                      </p>

                      <p className="mt-1 text-sm font-medium text-slate-200">
                        {search.total_collected}
                      </p>
                    </div>

                    <div className="rounded-lg bg-slate-950 p-3">
                      <p className="text-xs text-slate-600">
                        Processed
                      </p>

                      <p className="mt-1 text-sm font-medium text-slate-200">
                        {search.total_processed}
                      </p>
                    </div>
                  </div>

                  <p className="mt-4 text-xs text-slate-500">
                    {formatDateTime(
                      search.created_at
                    )}
                  </p>

                  <button
                    type="button"
                    onClick={() =>
                      openSearch(search)
                    }
                    className="mt-4 w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-2.5 text-sm font-medium text-slate-300 transition hover:bg-slate-700 hover:text-white"
                  >
                    View Search
                  </button>
                </article>
              ))}
            </div>
          </section>
        )}
    </div>
  );
}

export default SearchHistory;