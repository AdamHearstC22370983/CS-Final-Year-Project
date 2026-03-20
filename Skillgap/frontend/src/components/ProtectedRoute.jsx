import { Navigate, useLocation } from "react-router-dom";
import { isLoggedIn } from "../services/auth";

// Protect routes by checking for a valid stored auth session.
function ProtectedRoute({ children }) {
  const location = useLocation();

  if (!isLoggedIn()) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return children;
}

export default ProtectedRoute;