import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { 
  Search, Bell, Shield, User, ChevronDown, Sparkles, 
  BookOpen, Rocket, Briefcase, Settings, Moon, Sun, LogOut, Menu
} from 'lucide-react';

export const Navbar = ({ activeTab, setActiveTab, onOpenSidebar, unreadNotificationsCount = 3 }) => {
  const { user, switchRole, rolesInfo, logout } = useAuth();
  const theme = useTheme();
  const [roleDropdownOpen, setRoleDropdownOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const roleIcons = {
    RESEARCHER: <BookOpen className="w-4 h-4 text-cyan-400" />,
    STARTUP_FOUNDER: <Rocket className="w-4 h-4 text-emerald-400" />,
    INNOVATION_MANAGER: <Briefcase className="w-4 h-4 text-amber-400" />,
    SYSTEM_ADMIN: <Settings className="w-4 h-4 text-purple-400" />
  };

  return (
    <header
      style={{
        backgroundColor: theme.colors.bg.secondary,
        borderBottomColor: theme.colors.border,
      }}
      className="sticky top-0 z-40 w-full border-b px-6 py-3.5 flex items-center justify-between transition-colors duration-200"
    >
      {/* Brand & Search */}
      <div className="flex items-center space-x-4">
        <button
          onClick={onOpenSidebar}
          className="md:hidden p-2 rounded-lg transition-colors duration-200"
          style={{
            backgroundColor: theme.colors.bg.primary,
            color: theme.colors.text.secondary,
            borderColor: theme.colors.border,
          }}
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div
          className="flex items-center space-x-3 cursor-pointer"
          onClick={() => setActiveTab('dashboard')}
          style={{ color: theme.colors.text.primary }}
        >
          <div
            style={{ backgroundColor: theme.colors.accent }}
            className="w-9 h-9 rounded-xl flex items-center justify-center shadow-lg"
          >
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-base font-bold tracking-tight leading-none">
              Innovation Intelligence
            </h1>
            <p
              style={{ color: theme.colors.accent }}
              className="text-[11px] font-medium tracking-wide"
            >
              Research Funding & Analytics Platform
            </p>
          </div>
        </div>

        {/* Global Search Bar */}
        <div className="relative hidden md:block w-72">
          <Search
            className="w-4 h-4 absolute left-3 top-2.5"
            style={{ color: theme.colors.text.tertiary }}
          />
          <input
            type="text"
            placeholder="Search grants, patents, trends..."
            style={{
              backgroundColor: theme.colors.bg.primary,
              color: theme.colors.text.primary,
              borderColor: theme.colors.border,
            }}
            className="w-full text-xs pl-9 pr-4 py-2 rounded-lg border focus:outline-none transition-colors"
            onFocus={(e) => (e.target.style.borderColor = theme.colors.accent)}
            onBlur={(e) => (e.target.style.borderColor = theme.colors.border)}
          />
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-4">
        {/* Notifications Icon */}
        <button
          onClick={() => setActiveTab('notifications')}
          className="relative p-2 rounded-lg transition-colors duration-200"
          style={{
            backgroundColor: theme.colors.bg.primary,
            color: theme.colors.text.secondary,
            borderColor: theme.colors.border,
          }}
        >
          <Bell className="w-4 h-4" />
          {unreadNotificationsCount > 0 && (
            <span
              style={{ backgroundColor: theme.colors.error }}
              className="absolute -top-1 -right-1 w-4 h-4 text-white font-extrabold text-[9px] rounded-full flex items-center justify-center animate-pulse"
            >
              {unreadNotificationsCount}
            </span>
          )}
        </button>

        {/* Theme Toggle */}
        <button
          onClick={theme.toggleTheme}
          className="p-2 rounded-lg transition-colors duration-200"
          style={{
            backgroundColor: theme.colors.bg.primary,
            color: theme.colors.text.secondary,
            borderColor: theme.colors.border,
          }}
          title={theme.isDark ? 'Light Mode' : 'Dark Mode'}
        >
          {theme.isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>

        {/* User Menu */}
        <div className="relative">
          <button
            onClick={() => setUserMenuOpen(!userMenuOpen)}
            className="flex items-center space-x-2.5 pl-2 border-l transition-colors duration-200"
            style={{
              color: theme.colors.text.primary,
              borderLeftColor: theme.colors.border,
            }}
          >
            <div
              style={{ backgroundColor: theme.colors.accent + '20', borderColor: theme.colors.accent, color: theme.colors.accent }}
              className="w-8 h-8 rounded-lg border flex items-center justify-center text-xs font-bold"
            >
              {user?.full_name?.split(' ').map(n => n[0]).join('') || 'U'}
            </div>
            <div className="hidden sm:block text-left">
              <div className="text-xs font-semibold leading-tight">{user?.full_name}</div>
              <div
                style={{ color: theme.colors.text.tertiary }}
                className="text-[10px]"
              >
                {user?.email}
              </div>
            </div>
          </button>

          {userMenuOpen && (
            <div
              style={{
                backgroundColor: theme.colors.bg.primary,
                borderColor: theme.colors.border,
              }}
              className="absolute right-0 mt-2 w-48 border rounded-lg shadow-lg z-50"
            >
              <button
                onClick={() => {
                  logout();
                  setUserMenuOpen(false);
                }}
                className="w-full px-4 py-2 text-left flex items-center gap-2 text-sm rounded-lg transition-colors duration-200"
                style={{
                  color: theme.colors.error,
                }}
                onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = theme.colors.bg.tertiary)}
                onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
              >
                <LogOut size={16} />
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
