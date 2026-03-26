import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import api from "../services/api";
import { toTitleCaseSkill } from "../utils/formatters";

function Review() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const experienceLevel = searchParams.get("experience_level") || "";
  const hasTakenCourse = searchParams.get("has_taken_course") || "";

  const [missingEntities, setMissingEntities] = useState([]);
  const [confirmedSkills, setConfirmedSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState("");
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const totalReviewedSkills = useMemo(() => {
    return missingEntities.length + confirmedSkills.length;
  }, [missingEntities, confirmedSkills]);

  const loadReview = async ({ preserveMessages = false } = {}) => {
    setLoading(true);

    if (!preserveMessages) {
      setError("");
      setSuccessMessage("");
    }

    try {
      const [missingResponse, confirmedResponse] = await Promise.all([
        api.get("/analysis/missing-entities"),
        api.get("/me/confirmed-skills"),
      ]);

      setMissingEntities(missingResponse.data?.missing_entities || []);
      setConfirmedSkills(confirmedResponse.data?.confirmed_skills || []);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to load review page.");
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmSkill = async (skill) => {
    if (!skill) {
      return;
    }

    setActionLoading(skill);
    setError("");
    setSuccessMessage("");

    try {
      await api.post("/me/confirmed-skills", {
        skill_name: skill,
      });

      setSuccessMessage(`Confirmed "${toTitleCaseSkill(skill)}" as already known.`);
      await loadReview({ preserveMessages: true });
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to confirm skill.");
    } finally {
      setActionLoading("");
    }
  };

  const handleUndoSkill = async (skill) => {
    if (!skill) {
      return;
    }

    setActionLoading(skill);
    setError("");
    setSuccessMessage("");

    try {
      await api.delete("/me/confirmed-skills", {
        params: { skill_name: skill },
      });

      setSuccessMessage(`Removed confirmation for "${toTitleCaseSkill(skill)}".`);
      await loadReview({ preserveMessages: true });
    } catch (err) {
      setError(
        err.response?.data?.detail || err.message || "Failed to remove confirmation."
      );
    } finally {
      setActionLoading("");
    }
  };

  const goToRecommendations = () => {
    navigate(
      `/recommendations?experience_level=${encodeURIComponent(
        experienceLevel
      )}&has_taken_course=${encodeURIComponent(hasTakenCourse)}`
    );
  };

  useEffect(() => {
    loadReview();
  }, [experienceLevel, hasTakenCourse]);

  return (
    <div className="container py-5 results-page-shell">
      <div className="card shadow-sm border-0 mb-4 results-summary-card">
        <div className="card-body p-4">
          <div className="d-flex flex-column flex-lg-row justify-content-between align-items-lg-start gap-4">
            <div>
              <h1 className="mb-2">Review Your Skill Gap</h1>
              <p className="text-muted mb-0">
                Confirm any technical skills you already have before moving to course
                recommendations.
              </p>
            </div>

            <div className="d-flex flex-wrap gap-2 results-summary-stats">
              <span className="badge text-bg-light border px-3 py-2 results-summary-stat">
                {missingEntities.length} Missing
              </span>
              <span className="badge text-bg-light border px-3 py-2 results-summary-stat">
                {confirmedSkills.length} Confirmed
              </span>
              <span className="badge text-bg-light border px-3 py-2 results-summary-stat">
                {totalReviewedSkills} Total Reviewed
              </span>
            </div>
          </div>
        </div>
      </div>

      {loading && <div className="alert alert-info">Loading review...</div>}
      {error && <div className="alert alert-danger">{error}</div>}
      {successMessage && <div className="alert alert-success">{successMessage}</div>}

      {!loading && (
        <div className="row g-4">
          <div className="col-lg-7">
            <div className="card shadow-sm border-0 h-100 results-panel-card">
              <div className="card-body p-4">
                <div className="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
                  <div>
                    <h3 className="mb-1">Skills To Confirm</h3>
                    <p className="text-muted mb-0">
                      Confirm technical skills you already have but may not have included on your
                      CV.
                    </p>
                  </div>

                  <span className="badge text-bg-light border">
                    {missingEntities.length} remaining
                  </span>
                </div>

                {missingEntities.length === 0 ? (
                  <div className="alert alert-success mb-0">
                    No missing skills are currently being shown.
                  </div>
                ) : (
                  <div className="results-chip-grid">
                    {missingEntities.map((skill) => (
                      <div key={skill} className="results-skill-chip">
                        <span className="results-skill-chip-name">
                          {toTitleCaseSkill(skill)}
                        </span>

                        <button
                          type="button"
                          className="btn btn-sm btn-outline-success skill-confirm-btn"
                          onClick={() => handleConfirmSkill(skill)}
                          disabled={actionLoading === skill}
                          title={`Confirm ${toTitleCaseSkill(skill)}`}
                          aria-label={`Confirm ${toTitleCaseSkill(skill)}`}
                        >
                          {actionLoading === skill ? "..." : "✓"}
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="col-lg-5">
            <div className="card shadow-sm border-0 h-100 results-panel-card">
              <div className="card-body p-4">
                <div className="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
                  <div>
                    <h3 className="mb-1">Confirmed Skills</h3>
                    <p className="text-muted mb-0">
                      Skills you have manually confirmed as already known.
                    </p>
                  </div>

                  <span className="badge text-bg-light border">
                    {confirmedSkills.length} confirmed
                  </span>
                </div>

                {confirmedSkills.length === 0 ? (
                  <div className="text-muted">No manually confirmed skills yet.</div>
                ) : (
                  <div className="results-chip-grid">
                    {confirmedSkills.map((skill) => (
                      <div
                        key={skill}
                        className="results-skill-chip results-skill-chip-confirmed"
                      >
                        <span className="results-skill-chip-name">
                          {toTitleCaseSkill(skill)}
                        </span>

                        <button
                          type="button"
                          className="btn btn-sm btn-outline-danger skill-undo-btn"
                          onClick={() => handleUndoSkill(skill)}
                          disabled={actionLoading === skill}
                          title={`Undo ${toTitleCaseSkill(skill)}`}
                          aria-label={`Undo ${toTitleCaseSkill(skill)}`}
                        >
                          {actionLoading === skill ? "..." : "↺"}
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                <div className="mt-4 pt-2 border-top">
                  <button
                    type="button"
                    className="btn btn-primary w-100"
                    onClick={goToRecommendations}
                    disabled={loading}
                  >
                    Generate Recommendations
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Review;