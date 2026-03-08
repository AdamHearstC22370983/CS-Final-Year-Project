import { Link } from "react-router-dom";
//Home.jsx - The Home Page for the Skillgap Web Application
function Home() {
  return (
    <div className="bg-light">
      <section className="hero-section py-5">
        <div className="container py-4">
          <div className="row align-items-center g-4">
            <div className="col-lg-7">
              <h1 className="display-5 fw-bold mb-3">
                Identify skill gaps and discover relevant learning pathways
              </h1>
              <p className="lead text-muted mb-4">
                Skillgap compares a user’s CV against a target job description,
                highlights missing entities, and recommends suitable courses.
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
                    <li className="mb-2">Review missing entities</li>
                    <li>Get ranked course recommendations</li>
                  </ol>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
//basic Home page, first draft
export default Home;
