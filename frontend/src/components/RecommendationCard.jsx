//RecommendationCard.jsx
function RecommendationCard({ recommendation }) {
  const {
    course_name,
    provider,
    organization,
    level,
    duration,
    recommendation_label,
    covers,
    matched_skills,
    url,
  } = recommendation;

  return (
    <div className="card shadow-sm border-0 mb-3">
      <div className="card-body">
        <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-start gap-3">
          <div>
            <h5 className="card-title mb-1">{course_name}</h5>
            <p className="text-muted mb-2">
              {provider}
              {organization ? ` • ${organization}` : ""}
            </p>
          </div>

          <span className="badge rounded-pill label-pill">
            {recommendation_label || "Exploratory"}
          </span>
        </div>

        <div className="small text-muted mb-2">
          {level ? `Level: ${level}` : "Level: N/A"}
          {duration ? ` • Duration: ${duration}` : ""}
          {covers ? ` • Covers: ${covers}` : ""}
        </div>

        <div className="mb-3">
          <span className="fw-semibold d-block mb-2">Matched entities</span>
          <div className="d-flex flex-wrap gap-2">
            {(matched_skills || []).map((skill, index) => (
              <span key={`${skill}-${index}`} className="badge text-bg-info-subtle border">
                {skill}
              </span>
            ))}
          </div>
        </div>

        {url && (
          <a
            href={url}
            target="_blank"
            rel="noreferrer"
            className="btn btn-sm btn-primary"
          >
            View course
          </a>
        )}
      </div>
    </div>
  );
}
export default RecommendationCard;