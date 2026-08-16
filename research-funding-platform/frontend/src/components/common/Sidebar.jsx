import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  LayoutDashboard, User, Search, Sparkles, BookOpen,
  FileCheck, Cpu, Gauge, Briefcase, FileText, Bell, Settings, ShieldAlert
} from 'lucide-react';

export const Sidebar = () => {
  const { user } = useAuth();

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Research Profile', path: '/profile', icon: User },
    { label: 'Funding Discovery', path: '/funding', icon: Search },
    { label: 'Grant Matching AI', path: '/recommendations', icon: Sparkles },
    { label: 'Research Intelligence', path: '/research-trends', icon: BookOpen },
    { label: 'Patent Intelligence', path: '/patent-analytics', icon: FileCheck },
    { label: 'Tech Intelligence', path: '/tech-intelligence', icon: Cpu },
    { label: 'Innovation Score', path: '/innovation-score', icon: Gauge },
    { label: 'Commercialization', path: '/commercialization', icon: Briefcase },
    { label: 'Reports Engine', path: '/reports', icon: FileText },
    { label: 'Notifications', path: '/notifications', icon: Bell },
    { label: 'Settings', path: '/settings', icon: Settings },
  ];

  if (user?.role === 'Administrator') {
    navItems.push({ label: 'Admin Panel', path: '/admin', icon: ShieldAlert });
  }

  return (
    <aside className="w-64 bg-slate-950/90 border-r border-slate-800/80 min-h-[calc(100vh-4rem)] p-4 flex flex-col justify-between">
      <div className="space-y-1">
        <div className="px-3 py-2 text-xs font-bold text-slate-500 uppercase tracking-wider">
          Platform Intelligence
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-sm transition-all duration-200 ${
                  isActive
                    ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-inner'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </div>

      <div className="p-3 bg-slate-900/80 border border-slate-800 rounded-xl">
        <div className="text-xs text-slate-400">Connected Role</div>
        <div className="text-sm font-semibold text-teal-400">{user?.role || 'Guest'}</div>
        <div className="text-xs text-slate-500 truncate mt-0.5">{user?.organization}</div>
      </div>
    </aside>
  );
};
