import { Link, NavLink, useNavigate } from "react-router-dom";
import { clearCurrentUser, getCurrentUser } from "../services/auth";
import brandLogo from "../assets/images/brand/skillgap-logo.png";
//Navbar.jsx - Used to display Navigation bar across pages
function Navbar() {
  const navigate = useNavigate();
  const currentUser = getCurrentUser();

  const handleLogout = () => {
    clearCurrentUser();
    navigate("/login");
  };

  return (
    <nav className="navbar navbar-expand-lg skillgap-nav">
      <div className="container">
        <Link className="navbar-brand skillgap-brand" to="/">
          <img src={brandLogo} alt="Skillgap" className="skillgap-brand-logo" />
        </Link>

        <button
          className="navbar-toggler skillgap-nav-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#mainNav"
          aria-controls="mainNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon" />
        </button>

        <div className="collapse navbar-collapse" id="mainNav">
          <ul className="navbar-nav ms-auto align-items-lg-center skillgap-nav-list">
            <li className="nav-item skillgap-nav-item">
              <NavLink className="nav-link" to="/">
                Home
              </NavLink>
            </li>

            {currentUser && (
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

            {!currentUser ? (
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
                  Signed in as <strong>{currentUser.username}</strong>
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