import { useEffect, useState } from "react";
import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

const INTERVAL_OPTIONS = [
  {
    value: 5,
    label: "Every 5 minutes",
  },
  {
    value: 15,
    label: "Every 15 minutes",
  },
  {
    value: 30,
    label: "Every 30 minutes",
  },
  {
    value: 60,
    label: "Every hour",
  },
  {
    value: 360,
    label: "Every 6 hours",
  },
  {
    value: 720,
    label: "Every 12 hours",
  },
  {
    value: 1440,
    label: "Every 24 hours",
  },
  {
    value: 10080,
    label: "Every 7 days",
  },
];

function formatDateTime(value) {
  if (!value) {
    return "Not run yet";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Unknown";
  }

  return date.toLocaleString();
}

function formatInterval(minutes) {
  if (minutes < 60) {
    return `Every ${minutes} minutes`;
  }

  if (minutes === 60) {
    return "Every hour";
  }

  if (minutes < 1440) {
    const hours = minutes / 60;

    return `Every ${hours} hours`;
  }

  if (minutes === 1440) {
    return "Every 24 hours";
  }

  const days = minutes / 1440;

  return `Every ${days} days`;
}

function Monitoring() {
  const [monitorings, setMonitorings] = useState([]);
  const [keyword, setKeyword] = useState("");
  const [intervalMinutes, setIntervalMinutes] = useState(1440);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [editingInterval, setEditingInterval] = useState(1440);

  // =======================================================
  // LOAD MONITORINGS
  // =======================================================

  async function loadMonitorings() {
    try {
      setLoading(true);
      setError("");

      const response = await axios.get(
        `${API_BASE_URL}/api/monitorings`
      );

      setMonitorings(response.data);
    } catch (err) {
      console.error(
        "Failed to load monitorings:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Failed to load scheduled monitorings."
      );
    } finally {
      setLoading(false);
    }
  }

  // =======================================================
  // INITIAL LOAD
  // =======================================================

  useEffect(() => {
    const timer = setTimeout(() => {
      loadMonitorings();
    }, 0);

    return () => {
      clearTimeout(timer);
    };
  }, []);

  // =======================================================
  // CREATE MONITORING
  // =======================================================

  async function handleCreate(event) {
    event.preventDefault();

    const trimmedKeyword = keyword.trim();

    if (!trimmedKeyword) {
      setError("Please enter a keyword.");
      return;
    }

    try {
      setCreating(true);
      setError("");
      setSuccess("");

      await axios.post(
        `${API_BASE_URL}/api/monitorings`,
        {
          keyword: trimmedKeyword,
          interval_minutes: Number(intervalMinutes),
          is_active: true,
        }
      );

      setKeyword("");
      setIntervalMinutes(1440);

      setSuccess(
        "Scheduled monitoring created successfully."
      );

      await loadMonitorings();
    } catch (err) {
      console.error(
        "Failed to create monitoring:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Failed to create monitoring."
      );
    } finally {
      setCreating(false);
    }
  }

  // =======================================================
  // TOGGLE MONITORING
  // =======================================================

  async function handleToggle(monitoring) {
    try {
      setError("");
      setSuccess("");

      await axios.patch(
        `${API_BASE_URL}/api/monitorings/${monitoring.id}`,
        {
          is_active: !monitoring.is_active,
        }
      );

      setSuccess(
        monitoring.is_active
          ? "Monitoring paused."
          : "Monitoring activated."
      );

      await loadMonitorings();
    } catch (err) {
      console.error(
        "Failed to update monitoring:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Failed to update monitoring."
      );
    }
  }

  // =======================================================
  // START EDITING
  // =======================================================

  function startEditing(monitoring) {
    setEditingId(monitoring.id);
    setEditingInterval(
      monitoring.interval_minutes
    );
    setError("");
    setSuccess("");
  }

  // =======================================================
  // CANCEL EDIT
  // =======================================================

  function cancelEditing() {
    setEditingId(null);
  }

  // =======================================================
  // SAVE INTERVAL
  // =======================================================

  async function saveInterval(monitoringId) {
    try {
      setError("");
      setSuccess("");

      await axios.patch(
        `${API_BASE_URL}/api/monitorings/${monitoringId}`,
        {
          interval_minutes: Number(editingInterval),
        }
      );

      setEditingId(null);

      setSuccess(
        "Monitoring interval updated."
      );

      await loadMonitorings();
    } catch (err) {
      console.error(
        "Failed to update interval:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Failed to update monitoring interval."
      );
    }
  }

  // =======================================================
  // DELETE MONITORING
  // =======================================================

  async function handleDelete(monitoring) {
    const confirmed = window.confirm(
      `Delete monitoring for "${monitoring.keyword}"?`
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");
      setSuccess("");

      await axios.delete(
        `${API_BASE_URL}/api/monitorings/${monitoring.id}`
      );

      setSuccess(
        "Monitoring deleted successfully."
      );

      await loadMonitorings();
    } catch (err) {
      console.error(
        "Failed to delete monitoring:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Failed to delete monitoring."
      );
    }
  }

  return (
    <div className="space-y-8">
      {/* HEADER */}

      <div>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-3xl font-bold text-white">
            Scheduled Monitoring
          </h1>

          <span className="rounded-full bg-blue-500/10 px-3 py-1 text-xs font-medium text-blue-400">
            Automated Collection
          </span>
        </div>

        <p className="mt-2 max-w-3xl text-slate-400">
          Automatically collect and process new public
          mentions for the keywords you want to monitor.
        </p>
      </div>

      {/* CREATE FORM */}

      <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">
        <div className="mb-5">
          <h2 className="text-lg font-semibold text-white">
            Create Monitoring
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Choose a keyword and how frequently the
            platform should collect new mentions.
          </p>
        </div>

        <form
          onSubmit={handleCreate}
          className="grid gap-5 lg:grid-cols-[1fr_240px_auto]"
        >
          {/* KEYWORD */}

          <div>
            <label
              htmlFor="monitoring-keyword"
              className="mb-2 block text-sm font-medium text-slate-300"
            >
              Keyword
            </label>

            <input
              id="monitoring-keyword"
              type="text"
              value={keyword}
              onChange={(event) =>
                setKeyword(event.target.value)
              }
              placeholder="e.g. Samsung Galaxy S26"
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-slate-500"
            />
          </div>

          {/* INTERVAL */}

          <div>
            <label
              htmlFor="monitoring-interval"
              className="mb-2 block text-sm font-medium text-slate-300"
            >
              Collection interval
            </label>

            <select
              id="monitoring-interval"
              value={intervalMinutes}
              onChange={(event) =>
                setIntervalMinutes(
                  Number(event.target.value)
                )
              }
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none focus:border-slate-500"
            >
              {INTERVAL_OPTIONS.map((option) => (
                <option
                  key={option.value}
                  value={option.value}
                >
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* BUTTON */}

          <div className="flex items-end">
            <button
              type="submit"
              disabled={creating}
              className="w-full rounded-lg bg-white px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-50 lg:w-auto"
            >
              {creating
                ? "Creating..."
                : "Create Monitoring"}
            </button>
          </div>
        </form>
      </section>

      {/* MESSAGES */}

      {success && (
        <div className="rounded-lg border border-emerald-900/60 bg-emerald-950/30 px-5 py-4 text-sm text-emerald-300">
          {success}
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-red-900/60 bg-red-950/30 px-5 py-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* MONITORING LIST */}

      <section>
        <div className="mb-5 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white">
              Your Monitorings
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              {monitorings.length} monitoring
              {monitorings.length === 1
                ? ""
                : "s"}{" "}
              configured
            </p>
          </div>

          <button
            type="button"
            onClick={loadMonitorings}
            className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-slate-300 transition hover:bg-slate-800"
          >
            Refresh
          </button>
        </div>

        {/* LOADING */}

        {loading && (
          <div className="flex min-h-[220px] items-center justify-center rounded-xl border border-slate-800 bg-slate-900">
            <div className="text-center">
              <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-4 border-slate-700 border-t-white" />

              <p className="text-sm text-slate-400">
                Loading monitorings...
              </p>
            </div>
          </div>
        )}

        {/* EMPTY */}

        {!loading && monitorings.length === 0 && (
          <div className="rounded-xl border border-dashed border-slate-700 bg-slate-900 p-10 text-center">
            <h3 className="text-lg font-semibold text-white">
              No scheduled monitorings
            </h3>

            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-400">
              Create a monitoring above to
              automatically collect new mentions
              at regular intervals.
            </p>
          </div>
        )}

        {/* MONITORINGS */}

        {!loading && monitorings.length > 0 && (
          <div className="space-y-4">
            {monitorings.map((monitoring) => (
              <article
                key={monitoring.id}
                className="rounded-xl border border-slate-800 bg-slate-900 p-6"
              >
                {/* TOP ROW */}

                <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-3">
                      <h3 className="break-words text-lg font-semibold text-white">
                        {monitoring.keyword}
                      </h3>

                      <span
                        className={`rounded-full px-3 py-1 text-xs font-medium ${
                          monitoring.is_active
                            ? "bg-emerald-500/10 text-emerald-400"
                            : "bg-slate-700 text-slate-400"
                        }`}
                      >
                        {monitoring.is_active
                          ? "Active"
                          : "Paused"}
                      </span>
                    </div>

                    <p className="mt-2 text-sm text-slate-400">
                      {formatInterval(
                        monitoring.interval_minutes
                      )}
                    </p>
                  </div>

                  {/* ACTIONS */}

                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() =>
                        handleToggle(monitoring)
                      }
                      className="rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-sm text-slate-300 transition hover:bg-slate-700"
                    >
                      {monitoring.is_active
                        ? "Pause"
                        : "Activate"}
                    </button>

                    <button
                      type="button"
                      onClick={() =>
                        startEditing(monitoring)
                      }
                      className="rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-sm text-slate-300 transition hover:bg-slate-700"
                    >
                      Edit
                    </button>

                    <button
                      type="button"
                      onClick={() =>
                        handleDelete(monitoring)
                      }
                      className="rounded-lg border border-red-900/60 bg-red-950/20 px-4 py-2 text-sm text-red-400 transition hover:bg-red-950/40"
                    >
                      Delete
                    </button>
                  </div>
                </div>

                {/* EDIT INTERVAL */}

                {editingId === monitoring.id && (
                  <div className="mt-5 rounded-lg border border-slate-800 bg-slate-950 p-4">
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
                      <div className="flex-1">
                        <label
                          htmlFor={`interval-${monitoring.id}`}
                          className="mb-2 block text-sm font-medium text-slate-300"
                        >
                          Collection interval
                        </label>

                        <select
                          id={`interval-${monitoring.id}`}
                          value={editingInterval}
                          onChange={(event) =>
                            setEditingInterval(
                              Number(
                                event.target.value
                              )
                            )
                          }
                          className="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white outline-none focus:border-slate-500"
                        >
                          {INTERVAL_OPTIONS.map(
                            (option) => (
                              <option
                                key={option.value}
                                value={option.value}
                              >
                                {option.label}
                              </option>
                            )
                          )}
                        </select>
                      </div>

                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() =>
                            saveInterval(
                              monitoring.id
                            )
                          }
                          className="rounded-lg bg-white px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-200"
                        >
                          Save
                        </button>

                        <button
                          type="button"
                          onClick={cancelEditing}
                          className="rounded-lg border border-slate-700 bg-slate-800 px-4 py-3 text-sm text-slate-300 transition hover:bg-slate-700"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {/* METRICS */}

                <div className="mt-6 grid gap-4 sm:grid-cols-3">
                  <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                    <p className="text-xs uppercase tracking-wide text-slate-500">
                      Last Run
                    </p>

                    <p className="mt-2 text-sm font-medium text-slate-200">
                      {formatDateTime(
                        monitoring.last_run_at
                      )}
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                    <p className="text-xs uppercase tracking-wide text-slate-500">
                      Next Run
                    </p>

                    <p className="mt-2 text-sm font-medium text-slate-200">
                      {formatDateTime(
                        monitoring.next_run_at
                      )}
                    </p>
                  </div>

                  <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                    <p className="text-xs uppercase tracking-wide text-slate-500">
                      Created
                    </p>

                    <p className="mt-2 text-sm font-medium text-slate-200">
                      {formatDateTime(
                        monitoring.created_at
                      )}
                    </p>
                  </div>
                </div>

                {/* STATUS DESCRIPTION */}

                <div className="mt-5 border-t border-slate-800 pt-5">
                  <p className="text-sm leading-6 text-slate-400">
                    {monitoring.is_active
                      ? "This monitoring is active. New public mentions will be collected automatically according to the configured interval."
                      : "This monitoring is paused. No new scheduled collections will run until it is activated again."}
                  </p>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default Monitoring;