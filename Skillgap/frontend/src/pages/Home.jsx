import { Link } from "react-router-dom";
import { getCurrentUser } from "../services/auth";

function Home() {
  const currentUser = getCurrentUser();

  return (
    <div className="home-page-shell">
      <section className="hero-section py-5">
        <div className="container py-4">
          {!currentUser ? (
            <div className="row align-items-center g-4">
              <div className="col-lg-7">
                <h1 className="display-5 fw-bold mb-3">
                  Identify skill gaps and discover relevant learning pathways
                </h1>

                <p className="lead text-muted mb-4">
                  Skillgap compares a user’s CV against a target job description, highlights
                  missing skills, and recommends suitable courses.
                </p>

                <div className="d-flex flex-wrap gap-3">
                  <Link to="/register" className="btn btn-info btn-lg text-dark fw-semibold">
                    Get Started
                  </Link>
                  <Link to="/login" className="btn btn-outline-secondary btn-lg">
                    Sign In
                  </Link>
                </div>
              </div>

              <div className="col-lg-5">
                <div className="card border-0 shadow-lg">
                  <div className="card-body p-4">
                    <h4 className="mb-3">How it works</h4>
                    <ol className="mb-0 text-muted">
                      <li className="mb-2">Create a secure account</li>
                      <li className="mb-2">Upload a CV and job description</li>
                      <li className="mb-2">Review missing skills</li>
                      <li>Get ranked course recommendations</li>
                    </ol>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <>
              <div className="row align-items-center g-4 mb-4">
                <div className="col-lg-7">
                  <h1 className="display-5 fw-bold mb-3">Welcome back, {currentUser.username}</h1>
                  <p className="lead text-muted mb-4">
                    Start a new analysis or jump straight back into reviewing your current skill
                    gap and course recommendations.
                  </p>

                  <div className="d-flex flex-wrap gap-3">
                    <Link to="/dashboard" className="btn btn-primary btn-lg">
                      Start New Analysis
                    </Link>
                    <Link to="/review" className="btn btn-outline-primary btn-lg">
                      Review Skill Gap
                    </Link>
                    <Link to="/recommendations" className="btn btn-outline-secondary btn-lg">
                      View Recommendations
                    </Link>
                  </div>
                </div>

                <div className="col-lg-5">
                  <div className="card border-0 shadow-lg">
                    <div className="card-body p-4">
                      <h4 className="mb-3">Quick Actions</h4>
                      <div className="d-grid gap-3">
                        <Link to="/dashboard" className="btn btn-primary">
                          Upload New Documents
                        </Link>
                        <Link to="/review" className="btn btn-outline-primary">
                          Review Latest Skill Gap
                        </Link>
                        <Link to="/recommendations" className="btn btn-outline-primary">
                          Open Recommendations
                        </Link>
                        <Link to="/history" className="btn btn-outline-secondary">
                          View History
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="row g-4">
                <div className="col-md-4">
                  <div className="card border-0 shadow-sm h-100">
                    <div className="card-body p-4">
                      <h5 className="mb-2">Upload</h5>
                      <p className="text-muted mb-0">
                        Add a CV and target job description to begin a new comparison.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="col-md-4">
                  <div className="card border-0 shadow-sm h-100">
                    <div className="card-body p-4">
                      <h5 className="mb-2">Review</h5>
                      <p className="text-muted mb-0">
                        Confirm missing skills before moving on to course recommendations.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="col-md-4">
                  <div className="card border-0 shadow-sm h-100">
                    <div className="card-body p-4">
                      <h5 className="mb-2">Upskill</h5>
                      <p className="text-muted mb-0">
                        Explore relevant course matches across supported providers.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </section>
    </div>
  );
}

export default Home;