//RecommendationCard.jsx
import { toTitleCaseSkill, formatDurationHours } from "../utils/formatters";
import { getProviderDisplayName, getProviderLogo } from "../utils/providerLogos";
//function to display the reccomendation card to the user
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

  const providerLogo = getProviderLogo(provider);
  const providerDisplayName = getProviderDisplayName(provider);
  const formattedDuration = formatDurationHours(duration);

  return (
    <div className="card shadow-sm border-0 mb-3">
      <div className="card-body">
        <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-start gap-3">
          <div className="d-flex align-items-start gap-3">
            {providerLogo && (
              <div className="provider-logo-frame">
                <img
                  src={providerLogo}
                  alt={`${providerDisplayName} logo`}
                  className="provider-logo"
                />
              </div>
            )}

            <div>
              <h5 className="card-title mb-1">{course_name}</h5>
              <p className="text-muted mb-2">
                {providerDisplayName}
                {organization ? ` • ${organization}` : ""}
              </p>
            </div>
          </div>

          <span className="badge rounded-pill label-pill">
            {recommendation_label || "Exploratory"}
          </span>
        </div>

        <div className="small text-muted mb-2">
          {level ? `Level: ${toTitleCaseSkill(level)}` : "Level: N/A"}
          {formattedDuration ? ` • Duration: ${formattedDuration}` : ""}
          {covers ? ` • Covers: ${covers}` : ""}
        </div>

        <div className="mb-3">
          <span className="fw-semibold d-block mb-2">Matched Skills</span>
          <div className="d-flex flex-wrap gap-2">
            {(matched_skills || []).map((skill, index) => (
              <span
                key={`${skill}-${index}`}
                className="badge rounded-pill matched-skill-pill"
              >
                {toTitleCaseSkill(skill)}
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
            View Course
          </a>
        )}
      </div>
    </div>
  );
}
export default RecommendationCard;