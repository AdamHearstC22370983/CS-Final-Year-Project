import { useNavigate } from "react-router-dom";
import { clearCurrentUser, getCurrentUser } from "../services/auth";
import { toggleTheme, getCurrentTheme } from "../services/theme";
import { useEffect, useState } from "react";
import api from "../services/api";

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
          Manage your account details, appearance, password, and account actions.
        </p>
      </div>

      {message && <div className="alert alert-success">{message}</div>}
      {error && <div className="alert alert-danger">{error}</div>}

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
                Toggle between light and dark mode.
              </p>

              <button className="btn btn-outline-primary" onClick={handleThemeToggle}>
                Switch to {theme === "dark" ? "Light Mode" : "Dark Mode"}
              </button>
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
                Privacy, security, and data-handling explanations are available on the Help &
                Privacy page.
              </p>
            </div>
          </div>
        </div>

        <div className="col-lg-5">
          <div className="card shadow-sm border-0 mb-4">
            <div className="card-body p-4">
              <h4 className="mb-3">Quick Overview</h4>
              <ul className="text-muted small mb-0">
                <li>Manage account basics here.</li>
                <li>Update your password when needed.</li>
                <li>Export or remove your user-linked data.</li>
                <li>Use Help & Privacy for security and data explanations.</li>
              </ul>
            </div>
          </div>

          <div className="card shadow-sm border-0">
            <div className="card-body p-4">
              <h4 className="mb-3">Need More Control?</h4>
              <p className="text-muted mb-0">
                This page focuses on practical account actions. For information about how data is
                used, stored, and explained within the project, visit Help & Privacy.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
export default Account;