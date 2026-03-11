//Account.jsx
import { useNavigate } from "react-router-dom";
import { clearCurrentUser, getCurrentUser } from "../services/auth";
import { applyTheme, getCurrentTheme, toggleTheme } from "../services/theme";
import { useEffect, useState } from "react";

function Account() {
  const navigate = useNavigate();
  const currentUser = getCurrentUser();

  const [theme, setTheme] = useState(getCurrentTheme());

  useEffect(() => {
    const handleThemeChange = (event) => {
      setTheme(event.detail || getCurrentTheme());
    };

    window.addEventListener("skillgap-theme-change", handleThemeChange);

    return () => {
      window.removeEventListener("skillgap-theme-change", handleThemeChange);
    };
  }, []);

  const handleLogout = () => {
    clearCurrentUser();
    navigate("/login");
  };

  const handlePlaceholderAction = (actionName) => {
    alert(`${actionName} is not connected yet. This will be added in a later step.`);
  };

  const handleThemeToggle = () => {
    const nextTheme = toggleTheme();
    setTheme(nextTheme);
  };

  const handleSetLightMode = () => {
    applyTheme("light");
    setTheme("light");
  };

  const handleSetDarkMode = () => {
    applyTheme("dark");
    setTheme("dark");
  };

  return (
    <div className="container py-5">
      <div className="mb-4">
        <h1 className="mb-2">Account</h1>
        <p className="text-muted mb-0">
          Manage your account details, appearance preferences, and privacy controls.
        </p>
      </div>

      <div className="row g-4">
        <div className="col-lg-7">
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-body p-4">
              <h4 className="mb-3">Profile Information</h4>

              <div className="mb-3">
                <label className="form-label fw-semibold">Username</label>
                <input
                  type="text"
                  className="form-control"
                  value={currentUser?.username || ""}
                  disabled
                  readOnly
                />
              </div>

              <div className="mb-0">
                <label className="form-label fw-semibold">Email</label>
                <input
                  type="email"
                  className="form-control"
                  value={currentUser?.email || ""}
                  disabled
                  readOnly
                />
              </div>
            </div>
          </div>

          <div className="card shadow-sm border-0 mb-4">
            <div className="card-body p-4">
              <h4 className="mb-3">Appearance</h4>
              <p className="text-muted">
                Choose how Skillgap looks while you work.
              </p>

              <div className="d-flex flex-wrap gap-3">
                <button
                  className={`btn ${theme === "light" ? "btn-primary" : "btn-outline-primary"}`}
                  onClick={handleSetLightMode}
                >
                  Light Mode
                </button>

                <button
                  className={`btn ${theme === "dark" ? "btn-primary" : "btn-outline-primary"}`}
                  onClick={handleSetDarkMode}
                >
                  Dark Mode
                </button>

                <button className="btn btn-outline-secondary" onClick={handleThemeToggle}>
                  Toggle Theme
                </button>
              </div>

              <p className="text-muted small mt-3 mb-0">
                Your theme preference is stored locally in your browser.
              </p>
            </div>
          </div>

          <div className="card shadow-sm border-0">
            <div className="card-body p-4">
              <h4 className="mb-3">Account Actions</h4>

              <div className="d-flex flex-wrap gap-3">
                <button
                  className="btn btn-outline-primary"
                  onClick={() => handlePlaceholderAction("Change password")}
                >
                  Change Password
                </button>

                <button
                  className="btn btn-outline-secondary"
                  onClick={() => handlePlaceholderAction("Download my data")}
                >
                  Download My Data
                </button>

                <button
                  className="btn btn-outline-danger"
                  onClick={() => handlePlaceholderAction("Delete account")}
                >
                  Delete Account
                </button>

                <button className="btn btn-danger" onClick={handleLogout}>
                  Log Out
                </button>
              </div>

              <p className="text-muted small mt-3 mb-0">
                Some actions are currently placeholders and will be connected to backend routes later.
              </p>
            </div>
          </div>
        </div>

        <div className="col-lg-5">
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-body p-4">
              <h4 className="mb-3">Privacy Overview</h4>
              <p className="mb-3">
                Skillgap only stores the minimum information needed for account access:
              </p>

              <div className="privacy-chip-list d-flex flex-wrap gap-2 mb-3">
                <span className="badge text-bg-light border px-3 py-2">Username</span>
                <span className="badge text-bg-light border px-3 py-2">Email</span>
                <span className="badge text-bg-light border px-3 py-2">Password Hash</span>
              </div>

              <p className="text-muted small mb-0">
                Passwords are not stored in plain text. Uploaded CVs and job descriptions are used
                to extract skills and generate recommendation results.
              </p>
            </div>
          </div>

          <div className="card shadow-sm border-0">
            <div className="card-body p-4">
              <h4 className="mb-3">Your Control</h4>
              <p className="mb-2">
                This project is designed around minimal data collection and user control.
              </p>
              <ul className="text-muted small mb-0">
                <li>You can log out at any time.</li>
                <li>You can review your account information here.</li>
                <li>You can choose your preferred visual theme.</li>
                <li>Future versions will allow password updates and account deletion.</li>
                <li>Help / Privacy explains how recommendation results are generated.</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
export default Account;