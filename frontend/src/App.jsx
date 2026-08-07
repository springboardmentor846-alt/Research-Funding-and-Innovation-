import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'

// Layouts
import AuthLayout from '@/layouts/AuthLayout'
import AppLayout from '@/layouts/AppLayout'

// Public pages
import LandingPage from '@/pages/LandingPage'
import LoginPage from '@/pages/auth/LoginPage'
import RegisterPage from '@/pages/auth/RegisterPage'
import ForgotPasswordPage from '@/pages/auth/ForgotPasswordPage'
import ResetPasswordPage from '@/pages/auth/ResetPasswordPage'
import VerifyEmailPage from '@/pages/auth/VerifyEmailPage'

// Protected pages
import DashboardPage from '@/pages/dashboard/DashboardPage'
import ProfilePage from '@/pages/dashboard/ProfilePage'
import ResearchProfilePage from '@/pages/research/ResearchProfilePage'
import ResearcherDirectoryPage from '@/pages/research/ResearcherDirectoryPage'
import ResearcherDetailPage from '@/pages/research/ResearcherDetailPage'

// Funding Discovery pages (Phase 3)
import FundingDashboardPage from '@/pages/funding/FundingDashboardPage'
import FundingSearchPage from '@/pages/funding/FundingSearchPage'
import FundingDetailPage from '@/pages/funding/FundingDetailPage'
import MyBookmarksPage from '@/pages/funding/MyBookmarksPage'
import FundingAlertsPage from '@/pages/funding/FundingAlertsPage'

// Research Intelligence pages (Phase 4)
import ResearchIntelligenceDashboardPage from '@/pages/intelligence/ResearchIntelligenceDashboardPage'
import ResearchPaperSearchPage from '@/pages/intelligence/ResearchPaperSearchPage'
import ResearchPaperDetailPage from '@/pages/intelligence/ResearchPaperDetailPage'
import ResearchTrendsPage from '@/pages/intelligence/ResearchTrendsPage'

// Patent Intelligence pages (Phase 5)
import PatentDashboardPage from '@/pages/intelligence/PatentDashboardPage'
import PatentSearchPage from '@/pages/intelligence/PatentSearchPage'
import PatentDetailPage from '@/pages/intelligence/PatentDetailPage'
import PatentAnalyticsPage from '@/pages/intelligence/PatentAnalyticsPage'

// Technology Intelligence pages (Phase 6)
import TechnologyDashboardPage from '@/pages/intelligence/TechnologyDashboardPage'
import TechnologyTrendsPage from '@/pages/intelligence/TechnologyTrendsPage'
import InnovationScorePage from '@/pages/intelligence/InnovationScorePage'
import OpportunityAnalysisPage from '@/pages/intelligence/OpportunityAnalysisPage'

// Commercialization & Industry Collaboration pages (Phase 7)
import CommercializationDashboardPage from '@/pages/commercialization/CommercializationDashboardPage'
import CollaborationOpportunitiesPage from '@/pages/commercialization/CollaborationOpportunitiesPage'
import IndustryPartnersPage from '@/pages/commercialization/IndustryPartnersPage'
import StartupRecommendationsPage from '@/pages/commercialization/StartupRecommendationsPage'
import CommercializationDetailPage from '@/pages/commercialization/CommercializationDetailPage'

// Admin, Reports & Notifications pages (Phase 8)
import AdminDashboardPage from '@/pages/admin/AdminDashboardPage'
import ReportsPage from '@/pages/admin/ReportsPage'
import NotificationsPage from '@/pages/admin/NotificationsPage'
import SystemAnalyticsPage from '@/pages/admin/SystemAnalyticsPage'
import UserManagementPage from '@/pages/admin/UserManagementPage'

// Guards
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import PublicRoute from '@/components/auth/PublicRoute'

export default function App() {
  const { isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen bg-surface-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-4 border-brand-600 border-t-transparent animate-spin" />
          <p className="text-surface-400 text-sm animate-pulse">Initializing platform…</p>
        </div>
      </div>
    )
  }

  return (
    <Routes>
      {/* Public landing */}
      <Route path="/" element={<LandingPage />} />

      {/* Auth routes — redirect to dashboard if already logged in */}
      <Route element={<PublicRoute />}>
        <Route element={<AuthLayout />}>
          <Route path="/login"          element={<LoginPage />} />
          <Route path="/register"       element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password"  element={<ResetPasswordPage />} />
          <Route path="/verify-email"    element={<VerifyEmailPage />} />
        </Route>
      </Route>

      {/* Protected routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/dashboard"         element={<DashboardPage />} />
          <Route path="/funding"           element={<FundingDashboardPage />} />
          <Route path="/funding/search"    element={<FundingSearchPage />} />
          <Route path="/funding/bookmarks" element={<MyBookmarksPage />} />
          <Route path="/funding/alerts"    element={<FundingAlertsPage />} />
          <Route path="/funding/:id"       element={<FundingDetailPage />} />
          <Route path="/research-intelligence"          element={<ResearchIntelligenceDashboardPage />} />
          <Route path="/research-intelligence/search"   element={<ResearchPaperSearchPage />} />
          <Route path="/research-intelligence/trends"   element={<ResearchTrendsPage />} />
          <Route path="/research-intelligence/paper/:id" element={<ResearchPaperDetailPage />} />
          <Route path="/patent-intelligence"           element={<PatentDashboardPage />} />
          <Route path="/patent-intelligence/search"    element={<PatentSearchPage />} />
          <Route path="/patent-intelligence/analytics" element={<PatentAnalyticsPage />} />
          <Route path="/patent-intelligence/:id"        element={<PatentDetailPage />} />
          <Route path="/technology-intelligence"              element={<TechnologyDashboardPage />} />
          <Route path="/technology-intelligence/trends"       element={<TechnologyTrendsPage />} />
          <Route path="/technology-intelligence/innovation-score" element={<InnovationScorePage />} />
          <Route path="/technology-intelligence/opportunities" element={<OpportunityAnalysisPage />} />
          <Route path="/commercialization"              element={<CommercializationDashboardPage />} />
          <Route path="/commercialization/opportunities"element={<CollaborationOpportunitiesPage />} />
          <Route path="/commercialization/partners"     element={<IndustryPartnersPage />} />
          <Route path="/commercialization/startups"      element={<StartupRecommendationsPage />} />
          <Route path="/commercialization/:id"          element={<CommercializationDetailPage />} />
          <Route path="/admin"             element={<AdminDashboardPage />} />
          <Route path="/admin/analytics"  element={<SystemAnalyticsPage />} />
          <Route path="/admin/users"      element={<UserManagementPage />} />
          <Route path="/reports"          element={<ReportsPage />} />
          <Route path="/notifications"    element={<NotificationsPage />} />
          <Route path="/research-profile"  element={<ResearchProfilePage />} />
          <Route path="/researchers"       element={<ResearcherDirectoryPage />} />
          <Route path="/researchers/:id"   element={<ResearcherDetailPage />} />
          <Route path="/profile"           element={<ProfilePage />} />
        </Route>
      </Route>

      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
