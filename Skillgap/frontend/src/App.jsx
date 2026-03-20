//App.jsx 
import { BrowserRouter } from "react-router-dom";
import { useEffect, useState } from "react";
import AppRoutes from "./routes";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import { applyTheme, getCurrentTheme } from "./services/theme";

function App() {
  const [theme, setTheme] = useState(getCurrentTheme());

  useEffect(() => {
    applyTheme(theme);

    const handleThemeChange = (event) => {
      setTheme(event.detail || getCurrentTheme());
    };

    window.addEventListener("skillgap-theme-change", handleThemeChange);

    return () => {
      window.removeEventListener("skillgap-theme-change", handleThemeChange);
    };
  }, [theme]);

  return (
    <BrowserRouter>
      <div className="app-shell d-flex flex-column min-vh-100">
        <Navbar />
        <main className="flex-grow-1">
          <AppRoutes />
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}
export default App;