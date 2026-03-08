import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Results from "./pages/Results";
import Account from "./pages/Account";
import History from "./pages/History";
import Help from "./pages/Help";
//routes.jsx
function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/register" element={<Register />} />
      <Route path="/login" element={<Login />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/results" element={<Results />} />
      <Route path="/account" element={<Account />} />
      <Route path="/history" element={<History />} />
      <Route path="/help" element={<Help />} />
    </Routes>
  );
}
export default AppRoutes;