import { BrowserRouter } from "react-router-dom";
import AppRoutes from "./routes";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
//App.jsx
function App() {
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