import { useEffect, useState } from "react";
import api from "../services/api";
import { getCurrentUser } from "../services/auth";
import { toTitleCaseSkill } from "../utils/formatters";

function History() {
  const currentUser = getCurrentUser();

  const [history, setHistory] = useState([]);
  const [historyCount, setHistoryCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadHistory = async () => {
    setLoading(true);
    setError("");

    try {
      if (!currentUser?.user_id) {
        throw new Error("No signed-in user found.");
      }

      const response = await api.get(`/users/${currentUser.user_id}/history`);
      setHistory(response.data.history || []);
      setHistoryCount(response.data.history_count || 0);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to load history.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

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

  return (
    <div className="container py-5">
      <div className="mb-4">
        <h1 className="mb-2">History</h1>
        <p className="text-muted mb-0">
          Review your stored gap-analysis snapshots and the missing skills identified over time.
        </p>
      </div>

      <div className="card shadow-sm border-0 mb-4">
        <div className="card-body p-4 d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
          <div>
            <h5 className="mb-1">Analysis History</h5>
            <p className="text-muted mb-0">
              Each snapshot records the missing skills identified for a previous run.
            </p>
          </div>

          <span className="badge text-bg-light border px-3 py-2">
            {historyCount} snapshot{historyCount === 1 ? "" : "s"}
          </span>
        </div>
      </div>

      {loading && <div className="alert alert-info">Loading history...</div>}
      {error && <div className="alert alert-danger">{error}</div>}

      {!loading && !error && history.length === 0 && (
        <div className="alert alert-warning">
          No history is available yet. Run an analysis from the Dashboard first.
        </div>
      )}

      {!loading &&
        !error &&
        history.map((item) => (
          <div key={item.snapshot_id} className="card shadow-sm border-0 mb-3 history-card">
            <div className="card-body p-4">
              <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-start gap-3 mb-3">
                <div>
                  <h5 className="mb-1">Snapshot #{item.snapshot_id}</h5>
                  <p className="text-muted mb-0">{formatDateTime(item.created_at)}</p>
                </div>

                <span className="badge rounded-pill history-count-pill">
                  {item.missing_count} Missing Skill{item.missing_count === 1 ? "" : "s"}
                </span>
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
                <p className="text-muted mb-0">No missing skills were recorded for this snapshot.</p>
              )}
            </div>
          </div>
        ))}
    </div>
  );
}
export default History;