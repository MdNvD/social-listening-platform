import { useEffect, useState } from "react";
import axios from "axios";

import { useSearch } from "../context/useSearch";

// =========================================================
// API
// =========================================================

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

// =========================================================
// Main Component
// =========================================================

function Alerts() {
  const { activeSearch } = useSearch();

  const searchId = activeSearch?.id;

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // =========================================================
  // Load alerts whenever active search changes
  // =========================================================

  useEffect(() => {
    // There is nothing to load when no search is selected.
    // The UI handles this state directly during render.
    if (!searchId) {
      return;
    }

    let cancelled = false;

    async function loadCurrentAlerts() {
      try {
        setLoading(true);
        setError("");
        setData(null);

        const response = await axios.get(
          `${API_BASE_URL}/api/searches/${searchId}/alerts`
        );

        if (!cancelled) {
          setData(response.data);
        }
      } catch (error) {
        console.error(
          "Alerts loading error:",
          error
        );

        if (!cancelled) {
          setError(
            error.response?.data?.detail ||
              error.message ||
              "Failed to load alerts."
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadCurrentAlerts();

    return () => {
      cancelled = true;
    };
  }, [searchId]);

  // =========================================================
  // Manual refresh
  // =========================================================

  const loadAlerts = async (id) => {
    if (!id) {
      setData(null);
      setError("No active search selected.");

      return;
    }

    try {
      setLoading(true);
      setError("");
      setData(null);

      const response = await axios.get(
        `${API_BASE_URL}/api/searches/${id}/alerts`
      );

      setData(response.data);
    } catch (error) {
      console.error(
        "Alerts loading error:",
        error
      );

      setError(
        error.response?.data?.detail ||
          error.message ||
          "Failed to load alerts."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // No Active Search
  // =========================================================

  if (!searchId) {
    return (
      <div className="space-y-6">
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-3xl font-bold text-white">
              Alerts
            </h1>

            <span className="rounded-full bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-400">
              Monitoring
            </span>
          </div>

          <p className="mt-2 text-sm text-slate-400">
            Monitor significant changes in sentiment activity
            using deterministic statistical rules.
          </p>

          <p className="mt-1 text-xs text-slate-600">
            Alerts are generated only when the available
            evidence satisfies the configured thresholds.
          </p>
        </div>

        <section className="rounded-xl border border-slate-800 bg-slate-900 p-8">
          <div className="text-center">
            <h2 className="text-lg font-semibold text-white">
              No active search selected
            </h2>

            <p className="mt-2 text-sm text-slate-500">
              Run a search or select a previous search from
              Search History to view alerts.
            </p>
          </div>
        </section>
      </div>
    );
  }

  // =========================================================
  // Loading
  // =========================================================

  if (loading) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-700 border-t-blue-500" />

          <h2 className="mt-5 text-lg font-semibold text-white">
            Checking alerts...
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            Comparing recent and previous sentiment activity.
          </p>
        </div>
      </div>
    );
  }

  // =========================================================
  // Render
  // =========================================================

  return (
    <div className="space-y-6">
      {/* =====================================================
          Header
      ===================================================== */}

      <div>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-3xl font-bold text-white">
            Alerts
          </h1>

          <span className="rounded-full bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-400">
            Monitoring
          </span>
        </div>

        <p className="mt-2 text-sm text-slate-400">
          Monitor significant changes in sentiment activity
          using deterministic statistical rules.
        </p>

        <p className="mt-1 text-xs text-slate-600">
          Alerts are generated only when the available
          evidence satisfies the configured thresholds.
        </p>
      </div>

      {/* =====================================================
          Active Search
      ===================================================== */}

      <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">
              Active Search
            </p>

            <h2 className="mt-1 text-xl font-semibold text-white">
              {activeSearch?.keyword || "No search selected"}
            </h2>

            <p className="mt-1 text-xs text-slate-600">
              Search #{searchId || "—"}
            </p>
          </div>

          {searchId && (
            <button
              type="button"
              onClick={() => loadAlerts(searchId)}
              disabled={loading}
              className="rounded-lg border border-slate-700 bg-slate-950 px-4 py-2 text-sm font-medium text-slate-300 transition hover:bg-slate-800 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
            >
              Refresh
            </button>
          )}
        </div>
      </section>

      {/* =====================================================
          Error
      ===================================================== */}

      {error && (
        <div className="rounded-lg border border-red-900/50 bg-red-950/30 p-4">
          <p className="text-sm text-red-400">
            {error}
          </p>
        </div>
      )}

      {/* =====================================================
          Results
      ===================================================== */}

      {data && searchId && (
        <AlertResults data={data} />
      )}
    </div>
  );
}

// ===========================================================
// Alert Results
// ===========================================================

function AlertResults({ data }) {
  const summary = data.summary || {};
  const alerts = data.alerts || [];

  const recentRate =
    Number(summary.recent_negative_rate || 0) * 100;

  const previousRate =
    Number(summary.previous_negative_rate || 0) * 100;

  const rateChange =
    Number(summary.negative_rate_change || 0) * 100;

  return (
    <div className="space-y-6">
      {/* ===================================================
          Search Information
      =================================================== */}

      <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">
              Monitoring
            </p>

            <h2 className="mt-1 text-xl font-semibold text-white">
              {data.keyword}
            </h2>

            <p className="mt-1 text-xs text-slate-600">
              Search #{data.search_id}
            </p>
          </div>

          {alerts.length > 0 ? (
            <span className="rounded-full bg-red-500/10 px-3 py-1.5 text-xs font-semibold text-red-400">
              {alerts.length} Alert
              {alerts.length === 1 ? "" : "s"}
            </span>
          ) : (
            <span className="rounded-full bg-slate-700/50 px-3 py-1.5 text-xs font-semibold text-slate-300">
              No Alerts
            </span>
          )}
        </div>
      </section>

      {/* ===================================================
          Alert Status
      =================================================== */}

      {alerts.length === 0 ? (
        <NoAlerts />
      ) : (
        <ActiveAlerts alerts={alerts} />
      )}

      {/* ===================================================
          Statistics
      =================================================== */}

      <section>
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-white">
            Sentiment Monitoring
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Recent period compared with the previous period.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <StatCard
            label="Recent Mentions"
            value={summary.recent_mentions || 0}
          />

          <StatCard
            label="Recent Negative"
            value={
              summary.recent_negative_mentions || 0
            }
            valueClass="text-red-400"
          />

          <StatCard
            label="Recent Negative Rate"
            value={`${recentRate.toFixed(1)}%`}
          />

          <StatCard
            label="Negative Rate Change"
            value={`${
              rateChange >= 0 ? "+" : ""
            }${rateChange.toFixed(
              1
            )} percentage points`}
            valueClass={
              rateChange > 0
                ? "text-red-400"
                : rateChange < 0
                  ? "text-emerald-400"
                  : "text-slate-300"
            }
          />
        </div>
      </section>

      {/* ===================================================
          Data Sufficiency
      =================================================== */}

      <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">
        <div className="mb-5">
          <h2 className="text-lg font-semibold text-white">
            Alert Data Sufficiency
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Alert conditions require enough observations
            in both monitoring periods.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <DataStatusCard
            label="Recent Period"
            sufficient={summary.enough_recent_data}
            message={
              summary.enough_recent_data
                ? "Enough recent data"
                : "More recent mentions are required"
            }
          />

          <DataStatusCard
            label="Previous Period"
            sufficient={summary.enough_previous_data}
            message={
              summary.enough_previous_data
                ? "Enough baseline data"
                : "More baseline data is required"
            }
          />
        </div>
      </section>

      {/* ===================================================
          Period Comparison
      =================================================== */}

      <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-white">
            Period Comparison
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Negative sentiment rate across the two monitoring
            periods.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <PeriodCard
            title="Recent Period"
            mentions={summary.recent_mentions || 0}
            negative={
              summary.recent_negative_mentions || 0
            }
            rate={recentRate}
          />

          <PeriodCard
            title="Previous Period"
            mentions={summary.previous_mentions || 0}
            negative={
              summary.previous_negative_mentions || 0
            }
            rate={previousRate}
          />
        </div>

        <div className="mt-6 rounded-lg border border-slate-800 bg-slate-950 p-4">
          <p className="text-xs leading-5 text-slate-500">
            A negative sentiment alert is not generated
            simply because negative mentions exist. The
            backend requires sufficient recent data,
            sufficient previous-period data, and at least
            a 20 percentage-point increase in the negative
            sentiment rate.
          </p>
        </div>
      </section>

      {/* ===================================================
          Monitoring Period
      =================================================== */}

      {data.period && (
        <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">
          <h2 className="text-lg font-semibold text-white">
            Monitoring Period
          </h2>

          <div className="mt-4 grid gap-4 md:grid-cols-3">
            <DateCard
              label="Recent Period Start"
              value={formatDate(
                data.period.recent_start
              )}
            />

            <DateCard
              label="Previous Period Start"
              value={formatDate(
                data.period.previous_start
              )}
            />

            <DateCard
              label="Checked Until"
              value={formatDate(data.period.end)}
            />
          </div>
        </section>
      )}
    </div>
  );
}

// ===========================================================
// Data Status Card
// ===========================================================

function DataStatusCard({
  label,
  sufficient,
  message,
}) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950 p-5">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-slate-300">
            {label}
          </p>

          <p className="mt-1 text-xs text-slate-600">
            {message}
          </p>
        </div>

        <span
          className={
            sufficient
              ? "rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-400"
              : "rounded-full bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-400"
          }
        >
          {sufficient ? "Ready" : "Insufficient"}
        </span>
      </div>
    </div>
  );
}

// ===========================================================
// No Alerts
// ===========================================================

function NoAlerts() {
  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900 p-8">
      <div className="flex flex-col items-center text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-800 text-xl text-slate-400">
          —
        </div>

        <h2 className="mt-4 text-lg font-semibold text-white">
          No alerts detected
        </h2>

        <p className="mt-2 max-w-xl text-sm leading-6 text-slate-500">
          No configured alert condition was triggered
          for this search using the available recent
          and previous period data.
        </p>

        <p className="mt-3 text-xs text-slate-600">
          This does not mean there are no negative
          mentions. It means the configured alert
          threshold was not met.
        </p>
      </div>
    </section>
  );
}

// ===========================================================
// Active Alerts
// ===========================================================

function ActiveAlerts({ alerts }) {
  return (
    <section>
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-white">
          Active Alerts
        </h2>

        <p className="mt-1 text-sm text-slate-500">
          Conditions detected by the alert engine.
        </p>
      </div>

      <div className="space-y-4">
        {alerts.map((alert, index) => (
          <div
            key={`${alert.type}-${index}`}
            className="rounded-xl border border-red-900/50 bg-red-950/20 p-6"
          >
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-md bg-red-500/10 px-2 py-1 text-xs font-semibold text-red-400">
                    {alert.severity || "Alert"}
                  </span>

                  <span className="text-xs text-slate-600">
                    {alert.type}
                  </span>
                </div>

                <h3 className="mt-3 text-lg font-semibold text-white">
                  {alert.title}
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-400">
                  {alert.description}
                </p>
              </div>
            </div>

            {alert.evidence && (
              <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                <EvidenceMetric
                  label="Recent Mentions"
                  value={
                    alert.evidence.recent_mentions
                  }
                />

                <EvidenceMetric
                  label="Recent Negative"
                  value={
                    alert.evidence
                      .recent_negative_mentions
                  }
                />

                <EvidenceMetric
                  label="Recent Negative Rate"
                  value={`${(
                    Number(
                      alert.evidence
                        .recent_negative_rate || 0
                    ) * 100
                  ).toFixed(1)}%`}
                />

                <EvidenceMetric
                  label="Previous Mentions"
                  value={
                    alert.evidence.previous_mentions
                  }
                />

                <EvidenceMetric
                  label="Previous Negative"
                  value={
                    alert.evidence
                      .previous_negative_mentions
                  }
                />

                <EvidenceMetric
                  label="Negative Rate Change"
                  value={`${
                    Number(
                      alert.evidence.rate_change || 0
                    ) >= 0
                      ? "+"
                      : ""
                  }${(
                    Number(
                      alert.evidence.rate_change || 0
                    ) * 100
                  ).toFixed(
                    1
                  )} percentage points`}
                />
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

// ===========================================================
// Stat Card
// ===========================================================

function StatCard({
  label,
  value,
  valueClass = "text-white",
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
      <p className="text-xs uppercase tracking-wide text-slate-500">
        {label}
      </p>

      <p
        className={`mt-2 text-2xl font-bold ${valueClass}`}
      >
        {value}
      </p>
    </div>
  );
}

// ===========================================================
// Period Card
// ===========================================================

function PeriodCard({
  title,
  mentions,
  negative,
  rate,
}) {
  const safeRate = Number.isFinite(rate)
    ? Math.max(0, Math.min(rate, 100))
    : 0;

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950 p-5">
      <h3 className="font-semibold text-white">
        {title}
      </h3>

      <div className="mt-5 grid grid-cols-3 gap-4">
        <div>
          <p className="text-xs text-slate-500">
            Mentions
          </p>

          <p className="mt-1 text-xl font-bold text-white">
            {mentions}
          </p>
        </div>

        <div>
          <p className="text-xs text-slate-500">
            Negative
          </p>

          <p className="mt-1 text-xl font-bold text-red-400">
            {negative}
          </p>
        </div>

        <div>
          <p className="text-xs text-slate-500">
            Negative Rate
          </p>

          <p className="mt-1 text-xl font-bold text-white">
            {safeRate.toFixed(1)}%
          </p>
        </div>
      </div>

      <div className="mt-5 h-2 overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full rounded-full bg-red-500 transition-all"
          style={{
            width: `${safeRate}%`,
          }}
        />
      </div>
    </div>
  );
}

// ===========================================================
// Evidence Metric
// ===========================================================

function EvidenceMetric({
  label,
  value,
}) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
      <p className="text-xs text-slate-500">
        {label}
      </p>

      <p className="mt-1 text-lg font-semibold text-white">
        {value ?? 0}
      </p>
    </div>
  );
}

// ===========================================================
// Date Card
// ===========================================================

function DateCard({
  label,
  value,
}) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
      <p className="text-xs text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-sm text-slate-300">
        {value}
      </p>
    </div>
  );
}

// ===========================================================
// Date Formatter
// ===========================================================

function formatDate(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

// ===========================================================
// Export
// ===========================================================

export default Alerts;