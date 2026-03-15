import React from "react";

export default function GuidedQuestions({
  experienceLevel,
  setExperienceLevel,
  hasTakenCourse,
  setHasTakenCourse,
  disabled = false,
}) {
  return (
    <div className="card shadow-sm border-0 mb-4">
      <div className="card-body">
        <div className="d-flex align-items-center justify-content-between flex-wrap gap-2 mb-3">
          <div>
            <h5 className="mb-1">Guided Questions</h5>
            <p className="text-muted mb-0">
              These answers help tailor the course recommendations after the gap analysis.
            </p>
          </div>
          <span className="badge text-bg-light border">Optional but helpful</span>
        </div>

        <div className="row g-3">
          <div className="col-md-6">
            <label htmlFor="experienceLevel" className="form-label fw-semibold">
              Your current experience level
            </label>
            <select
              id="experienceLevel"
              className="form-select"
              value={experienceLevel}
              onChange={(e) => setExperienceLevel(e.target.value)}
              disabled={disabled}
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
            <div className="form-text">
              Helps match course difficulty to your background.
            </div>
          </div>

          <div className="col-md-6">
            <label htmlFor="hasTakenCourse" className="form-label fw-semibold">
              Taken similar online courses before?
            </label>
            <select
              id="hasTakenCourse"
              className="form-select"
              value={String(hasTakenCourse)}
              onChange={(e) => setHasTakenCourse(e.target.value === "true")}
              disabled={disabled}
            >
              <option value="false">No</option>
              <option value="true">Yes</option>
            </select>
            <div className="form-text">
              Helps avoid recommending courses that are too basic.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}