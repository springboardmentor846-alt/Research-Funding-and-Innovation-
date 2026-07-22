import { BrowserRouter, Routes, Route } from "react-router-dom";

import LandingPage from "./pages/LandingPage";
import Dashboard from "./pages/Dashboard";
import Patents from "./pages/Patents";
import Funding from "./pages/Funding";
import Technologies from "./pages/Technologies";
import AIInsights from "./pages/AIInsights";
import Analytics from "./pages/Analytics";
import SettingsPage from "./pages/Settings";
import Login from "./pages/Login";

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Landing Page */}
        <Route path="/" element={<LandingPage />} />

        {/* Dashboard */}
        <Route path="/dashboard" element={<Dashboard />} />

        {/* Other Pages */}
        <Route path="/login" element={<Login />} />
        <Route path="/patents" element={<Patents />} />
        <Route path="/funding" element={<Funding />} />
        <Route path="/technologies" element={<Technologies />} />
        <Route path="/ai" element={<AIInsights />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/settings" element={<SettingsPage />} />
       

      </Routes>
    </BrowserRouter>
  );
}

export default App;