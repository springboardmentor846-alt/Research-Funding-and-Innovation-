import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "../pages/Login";
import Register from "../pages/Register";
import Dashboard from "../pages/Dashboard";
import Profile from "../pages/Profile";
import Publications from "../pages/Publications";
import Patents from "../pages/Patents";
import Funding from "../pages/Funding";
import Recommendations from "../pages/Recommendations";
import GrantMatching from "../pages/GrantMatching";
import PublicationTrends from "../pages/PublicationTrends";

import DashboardLayout from "../components/DashboardLayout";
import ProtectedRoute from "../components/ProtectedRoute";

function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected Routes */}
        <Route
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/publications" element={<Publications />} />
          <Route path="/patents" element={<Patents />} />
          <Route path="/funding" element={<Funding />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/grant-matching" element={<GrantMatching />} />
          <Route
            path="/publication-trends"
            element={<PublicationTrends />}
          />
        </Route>

        {/* Redirect unknown routes */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default AppRoutes;