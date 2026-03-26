// RecommendationCard.jsx
import { toTitleCaseSkill, formatDurationHours } from "../utils/formatters";
import { getProviderDisplayName, getProviderLogo } from "../utils/providerLogos";

// Function to display a recommendation card to the user.
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
    rating,
    nu_reviews,
    enrollments,
    subject,
    type,
  } = recommendation;

  const providerLogo = getProviderLogo(provider);
  const providerDisplayName = getProviderDisplayName(provider);
  const formattedDuration = formatDurationHours(duration);

  return (
    <div className="card shadow-sm border-0 mb-3 recommendation-card-compact">
      <div className="card-body p-4">
        <div className="d-flex flex-column flex-lg-row justify-content-between align-items-lg-start gap-3">
          <div className="d-flex align-items-start gap-3 flex-grow-1">
            {providerLogo && (
              <div className="provider-logo-frame">
                <img
                  src={providerLogo}
                  alt={`${providerDisplayName} logo`}
                  className="provider-logo"
                />
              </div>
            )}

            <div className="recommendation-main-content">
              <div className="d-flex flex-wrap align-items-center gap-2 mb-2">
                <h4 className="card-title mb-0 recommendation-course-title">{course_name}</h4>

                <span className="badge rounded-pill label-pill recommendation-label-pill">
                  {recommendation_label || "Exploratory"}
                </span>
              </div>

              <div className="recommendation-provider-line text-muted mb-2">
                <span className="recommendation-provider-name">{providerDisplayName}</span>
                {organization ? ` • ${organization}` : ""}
                {type ? ` • ${toTitleCaseSkill(type)}` : ""}
                {subject ? ` • ${toTitleCaseSkill(subject)}` : ""}
              </div>

              <div className="recommendation-meta-row small text-muted mb-3">
                <span>{level ? `Level: ${toTitleCaseSkill(level)}` : "Level: N/A"}</span>
                {formattedDuration ? <span>Duration: {formattedDuration}</span> : null}
                {covers ? <span>Covers: {covers}</span> : null}
                {typeof rating === "number" ? <span>Rating: {rating}</span> : null}
                {typeof nu_reviews === "number" ? <span>Reviews: {nu_reviews}</span> : null}
                {typeof enrollments === "number" ? <span>Enrolments: {enrollments}</span> : null}
              </div>

              {!!matched_skills?.length && (
                <div className="mb-0">
                  <span className="fw-semibold d-block mb-2 recommendation-skill-heading">
                    Matched Skills
                  </span>

                  <div className="d-flex flex-wrap gap-2">
                    {matched_skills.map((skill, index) => (
                      <span
                        key={`${skill}-${index}`}
                        className="badge rounded-pill matched-skill-pill"
                      >
                        {toTitleCaseSkill(skill)}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="recommendation-cta-wrap">
            {url && (
              <a
                href={url}
                target="_blank"
                rel="noreferrer"
                className="btn btn-primary recommendation-cta"
              >
                View Course
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default RecommendationCard;