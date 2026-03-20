import { NavLink, useNavigate } from "react-router-dom";
import { clearCurrentUser, getCurrentUser, isLoggedIn } from "../services/auth";
import skillgapLogo from "../assets/images/brand/skillgap-logo.png";

function Navbar() {
  const navigate = useNavigate();
  const loggedIn = isLoggedIn();
  const currentUser = getCurrentUser();

  const handleLogout = () => {
    clearCurrentUser();
    navigate("/login");
  };

  const navLinkClass = ({ isActive }) =>
    `nav-link skillgap-main-link${isActive ? " active" : ""}`;

  return (
    <nav className="navbar navbar-expand-lg skillgap-navbar sticky-top shadow-sm">
      <div className="container">
        <NavLink className="navbar-brand skillgap-brand d-flex align-items-center" to="/">
          <img
            src={skillgapLogo}
            alt="Skillgap logo"
            className="skillgap-brand-logo"
          />
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
              <NavLink className={navLinkClass} to="/">
                Home
              </NavLink>
            </li>

            {loggedIn && (
              <>
                <li className="nav-item skillgap-nav-item">
                  <NavLink className={navLinkClass} to="/dashboard">
                    Dashboard
                  </NavLink>
                </li>

                <li className="nav-item skillgap-nav-item">
                  <NavLink className={navLinkClass} to="/results">
                    Results
                  </NavLink>
                </li>

                <li className="nav-item skillgap-nav-item">
                  <NavLink className={navLinkClass} to="/history">
                    History
                  </NavLink>
                </li>

                <li className="nav-item skillgap-nav-item">
                  <NavLink className={navLinkClass} to="/account">
                    Account
                  </NavLink>
                </li>
              </>
            )}

            <li className="nav-item skillgap-nav-item">
              <NavLink className={navLinkClass} to="/help">
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