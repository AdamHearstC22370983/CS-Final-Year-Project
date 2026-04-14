import { useEffect, useMemo, useState } from "react";
import api from "../services/api";
import { toTitleCaseSkill } from "../utils/formatters";

function History() {
  const [history, setHistory] = useState([]);
  const [historyCount, setHistoryCount] = useState(0);
  const [visibleCount, setVisibleCount] = useState(10);
  const [loading, setLoading] = useState(true);
  const [deleteLoading, setDeleteLoading] = useState("");
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const loadHistory = async ({ preserveMessages = false } = {}) => {
    setLoading(true);

    if (!preserveMessages) {
      setError("");
      setSuccessMessage("");
    }

    try {
      const response = await api.get("/me/history");
      const nextHistory = response.data?.history || [];
      const nextHistoryCount = response.data?.history_count || 0;

      setHistory(nextHistory);
      setHistoryCount(nextHistoryCount);

      // Keep the visible count between 10 -> 20 range.
      setVisibleCount((prev) => {
        if (nextHistory.length <= 10) {
          return Math.min(10, nextHistory.length || 10);
        }

        return Math.min(prev, 20, nextHistory.length);
      });
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to load history.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const visibleHistory = useMemo(() => {
    return history.slice(0, visibleCount);
  }, [history, visibleCount]);

  const remainingHistoryCount = Math.max(
    Math.min(history.length, 20) - visibleCount,
    0
  );

  const formatDateTime = (value) => {
    if (!value) {
      return "Unknown date";
    }

    const parsed = new Date(value);

    if (Number.isNaN(parsed.getTime())) {
      return value;
    }

    return parsed.toLocaleString();
  };

  const handleShowMore = () => {
    setVisibleCount((prev) => Math.min(prev + 10, 20, history.length));
  };

  const handleDeleteSnapshot = async (snapshotId) => {
    if (!snapshotId) {
      return;
    }

    const confirmed = window.confirm(
      "Are you sure you want to delete this analysis snapshot? This cannot be undone."
    );

    if (!confirmed) {
      return;
    }

    setDeleteLoading(String(snapshotId));
    setError("");
    setSuccessMessage("");

    try {
      await api.delete("/me/history", {
        params: { snapshot_id: snapshotId },
      });

      setSuccessMessage(`Deleted snapshot #${snapshotId}.`);
      await loadHistory({ preserveMessages: true });
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to delete snapshot.");
    } finally {
      setDeleteLoading("");
    }
  };

  return (
    <div className="container py-5 history-page-shell">
      <div className="mb-4">
        <h1 className="mb-2">History</h1>
        <p className="text-muted mb-0">
          Review your stored gap-analysis snapshots and the missing skills identified over time.
        </p>
      </div>

      <div className="card shadow-sm border-0 mb-4 history-summary-card">
        <div className="card-body p-4 d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
          <div>
            <h5 className="mb-1">Analysis History</h5>
            <p className="text-muted mb-0">
              Your most recent 10 snapshots are shown first, with the option to reveal up to 10
              more.
            </p>
          </div>

          <span className="badge text-bg-light border px-3 py-2 history-summary-pill">
            {historyCount} snapshot{historyCount === 1 ? "" : "s"}
          </span>
        </div>
      </div>

      {loading && <div className="alert alert-info">Loading history...</div>}
      {error && <div className="alert alert-danger">{error}</div>}
      {successMessage && <div className="alert alert-success">{successMessage}</div>}

      {!loading && !error && history.length === 0 && (
        <div className="alert alert-warning history-empty-card">
          No history is available yet. Run an analysis from the Dashboard first.
        </div>
      )}

      {!loading && !error && history.length > 0 && (
        <>
          <div className="d-flex justify-content-end mb-3">
            <div className="text-md-end">
              <div className="fw-semibold">
                Showing {visibleHistory.length} of {Math.min(history.length, 20)}
              </div>
              <div className="text-muted small">
                The history page currently reveals up to 20 snapshots at a time.
              </div>
            </div>
          </div>

          {visibleHistory.map((item) => (
            <div key={item.snapshot_id} className="card shadow-sm border-0 mb-3 history-card">
              <div className="card-body p-4">
                <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-start gap-3 mb-3">
                  <div>
                    <h5 className="mb-1">Snapshot #{item.snapshot_id}</h5>
                    <p className="text-muted mb-0">{formatDateTime(item.created_at)}</p>
                  </div>

                  <div className="d-flex flex-column flex-sm-row align-items-sm-center gap-2">
                    <span className="badge rounded-pill history-count-pill">
                      {item.missing_count} Missing Skill{item.missing_count === 1 ? "" : "s"}
                    </span>

                    <button
                      type="button"
                      className="btn btn-sm btn-outline-danger"
                      onClick={() => handleDeleteSnapshot(item.snapshot_id)}
                      disabled={deleteLoading === String(item.snapshot_id)}
                    >
                      {deleteLoading === String(item.snapshot_id) ? "Deleting..." : "Delete"}
                    </button>
                  </div>
                </div>

                {item.missing_entities?.length ? (
                  <div className="d-flex flex-wrap gap-2">
                    {item.missing_entities.map((skill, index) => (
                      <span
                        key={`${item.snapshot_id}-${skill}-${index}`}
                        className="badge rounded-pill matched-skill-pill"
                      >
                        {toTitleCaseSkill(skill)}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted mb-0">
                    No missing skills were recorded for this snapshot.
                  </p>
                )}
              </div>
            </div>
          ))}

          {remainingHistoryCount > 0 && (
            <div className="d-flex justify-content-center mt-4">
              <button
                type="button"
                className="btn btn-outline-primary"
                onClick={handleShowMore}
              >
                Show 10 More
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default History;