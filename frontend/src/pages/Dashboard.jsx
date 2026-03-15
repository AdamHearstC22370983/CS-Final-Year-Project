import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import UploadCard from "../components/UploadCard";
import GuidedQuestions from "../components/GuidedQuestions";
import { getCurrentUser } from "../services/auth";

function Dashboard() {
  const navigate = useNavigate();
  const currentUser = getCurrentUser();

  const [cvFile, setCvFile] = useState(null);
  const [jdFile, setJdFile] = useState(null);
  const [experienceLevel, setExperienceLevel] = useState("");
  const [hasTakenCourse, setHasTakenCourse] = useState("");
  const [preferredLearningStyle, setPreferredLearningStyle] = useState("");
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

    await api.post(`/save-cv-entities?user_id=${currentUser.user_id}`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  };

  const uploadJdEntities = async () => {
    const formData = new FormData();
    formData.append("file", jdFile);

    await api.post("/save-jd-entities", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  };

  const computeGap = async () => {
    await api.post(`/compute-gap?user_id=${currentUser.user_id}`);
  };

  const handleRunAnalysis = async () => {
    setStatus("");
    setError("");

    try {
      if (!currentUser?.user_id) {
        throw new Error("No signed-in user found.");
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

      setStatus("Analysis complete. Redirecting to results...");

      setTimeout(() => {
        navigate(
          `/results?experience_level=${experienceLevel}&has_taken_course=${hasTakenCourse}&preference=${preferredLearningStyle}`
        );
      }, 500);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Analysis failed.");
      setStatus("");
      setIsRunning(false);
      return;
    }

    setIsRunning(false);
  };

  return (
    <div className="container py-5">
      <div className="mb-4">
        <h1 className="mb-2">Dashboard</h1>
        <p className="text-muted mb-0">
          Work through the four stages below to generate tailored recommendations from your CV and
          target job description.
        </p>
      </div>

      <div className="card shadow-sm border-0 mb-4 dashboard-summary-card">
        <div className="card-body d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
          <div>
            <div className="fw-semibold mb-1">Signed in user</div>
            <div className="text-muted">
              {currentUser?.username} ({currentUser?.email})
            </div>
          </div>

          <div className="dashboard-stage-badges d-flex flex-wrap gap-2">
            <span className="badge text-bg-light border px-3 py-2">1. Upload</span>
            <span className="badge text-bg-light border px-3 py-2">2. Answer</span>
            <span className="badge text-bg-light border px-3 py-2">3. Analyse</span>
            <span className="badge text-bg-light border px-3 py-2">4. Review</span>
          </div>
        </div>
      </div>

      <div className="row g-4 mb-4">
        <div className="col-12">
          <div className="dashboard-section-header">
            <span className="dashboard-section-number">1</span>
            <div>
              <h4 className="mb-1">Upload your documents</h4>
              <p className="text-muted mb-0">
                Add both a CV and a target job description to begin the comparison.
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

      <div className="row g-4 mb-4">
        <div className="col-12">
          <div className="dashboard-section-header">
            <span className="dashboard-section-number">2</span>
            <div>
              <h4 className="mb-1">Answer a few guided questions</h4>
              <p className="text-muted mb-0">
                These are optional, but they help the system shape the recommendation experience.
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
          <div className="card shadow-sm border-0 h-100 dashboard-check-card">
            <div className="card-body p-4">
              <h5 className="card-title">Readiness Check</h5>
              <p className="text-muted">
                Make sure the core inputs are in place before you start.
              </p>

              <div className="dashboard-checklist small">
                <div className={`mb-2 ${cvFile ? "text-success" : "text-muted"}`}>
                  {cvFile ? "✓" : "•"} CV selected
                </div>
                <div className={`mb-2 ${jdFile ? "text-success" : "text-muted"}`}>
                  {jdFile ? "✓" : "•"} Job description selected
                </div>
                <div className={`mb-2 ${experienceLevel ? "text-success" : "text-muted"}`}>
                  {experienceLevel ? "✓" : "•"} Experience level set
                </div>
                <div className={hasTakenCourse ? "text-success" : "text-muted"}>
                  {hasTakenCourse ? "✓" : "•"} Course background answered
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="row g-4 mb-4">
        <div className="col-12">
          <div className="dashboard-section-header">
            <span className="dashboard-section-number">3</span>
            <div>
              <h4 className="mb-1">Run the analysis</h4>
              <p className="text-muted mb-0">
                Skillgap will extract skills, compare your documents, and prepare recommendations.
              </p>
            </div>
          </div>
        </div>
      </div>

      {status && <div className="alert alert-info">{status}</div>}
      {error && <div className="alert alert-danger">{error}</div>}

      <button
        className="btn btn-primary btn-lg dashboard-run-button"
        onClick={handleRunAnalysis}
        disabled={isRunning}
      >
        {isRunning ? "Running Analysis..." : "Run Analysis"}
      </button>
    </div>
  );
}
export default Dashboard;