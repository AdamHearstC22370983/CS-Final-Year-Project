import { Link, NavLink } from "react-router-dom";
//Navbar.jsx
function Navbar() {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark skillgap-nav">
      <div className="container">
        <Link className="navbar-brand fw-bold" to="/">
          Skillgap
        </Link>

        <button
          className="navbar-toggler"
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
          <ul className="navbar-nav ms-auto align-items-lg-center">
            <li className="nav-item">
              <NavLink className="nav-link" to="/">
                Home
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink className="nav-link" to="/dashboard">
                Dashboard
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink className="nav-link" to="/results">
                Results
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink className="nav-link" to="/help">
                Help
              </NavLink>
            </li>
            <li className="nav-item ms-lg-2">
              <NavLink className="btn btn-outline-light btn-sm me-2" to="/login">
                Login
              </NavLink>
            </li>
            <li className="nav-item mt-2 mt-lg-0">
              <NavLink className="btn btn-info btn-sm text-dark fw-semibold" to="/register">
                Register
              </NavLink>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
}
export default Navbar;
