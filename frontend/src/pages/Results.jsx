import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import api from "../services/api";
import MissingEntitiesList from "../components/MissingEntitiesList";
import RecommendationCard from "../components/RecommendationCard";
//Results.jsx - Shows the results of the computed skillgap and recommends courses to the user
function Results() {
  const [searchParams] = useSearchParams();

  const userId = searchParams.get("user_id") || "1";
  const experienceLevel = searchParams.get("experience_level") || "";
  const hasTakenCourse = searchParams.get("has_taken_course") || "";

  const [missingEntities, setMissingEntities] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadResults = async () => {
    setLoading(true);
    setError("");

    try {
      const missingResponse = await api.get(`/missing-entities?user_id=${userId}`);

      const recommendationResponse = await api.get("/recommend-courses", {
        params: {
          user_id: userId,
          top_n: 10,
          use_cosine: true,
          experience_level: experienceLevel || undefined,
          has_taken_course:
            hasTakenCourse === ""
              ? undefined
              : hasTakenCourse === "true",
        },
      });

      setMissingEntities(missingResponse.data.missing_entities || []);
      setRecommendations(recommendationResponse.data.recommendations || []);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load results.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadResults();
  }, []);

  return (
    <div className="container py-5">
      <div className="mb-4">
        <h1 className="mb-2">Results</h1>
        <p className="text-muted mb-0">
          Review the missing entities identified and the recommended courses returned by the system.
        </p>
      </div>

      {loading && <div className="alert alert-info">Loading results...</div>}
      {error && <div className="alert alert-danger">{error}</div>}

      {!loading && !error && (
        <>
          <div className="row g-4 mb-4">
            <div className="col-12">
              <MissingEntitiesList entities={missingEntities} />
            </div>
          </div>

          <div className="mb-3">
            <h3>Recommended Courses</h3>
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