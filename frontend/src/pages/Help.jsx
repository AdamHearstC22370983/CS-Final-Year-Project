function Help() {
  return (
    <div className="container py-5">
      <div className="mb-4">
        <h1 className="mb-2">Help & Privacy</h1>
        <p className="text-muted mb-0">
          Learn how Skillgap works, what data is used, and how recommendations are generated.
        </p>
      </div>

      <div className="row g-4">
        <div className="col-lg-8">
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-body p-4">
              <h3 className="mb-3">How Skillgap Works</h3>
              <p>
                Skillgap compares a user’s CV against a target job description to identify missing
                skills. It then recommends courses that may help bridge those gaps.
              </p>

              <div className="help-step-card mb-3">
                <h5 className="mb-2">1. Upload documents</h5>
                <p className="mb-0 text-muted">
                  A CV and a job description are uploaded through the dashboard.
                </p>
              </div>

              <div className="help-step-card mb-3">
                <h5 className="mb-2">2. Extract skills</h5>
                <p className="mb-0 text-muted">
                  The system extracts skills and related terms from both documents.
                </p>
              </div>

              <div className="help-step-card mb-3">
                <h5 className="mb-2">3. Identify missing skills</h5>
                <p className="mb-0 text-muted">
                  Skills present in the job description but not found in the CV are treated as missing.
                </p>
              </div>

              <div className="help-step-card">
                <h5 className="mb-2">4. Recommend courses</h5>
                <p className="mb-0 text-muted">
                  Courses are ranked using skill overlap and supporting text similarity, with some
                  provider diversity added where useful.
                </p>
              </div>
            </div>
          </div>

          <div className="card shadow-sm border-0 mb-4">
            <div className="card-body p-4">
              <h3 className="mb-3">Understanding Recommendation Labels</h3>

              <div className="mb-3">
                <span className="badge rounded-pill label-pill me-2">Recommended</span>
                <span className="text-muted">Strongest match in the current result set.</span>
              </div>

              <div className="mb-3">
                <span className="badge rounded-pill label-pill me-2">Good match</span>
                <span className="text-muted">Clearly useful and relevant to the missing skills.</span>
              </div>

              <div className="mb-3">
                <span className="badge rounded-pill label-pill me-2">Worth exploring</span>
                <span className="text-muted">Relevant, but narrower or less complete in coverage.</span>
              </div>

              <div className="mb-0">
                <span className="badge rounded-pill label-pill me-2">Exploratory</span>
                <span className="text-muted">Lower-confidence option that may still be useful.</span>
              </div>
            </div>
          </div>

          <div className="card shadow-sm border-0">
            <div className="card-body p-4">
              <h3 className="mb-3">What “Matched Skills” Means</h3>
              <p className="mb-0">
                Matched Skills are the skills from your missing skill list that also appear in the
                course profile. They help explain why a course was recommended.
              </p>
            </div>
          </div>
        </div>

        <div className="col-lg-4">
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-body p-4">
              <h3 className="mb-3">Privacy Summary</h3>
              <p>
                Skillgap is designed to collect only the information needed to support account access
                and recommendation generation.
              </p>

              <h6 className="fw-semibold mt-4">Account data collected</h6>
              <ul className="text-muted small">
                <li>Username</li>
                <li>Email address</li>
                <li>Hashed password</li>
              </ul>

              <h6 className="fw-semibold mt-4">Analysis data used</h6>
              <ul className="text-muted small">
                <li>Uploaded CV content</li>
                <li>Uploaded job description content</li>
                <li>Extracted and missing skills</li>
              </ul>
            </div>
          </div>

          <div className="card shadow-sm border-0 mb-4">
            <div className="card-body p-4">
              <h3 className="mb-3">Security Principles</h3>
              <ul className="text-muted small mb-0">
                <li>Minimal user data collection</li>
                <li>Password hashing</li>
                <li>Protected frontend routes</li>
                <li>Restricted development CORS configuration</li>
                <li>Planned future support for stronger account controls</li>
              </ul>
            </div>
          </div>

          <div className="card shadow-sm border-0">
            <div className="card-body p-4">
              <h3 className="mb-3">Need More Help?</h3>
              <p className="text-muted mb-0">
                Future versions of this page can include FAQs, troubleshooting tips, and guidance
                on how to interpret recommendation results for different job types.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Help;