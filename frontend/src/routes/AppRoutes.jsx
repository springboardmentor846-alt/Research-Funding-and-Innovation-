import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";

import Login               from "@/pages/Login";
import Register            from "@/pages/Register";
import Dashboard           from "@/pages/Dashboard";
import Profile             from "@/pages/Profile";
import FundingDashboard    from "@/pages/FundingDashboard";
import FundingDetail       from "@/pages/FundingDetail";
import Recommendations     from "@/pages/Recommendations";
import GrantMatching       from "@/pages/GrantMatching";
import ResearchDashboard   from "@/pages/ResearchDashboard";
import PublicationAnalytics from "@/pages/PublicationAnalytics";
import MyPublications from "@/pages/MyPublications";
import AddPublication from "@/pages/AddPublication";
import EditPublication from "@/pages/EditPublication";

// Protect routes — redirect to login if not authenticated
function PrivateRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/" replace />;
}

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/"         element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected */}
        <Route path="/dashboard"          element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/profile"            element={<PrivateRoute><Profile /></PrivateRoute>} />
        <Route path="/funding"            element={<PrivateRoute><FundingDashboard /></PrivateRoute>} />
        <Route path="/funding/:id"        element={<PrivateRoute><FundingDetail /></PrivateRoute>} />
        <Route path="/recommendations"    element={<PrivateRoute><Recommendations /></PrivateRoute>} />
        <Route path="/grant-matching"     element={<PrivateRoute><GrantMatching /></PrivateRoute>} />
        <Route path="/research-dashboard" element={<PrivateRoute><ResearchDashboard /></PrivateRoute>} />
        <Route path="/publications"       element={<PrivateRoute><PublicationAnalytics /></PrivateRoute>} />
        <Route path="/my-publications"     element={<PrivateRoute><MyPublications /></PrivateRoute>} />
        <Route path="/add-publication"     element={<PrivateRoute><AddPublication /></PrivateRoute>} />
        <Route path="/edit-publication/:id" element={<PrivateRoute><EditPublication /></PrivateRoute>} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
