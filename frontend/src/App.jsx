import React from "react";
import { Routes, Route, Navigate, Outlet } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext.jsx";
import { SavedPatentsProvider } from "./context/SavedPatentsContext.jsx";
import { NotificationsProvider } from "./context/NotificationsContext.jsx";
import ErrorBoundary from "./components/ErrorBoundary.jsx";
import MainLayout from "./layouts/MainLayout.jsx";
import AdminLayout from "./layouts/AdminLayout.jsx";

import Landing from "./pages/Landing.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Publications from "./pages/Publications.jsx";
import Funding from "./pages/Funding.jsx";
import Recommendations from "./pages/Recommendations.jsx";
import Patents from "./pages/Patents.jsx";
import PatentAnalytics from "./pages/PatentAnalytics.jsx";
import PatentIntelligenceDashboard from "./pages/PatentIntelligenceDashboard.jsx";
import SavedPatents from "./pages/SavedPatents.jsx";
import Trends from "./pages/Trends.jsx";
import AIAssistant from "./pages/AIAssistant.jsx";
import Search from "./pages/Search.jsx";
import Profile from "./pages/Profile.jsx";
import Notifications from "./pages/Notifications.jsx";

// Admin pages
import AdminDashboard from "./pages/admin/AdminDashboard.jsx";
import UserManagement from "./pages/admin/UserManagement.jsx";
import FundingManagement from "./pages/admin/FundingManagement.jsx";
import FundingIntelSync from "./pages/admin/FundingIntelSync.jsx";
import PublicationMonitor from "./pages/admin/PublicationMonitor.jsx";
import PatentMonitor from "./pages/admin/PatentMonitor.jsx";
import PatentIntel from "./pages/admin/PatentIntel.jsx";
import AIRecommendationMonitor from "./pages/admin/AIRecommendationMonitor.jsx";
import AdminReports from "./pages/admin/AdminReports.jsx";
import SystemSettings from "./pages/admin/SystemSettings.jsx";

function PrivateRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }
  return user ? children : <Navigate to="/login" replace />;
}

/**
 * Guard for any route that must only be reachable by the Admin role.
 * Non-admin users are redirected to the standard dashboard.
 */
function AdminRoute() {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== "admin") return <Navigate to="/dashboard" replace />;
  return <Outlet />;
}

function AppRoutes() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* User-facing private routes (researcher, founder, innovation, admin) */}
      <Route
        element={
          <PrivateRoute>
            <MainLayout />
          </PrivateRoute>
        }
      >
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/publications" element={<Publications />} />
        <Route path="/funding" element={<Funding />} />
        <Route path="/recommendations" element={<Recommendations />} />
        <Route path="/patents" element={<Patents />} />
        <Route path="/patents/analytics" element={<PatentAnalytics />} />
        <Route
          path="/patents/dashboard/:patentNumber"
          element={<PatentIntelligenceDashboard />}
        />
        <Route path="/saved-patents" element={<SavedPatents />} />
        <Route path="/trends" element={<Trends />} />
        <Route path="/ai-assistant" element={<AIAssistant />} />
        <Route path="/search" element={<Search />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/notifications" element={<Notifications />} />
      </Route>

      {/* Admin Portal — admin role only, isolated layout */}
      <Route element={<AdminRoute />}>
        <Route element={<AdminLayout />}>
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/admin/users" element={<UserManagement />} />
          <Route path="/admin/funding" element={<FundingManagement />} />
          <Route path="/admin/funding-intel" element={<FundingIntelSync />} />
          <Route path="/admin/publications" element={<PublicationMonitor />} />
          <Route path="/admin/patents" element={<PatentMonitor />} />
          <Route path="/admin/patents-intel" element={<PatentIntel />} />
          <Route path="/admin/recommendations" element={<AIRecommendationMonitor />} />
          <Route path="/admin/reports" element={<AdminReports />} />
          <Route path="/admin/settings" element={<SystemSettings />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <SavedPatentsProvider>
          <NotificationsProvider>
            <AppRoutes />
          </NotificationsProvider>
        </SavedPatentsProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}
