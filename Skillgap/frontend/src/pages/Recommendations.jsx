import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import api from "../services/api";
import RecommendationCard from "../components/RecommendationCard";

function Recommendations() {
  const [searchParams] = useSearchParams();

  const experienceLevel = searchParams.get("experience_level") || "";
  const hasTakenCourse = searchParams.get("has_taken_course") || "";

  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [visibleRecommendationCount, setVisibleRecommendationCount] = useState(5);
  const [error, setError] = useState("");

  const visibleRecommendations = useMemo(() => {
    return recommendations.slice(0, visibleRecommendationCount);
  }, [recommendations, visibleRecommendationCount]);

  const remainingRecommendationCount = Math.max(
    recommendations.length - visibleRecommendationCount,
    0
  );

  const loadRecommendations = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/analysis/recommend-courses", {
        params: {
          top_n: 10,
          use_cosine: true,
          experience_level: experienceLevel || undefined,
          has_taken_course: hasTakenCourse === "" ? undefined : hasTakenCourse === "true",
        },
      });

      const recommendationData = response.data || {};

      if (recommendationData.error) {
        setRecommendations([]);
        setError(recommendationData.error);
      } else {
        setRecommendations(recommendationData.recommendations || []);
      }

      setVisibleRecommendationCount(5);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Failed to load recommendations.");
    } finally {
      setLoading(false);
    }
  };

  const handleShowMoreRecommendations = () => {
    setVisibleRecommendationCount((prev) => Math.min(prev + 5, recommendations.length));
  };

  useEffect(() => {
    loadRecommendations();
  }, [experienceLevel, hasTakenCourse]);

  return (
    <div className="container py-5 results-page-shell">
      <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-end gap-3 mb-4">
        <div>
          <h1 className="mb-2">Course Recommendations</h1>
          <p className="text-muted mb-0">
            Explore the strongest course matches based on your reviewed skill gap.
          </p>
        </div>

        <Link
          to={`/review?experience_level=${encodeURIComponent(
            experienceLevel
          )}&has_taken_course=${encodeURIComponent(hasTakenCourse)}`}
          className="btn btn-outline-secondary"
        >
          Back To Manual Skill Confirmation
        </Link>
      </div>

      {loading && <div className="alert alert-info">Loading recommendations...</div>}
      {error && <div className="alert alert-danger">{error}</div>}

      {!loading && (
        <div className="recommendations-section">
          <div className="d-flex justify-content-end mb-3">
            <div className="text-md-end">
              <div className="fw-semibold">
                Showing {visibleRecommendations.length} of {recommendations.length}
              </div>
              <div className="text-muted small">Reveal more results as needed.</div>
            </div>
          </div>

          {recommendations.length === 0 ? (
            <div className="alert alert-warning">
              No recommendations are currently available for this analysis.
            </div>
          ) : (
            <>
              {visibleRecommendations.map((recommendation, index) => (
                <RecommendationCard
                  key={recommendation.course_id || index}
                  recommendation={recommendation}
                />
              ))}

              {remainingRecommendationCount > 0 && (
                <div className="d-flex justify-content-center mt-4">
                  <button
                    type="button"
                    className="btn btn-outline-primary"
                    onClick={handleShowMoreRecommendations}
                  >
                    Show More Recommendations ({remainingRecommendationCount} left)
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
export default Recommendations;