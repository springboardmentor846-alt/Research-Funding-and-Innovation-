import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { Login } from './pages/Login';
import { Signup } from './pages/Signup';

import { ResearcherDashboard } from './pages/ResearcherDashboard';
import { StartupDashboard } from './pages/StartupDashboard';
import { ManagerDashboard } from './pages/ManagerDashboard';
import { AdminDashboard } from './pages/AdminDashboard';

import { FundingDiscovery } from './pages/FundingDiscovery';
import { ResearchTrends } from './pages/ResearchTrends';
import { PatentLandscape } from './pages/PatentLandscape';
import { TechnologyIntelligence } from './pages/TechnologyIntelligence';
import { InnovationScorer } from './pages/InnovationScorer';
import { SavedFunding } from './pages/SavedFunding';
import { AiAssistant } from './pages/AiAssistant';
import { NotificationCenter } from './pages/NotificationCenter';
import { ReportsExport } from './pages/ReportsExport';

const MainLayout = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [authView, setAuthView] = useState('login'); // 'login' or 'signup'
  const { user, isAuthenticated, loading } = useAuth();
  const theme = useTheme();

  const renderDashboardByRole = () => {
    switch (user?.role) {
      case 'STARTUP_FOUNDER':
        return <StartupDashboard onNavigate={setActiveTab} />;
      case 'INNOVATION_MANAGER':
        return <ManagerDashboard onNavigate={setActiveTab} />;
      case 'SYSTEM_ADMIN':
        return <AdminDashboard onNavigate={setActiveTab} />;
      case 'RESEARCHER':
      default:
        return <ResearcherDashboard onNavigate={setActiveTab} />;
    }
  };

  const renderMainContent = () => {
    switch (activeTab) {
      case 'funding':
        return <FundingDiscovery setActiveTab={setActiveTab} />;
      case 'research':
        return <ResearchTrends />;
      case 'patents':
        return <PatentLandscape />;
      case 'technology':
        return <TechnologyIntelligence />;
      case 'scoring':
        return <InnovationScorer />;
      case 'saved':
        return <SavedFunding setActiveTab={setActiveTab} />;
      case 'ai':
        return <AiAssistant setActiveTab={setActiveTab} />;
      case 'notifications':
        return <NotificationCenter />;
      case 'reports':
        return <ReportsExport />;
      case 'dashboard':
      default:
        return renderDashboardByRole();
    }
  };

  // Show loading screen
  if (loading) {
    return (
      <div
        style={{ backgroundColor: theme.colors.bg.primary }}
        className="min-h-screen flex items-center justify-center"
      >
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-current border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p style={{ color: theme.colors.text.secondary }}>Loading...</p>
        </div>
      </div>
    );
  }

  // Show authentication pages if not authenticated
  if (!isAuthenticated) {
    return authView === 'login' ? (
      <Login onSwitchToSignup={() => setAuthView('signup')} />
    ) : (
      <Signup onSwitchToLogin={() => setAuthView('login')} />
    );
  }

  return (
    <div
      style={{
        backgroundColor: theme.colors.bg.primary,
        color: theme.colors.text.primary,
      }}
      className="min-h-screen flex flex-col font-sans transition-colors duration-200"
    >
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenSidebar={() => setSidebarOpen(true)}
      />
      <div className="flex flex-1">
        <Sidebar
          activeTab={activeTab}
          setActiveTab={(tab) => {
            setActiveTab(tab);
            setSidebarOpen(false);
          }}
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />
        <main
          className="flex-1 p-6 max-w-7xl mx-auto w-full"
          onClick={() => sidebarOpen && setSidebarOpen(false)}
        >
          {renderMainContent()}
        </main>
      </div>
    </div>
  );
};

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <MainLayout />
      </AuthProvider>
    </ThemeProvider>
  );
}
