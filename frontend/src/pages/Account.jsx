import { useNavigate } from "react-router-dom";
import { clearCurrentUser, getCurrentUser } from "../services/auth";
import { toggleTheme, getCurrentTheme } from "../services/theme";
import { useEffect, useState } from "react";
import api from "../services/api";
//Account.jsx
function Account() {
  const navigate = useNavigate();
  const currentUser = getCurrentUser();

  const [theme, setTheme] = useState(getCurrentTheme());
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isDownloading, setIsDownloading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  const [passwordForm, setPasswordForm] = useState({
    current_password: "",
    new_password: "",
  });

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

  const handleThemeToggle = () => {
    const nextTheme = toggleTheme();
    setTheme(nextTheme);
  };

  const handlePasswordChange = (e) => {
    setPasswordForm((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleDownloadData = async () => {
    setMessage("");
    setError("");
    setIsDownloading(true);

    try {
      const response = await api.get(`/users/${currentUser.user_id}/export`);
      const dataStr = JSON.stringify(response.data, null, 2);
      const blob = new Blob([dataStr], { type: "application/json" });
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;
      link.download = `skillgap-user-${currentUser.user_id}-data.json`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      setMessage("Your data export has been downloaded.");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to download your data.");
    } finally {
      setIsDownloading(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setMessage("");
    setError("");
    setIsChangingPassword(true);

    try {
      await api.post(`/users/${currentUser.user_id}/change-password`, passwordForm);

      setPasswordForm({
        current_password: "",
        new_password: "",
      });

      setMessage("Password updated successfully.");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to change password.");
    } finally {
      setIsChangingPassword(false);
    }
  };

  const handleDeleteAccount = async () => {
    const confirmed = window.confirm(
      "Are you sure you want to delete your account and related user data? This cannot be undone."
    );

    if (!confirmed) {
      return;
    }

    setMessage("");
    setError("");
    setIsDeleting(true);

    try {
      await api.delete(`/users/${currentUser.user_id}`);
      clearCurrentUser();
      navigate("/register");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete account.");
      setIsDeleting(false);
    }
  };

  return (
    <div className="container py-5">
      <div className="mb-4">
        <h1 className="mb-2">Account</h1>
        <p className="text-muted mb-0">
          Manage your account details, appearance preference, and privacy controls.
        </p>
      </div>

      {message && <div className="alert alert-success">{message}</div>}
      {error && <div className="alert alert-danger">{error}</div>}

      <div className="row g-4">
        <div className="col-lg-7">
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-body p-4">
              <h4 className="mb-3">Profile Info</h4>

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
                Toggle between light and dark mode.
              </p>

              <button className="btn btn-outline-primary" onClick={handleThemeToggle}>
                Switch to {theme === "dark" ? "Light Mode" : "Dark Mode"}
              </button>

              <p className="text-muted small mt-3 mb-0">
                Your theme preference is stored locally in your browser for future logins.
              </p>
            </div>
          </div>

          <div className="card shadow-sm border-0 mb-4">
            <div className="card-body p-4">
              <h4 className="mb-3">Change Password</h4>

              <form onSubmit={handleChangePassword}>
                <div className="mb-3">
                  <label className="form-label fw-semibold">Current Password</label>
                  <input
                    type="password"
                    className="form-control"
                    name="current_password"
                    value={passwordForm.current_password}
                    onChange={handlePasswordChange}
                    required
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label fw-semibold">New Password</label>
                  <input
                    type="password"
                    className="form-control"
                    name="new_password"
                    value={passwordForm.new_password}
                    onChange={handlePasswordChange}
                    required
                  />
                </div>

                <button
                  type="submit"
                  className="btn btn-outline-primary"
                  disabled={isChangingPassword}
                >
                  {isChangingPassword ? "Updating Password..." : "Update Password"}
                </button>
              </form>
            </div>
          </div>

          <div className="card shadow-sm border-0">
            <div className="card-body p-4">
              <h4 className="mb-3">Account Actions</h4>

              <div className="d-flex flex-wrap gap-3">
                <button
                  className="btn btn-outline-secondary"
                  onClick={handleDownloadData}
                  disabled={isDownloading}
                >
                  {isDownloading ? "Downloading..." : "Download My Data"}
                </button>

                <button className="btn btn-danger" onClick={handleLogout}>
                  Log Out
                </button>

                <button
                  className="btn btn-outline-danger"
                  onClick={handleDeleteAccount}
                  disabled={isDeleting}
                >
                  {isDeleting ? "Deleting Account..." : "Delete Account"}
                </button>
              </div>

              <p className="text-muted small mt-3 mb-0">
                Download lets you export your user-linked data. Delete Account permanently removes
                your account and related user-owned records.
              </p>
            </div>
          </div>
        </div>

        <div className="col-lg-5">
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-body p-4">
              <h4 className="mb-3">Privacy Overview</h4>
              <p className="mb-3">
                Skillgap only stores the minimum information needed for account access such as:
              </p>

              <div className="privacy-chip-list d-flex flex-wrap gap-2 mb-3">
                <span className="badge text-bg-light border px-3 py-2">Username</span>
                <span className="badge text-bg-light border px-3 py-2">Email</span>
                <span className="badge text-bg-light border px-3 py-2">Password</span>
              </div>

              <p className="text-muted small mb-0">
                Passwords are encrypted. Uploaded CVs and Job Descriptions are used
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
                <li>You can also download your user-linked data.</li>
                <li>You can also change your password or delete your account and your data.</li>
                <li>You can log out at any time.</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
export default Account;