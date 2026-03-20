import { Link } from "react-router-dom";
import { getCurrentUser } from "../services/auth";
//Home.jsx
function Home() {
  const currentUser = getCurrentUser();

  return (
    <div className="home-page-shell">
      <section className="hero-section py-5">
        <div className="container py-4">
          <div className="row align-items-center g-4">
            <div className="col-lg-7">
              {!currentUser ? (
                <>
                  <h1 className="display-5 fw-bold mb-3">
                    Identify skill gaps and discover relevant learning pathways
                  </h1>
                  <p className="lead text-muted mb-4">
                    Skillgap compares a user’s CV against a target job description,
                    highlights missing skills, and recommends suitable courses.
                  </p>

                  <div className="d-flex flex-wrap gap-3">
                    <Link to="/register" className="btn btn-info btn-lg text-dark fw-semibold">
                      Get Started
                    </Link>
                    <Link to="/login" className="btn btn-outline-secondary btn-lg">
                      Sign In
                    </Link>
                  </div>
                </>
              ) : (
                <>
                  <h1 className="display-5 fw-bold mb-3">
                    Welcome back, {currentUser.username}
                  </h1>
                  <p className="lead text-muted mb-4">
                    Continue building your learning pathway by uploading a CV, analysing a job
                    description, and reviewing fresh course recommendations.
                  </p>

                  <div className="d-flex flex-wrap gap-3">
                    <Link to="/dashboard" className="btn btn-info btn-lg text-dark fw-semibold">
                      Go to Dashboard
                    </Link>
                    <Link to="/results" className="btn btn-outline-secondary btn-lg">
                      View Results
                    </Link>
                  </div>
                </>
              )}
            </div>

            <div className="col-lg-5">
              {!currentUser ? (
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
              ) : (
                <div className="card border-0 shadow-lg">
                  <div className="card-body p-4">
                    <h4 className="mb-3">Quick Actions</h4>
                    <div className="d-grid gap-3">
                      <Link to="/dashboard" className="btn btn-primary">
                        Start New Analysis
                      </Link>
                      <Link to="/results" className="btn btn-outline-primary">
                        Review Latest Results
                      </Link>
                      <Link to="/account" className="btn btn-outline-secondary">
                        Account Settings
                      </Link>
                      <Link to="/help" className="btn btn-outline-secondary">
                        Help & Privacy
                      </Link>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {currentUser && (
            <div className="row mt-5 g-4">
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
                    <h5 className="mb-2">Analyse</h5>
                    <p className="text-muted mb-0">
                      Identify missing skills and tailor recommendations with guided questions.
                    </p>
                  </div>
                </div>
              </div>

              <div className="col-md-4">
                <div className="card border-0 shadow-sm h-100">
                  <div className="card-body p-4">
                    <h5 className="mb-2">Upskill</h5>
                    <p className="text-muted mb-0">
                      Explore relevant learning options across multiple course providers.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
export default Home;