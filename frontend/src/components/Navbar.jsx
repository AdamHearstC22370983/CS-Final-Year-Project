import { NavLink, useNavigate } from "react-router-dom";
import { clearCurrentUser, getCurrentUser, isLoggedIn } from "../services/auth";

function Navbar() {
  const navigate = useNavigate();
  const loggedIn = isLoggedIn();
  const currentUser = getCurrentUser();

  const handleLogout = () => {
    clearCurrentUser();
    navigate("/login");
  };

  return (
    <nav className="navbar navbar-expand-lg skillgap-navbar sticky-top shadow-sm">
      <div className="container">
        <NavLink className="navbar-brand d-flex align-items-center gap-2" to="/">
          <img src="/skillgap-logo.png" alt="Skillgap" height="34" />
        </NavLink>

        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#skillgapNavbar"
          aria-controls="skillgapNavbar"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        <div className="collapse navbar-collapse" id="skillgapNavbar">
          <ul className="navbar-nav ms-auto align-items-lg-center">
            <li className="nav-item skillgap-nav-item">
              <NavLink className="nav-link" to="/">
                Home
              </NavLink>
            </li>

            {loggedIn && (
              <>
                <li className="nav-item skillgap-nav-item">
                  <NavLink className="nav-link" to="/dashboard">
                    Dashboard
                  </NavLink>
                </li>

                <li className="nav-item skillgap-nav-item">
                  <NavLink className="nav-link" to="/results">
                    Results
                  </NavLink>
                </li>

                <li className="nav-item skillgap-nav-item">
                  <NavLink className="nav-link" to="/history">
                    History
                  </NavLink>
                </li>

                <li className="nav-item skillgap-nav-item">
                  <NavLink className="nav-link" to="/account">
                    Account
                  </NavLink>
                </li>
              </>
            )}

            <li className="nav-item skillgap-nav-item">
              <NavLink className="nav-link" to="/help">
                Help
              </NavLink>
            </li>

            {!loggedIn ? (
              <>
                <li className="nav-item ms-lg-3 mt-2 mt-lg-0">
                  <NavLink className="btn btn-outline-primary btn-sm me-2" to="/login">
                    Login
                  </NavLink>
                </li>
                <li className="nav-item mt-2 mt-lg-0">
                  <NavLink className="btn btn-primary btn-sm" to="/register">
                    Register
                  </NavLink>
                </li>
              </>
            ) : (
              <>
                <li className="nav-item ms-lg-3 nav-user-label me-3 mt-2 mt-lg-0">
                  Signed in as <strong>{currentUser?.username || "User"}</strong>
                </li>
                <li className="nav-item mt-2 mt-lg-0">
                  <button className="btn btn-outline-primary btn-sm" onClick={handleLogout}>
                    Logout
                  </button>
                </li>
              </>
            )}
          </ul>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;