import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { ProtectedRoute } from './components/guards/ProtectedRoute';

import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';
import { DashboardPage } from './pages/DashboardPage';
import { ResearchProfilePage } from './pages/ResearchProfilePage';
import { FundingDiscoveryPage } from './pages/FundingDiscoveryPage';
import { FundingRecommendationsPage } from './pages/FundingRecommendationsPage';
import { ResearchTrendsPage } from './pages/ResearchTrendsPage';
import { PatentAnalyticsPage } from './pages/PatentAnalyticsPage';
import { TechIntelligencePage } from './pages/TechIntelligencePage';
import { InnovationScorePage } from './pages/InnovationScorePage';
import { CommercializationPage } from './pages/CommercializationPage';
import { ReportsPage } from './pages/ReportsPage';
import { NotificationsPage } from './pages/NotificationsPage';
import { SettingsPage } from './pages/SettingsPage';
import { AdminPanelPage } from './pages/AdminPanelPage';
import { NotFoundPage } from './pages/NotFoundPage';

export function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <NotificationProvider>
          <Router>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />

              {/* Protected User Routes */}
              <Route element={<ProtectedRoute />}>
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/profile" element={<ResearchProfilePage />} />
                <Route path="/funding" element={<FundingDiscoveryPage />} />
                <Route path="/recommendations" element={<FundingRecommendationsPage />} />
                <Route path="/research-trends" element={<ResearchTrendsPage />} />
                <Route path="/patent-analytics" element={<PatentAnalyticsPage />} />
                <Route path="/tech-intelligence" element={<TechIntelligencePage />} />
                <Route path="/innovation-score" element={<InnovationScorePage />} />
                <Route path="/commercialization" element={<CommercializationPage />} />
                <Route path="/reports" element={<ReportsPage />} />
                <Route path="/notifications" element={<NotificationsPage />} />
                <Route path="/settings" element={<SettingsPage />} />
              </Route>

              {/* Admin Protected Routes */}
              <Route element={<ProtectedRoute allowedRoles={['Administrator']} />}>
                <Route path="/admin" element={<AdminPanelPage />} />
              </Route>

              {/* 404 Route */}
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </Router>
        </NotificationProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
