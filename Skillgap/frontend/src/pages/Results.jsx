import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import api from "../services/api";
import RecommendationCard from "../components/RecommendationCard";
import { toTitleCaseSkill } from "../utils/formatters";

function Results() {
  const [searchParams] = useSearchParams();

  const experienceLevel = searchParams.get("experience_level") || "";
  const hasTakenCourse = searchParams.get("has_taken_course") || "";

  const [missingEntities, setMissingEntities] = useState([]);
  const [confirmedSkills, setConfirmedSkills] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState("");
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const loadResults = async () => {
    setLoading(true);
    setError("");
    setSuccessMessage("");

    try {
      const [missingResponse, recommendationResponse, confirmedResponse] = await Promise.all([
        api.get("/analysis/missing-entities"),
        api.get("/analysis/recommend-courses", {
          params: {
            top_n: 10,
            use_cosine: true,
            experience_level: experienceLevel || undefined,
            has_taken_course:
              hasTakenCourse === "" ? undefined : hasTakenCourse === "true",
          },
        }),
        api.get("/me/confirmed-skills"),
      ]);

      const recommendationData = recommendationResponse.data || {};

      if (recommendationData.error) {
        setRecommendations([]);
        setError(recommendationData.error);
      } else {
        setRecommendations(recommendationData.recommendations || []);
      }

      setMissingEntities(missingResponse.data?.missing_entities || []);
      setConfirmedSkills(confirmedResponse.data?.confirmed_skills || []);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to load results.");
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

      setSuccessMessage(`Confirmed "${skill}" as already known.`);
      await loadResults();
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

      setSuccessMessage(`Removed confirmation for "${skill}".`);
      await loadResults();
    } catch (err) {
      setError(
        err.response?.data?.detail || err.message || "Failed to remove confirmation."
      );
    } finally {
      setActionLoading("");
    }
  };

  useEffect(() => {
    loadResults();
  }, [experienceLevel, hasTakenCourse]);

  return (
    <div className="container py-5">
      <div className="mb-4">
        <h1 className="mb-2">Results</h1>
        <p className="text-muted mb-0">
          Review the missing skills identified and the recommended courses returned by the system.
        </p>
      </div>

      {loading && <div className="alert alert-info">Loading results...</div>}
      {error && <div className="alert alert-danger">{error}</div>}
      {successMessage && <div className="alert alert-success">{successMessage}</div>}

      {!loading && (
        <>
          <div className="row g-4 mb-4">
            <div className="col-lg-7">
              <div className="card shadow-sm border-0 h-100">
                <div className="card-body p-4">
                  <div className="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
                    <div>
                      <h3 className="mb-1">Missing Skills</h3>
                      <p className="text-muted mb-0">
                        Click a skill if you already have it but forgot to include it on your CV.
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
                    <div className="results-skill-list">
                      {missingEntities.map((skill) => (
                        <div key={skill} className="results-skill-row">
                          <div className="results-skill-name">{toTitleCaseSkill(skill)}</div>

                          <div className="results-skill-actions">
                            <button
                              className="btn btn-sm btn-outline-success"
                              onClick={() => handleConfirmSkill(skill)}
                              disabled={actionLoading === skill}
                            >
                              {actionLoading === skill ? "Updating..." : "I already have this"}
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="col-lg-5">
              <div className="card shadow-sm border-0 h-100">
                <div className="card-body p-4">
                  <div className="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
                    <div>
                      <h3 className="mb-1">Confirmed by You</h3>
                      <p className="text-muted mb-0">
                        Skills you manually confirmed as already known.
                      </p>
                    </div>
                    <span className="badge text-bg-light border">
                      {confirmedSkills.length} confirmed
                    </span>
                  </div>

                  {confirmedSkills.length === 0 ? (
                    <div className="text-muted">No manually confirmed skills yet.</div>
                  ) : (
                    <div className="results-skill-list">
                      {confirmedSkills.map((skill) => (
                        <div key={skill} className="results-skill-row">
                          <div className="results-skill-name">{toTitleCaseSkill(skill)}</div>

                          <div className="results-skill-actions">
                            <button
                              className="btn btn-sm btn-outline-danger"
                              onClick={() => handleUndoSkill(skill)}
                              disabled={actionLoading === skill}
                            >
                              {actionLoading === skill ? "Updating..." : "Undo"}
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="mb-3">
            <h3>Recommended Courses</h3>
            <p className="text-muted mb-0">
              Recommendations refresh automatically based on the adjusted missing-skill list.
            </p>
          </div>

          {recommendations.length === 0 ? (
            <div className="alert alert-warning">No recommendations available.</div>
          ) : (
            recommendations.map((recommendation, index) => (
              <RecommendationCard
                key={recommendation.course_id || index}
                recommendation={recommendation}
              />
            ))
          )}
        </>
      )}
    </div>
  );
}

export default Results;