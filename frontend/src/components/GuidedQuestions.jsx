//GuidedQuestions.jsx
function GuidedQuestions({
  experienceLevel,
  setExperienceLevel,
  hasTakenCourse,
  setHasTakenCourse,
}) {
  return (
    <div className="card shadow-sm border-0">
      <div className="card-body">
        <h5 className="card-title">Guided Questions</h5>
        <p className="text-muted">
          These answers help tailor recommendations to the user’s level.
        </p>

        <div className="mb-3">
          <label className="form-label fw-semibold">Experience level</label>
          <select
            className="form-select"
            value={experienceLevel}
            onChange={(e) => setExperienceLevel(e.target.value)}
          >
            <option value="">Select level</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>

        <div>
          <label className="form-label fw-semibold">
            Have you taken a course in this area before?
          </label>
          <select
            className="form-select"
            value={hasTakenCourse}
            onChange={(e) => setHasTakenCourse(e.target.value)}
          >
            <option value="">Select option</option>
            <option value="true">Yes</option>
            <option value="false">No</option>
          </select>
        </div>
      </div>
    </div>
  );
}
export default GuidedQuestions;