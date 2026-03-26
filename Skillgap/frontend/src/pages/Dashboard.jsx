import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import UploadCard from "../components/UploadCard";
import GuidedQuestions from "../components/GuidedQuestions";
import { isLoggedIn } from "../services/auth";

function Dashboard() {
  const navigate = useNavigate();

  const [cvFile, setCvFile] = useState(null);
  const [jdFile, setJdFile] = useState(null);
  const [experienceLevel, setExperienceLevel] = useState("");
  const [hasTakenCourse, setHasTakenCourse] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [isRunning, setIsRunning] = useState(false);

  const handleCvChange = (e) => {
    setCvFile(e.target.files[0] || null);
  };

  const handleJdChange = (e) => {
    setJdFile(e.target.files[0] || null);
  };

  const uploadCvEntities = async () => {
    const formData = new FormData();
    formData.append("file", cvFile);

    await api.post("/analysis/save-cv-entities", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  };

  const uploadJdEntities = async () => {
    const formData = new FormData();
    formData.append("file", jdFile);

    await api.post("/analysis/save-jd-entities", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  };

  const computeGap = async () => {
    await api.post("/analysis/compute-gap");
  };

  const handleRunAnalysis = async () => {
    setStatus("");
    setError("");

    try {
      if (!isLoggedIn()) {
        throw new Error("You must be signed in to run an analysis.");
      }

      if (!cvFile || !jdFile) {
        throw new Error("Please upload both a CV and a Job Description.");
      }

      setIsRunning(true);

      setStatus("Uploading CV and extracting skills...");
      await uploadCvEntities();

      setStatus("Uploading job description and extracting skills...");
      await uploadJdEntities();

      setStatus("Comparing skills and building your latest gap snapshot...");
      await computeGap();

      setStatus("Analysis complete. Redirecting to review...");

      navigate(
        `/review?experience_level=${encodeURIComponent(
          experienceLevel
        )}&has_taken_course=${encodeURIComponent(hasTakenCourse)}`
      );
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Analysis failed.");
      setStatus("");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="container py-5">
      <div className="mb-4">
        <h1 className="mb-2">Dashboard</h1>
        <p className="text-muted mb-0">
          Upload your CV and target job description, then run a secure skill-gap analysis.
        </p>
      </div>

      <div className="row g-4 mb-4">
        <div className="col-12">
          <div className="dashboard-section-header">
            <span className="dashboard-section-number">1</span>
            <div>
              <h4 className="mb-1">Upload your documents</h4>
              <p className="text-muted mb-0">
                Add both a CV and Job Description to begin your skill-gap comparison.
              </p>
            </div>
          </div>
        </div>

        <div className="col-lg-6">
          <UploadCard
            title="Upload CV"
            description="Accepted formats: PDF, DOCX, TXT"
            file={cvFile}
            onFileChange={handleCvChange}
          />
        </div>

        <div className="col-lg-6">
          <UploadCard
            title="Upload Job Description"
            description="Accepted formats: PDF, DOCX, TXT"
            file={jdFile}
            onFileChange={handleJdChange}
          />
        </div>
      </div>

      <div className="row g-4 align-items-stretch">
        <div className="col-12">
          <div className="dashboard-section-header">
            <span className="dashboard-section-number">2</span>
            <div>
              <h4 className="mb-1">Refine and run your analysis</h4>
              <p className="text-muted mb-0">
                Guided questions are optional, but they help shape the recommendation experience.
              </p>
            </div>
          </div>
        </div>

        <div className="col-lg-8">
          <GuidedQuestions
            experienceLevel={experienceLevel}
            setExperienceLevel={setExperienceLevel}
            hasTakenCourse={hasTakenCourse}
            setHasTakenCourse={setHasTakenCourse}
          />
        </div>

        <div className="col-lg-4">
          <div className="card shadow-sm border-0 h-100 dashboard-run-card">
            <div className="card-body p-4 d-flex flex-column justify-content-between">
              <div>
                <h5 className="card-title mb-2">Run Analysis</h5>
                <p className="text-muted mb-0">
                  Skillgap will extract skills, compare both documents, and prepare a review page
                  where you can confirm skills before viewing recommendations.
                </p>
              </div>

              <div className="mt-4">
                <button
                  className="btn btn-primary btn-lg w-100 dashboard-run-button"
                  onClick={handleRunAnalysis}
                  disabled={isRunning}
                >
                  {isRunning ? "Running Analysis..." : "Run Analysis"}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {status && <div className="alert alert-info mt-4">{status}</div>}
      {error && <div className="alert alert-danger mt-4">{error}</div>}
    </div>
  );
}

export default Dashboard;