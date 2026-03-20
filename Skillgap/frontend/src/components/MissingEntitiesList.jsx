//MissingEntitiesList.jsx
import { toTitleCaseSkill } from "../utils/formatters";
function MissingEntitiesList({ entities = [] }) {
  return (
    <div className="card shadow-sm border-0 h-100">
      <div className="card-body">
        <h5 className="card-title">Missing Skills</h5>

        {entities.length === 0 ? (
          <p className="text-muted mb-0">No missing skills available yet.</p>
        ) : (
          <div className="d-flex flex-wrap gap-2 mt-3">
            {entities.map((entity, index) => (
              <span key={`${entity}-${index}`} className="badge text-bg-light border px-3 py-2">
                {toTitleCaseSkill(entity)}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
export default MissingEntitiesList;