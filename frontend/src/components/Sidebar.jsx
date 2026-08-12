import React from 'react';
import { useTheme } from '../context/ThemeContext';
import { 
  LayoutDashboard, Search, TrendingUp, ShieldCheck, 
  Cpu, Award, Bell, FileSpreadsheet, ChevronRight, Bookmark, Sparkles, X
} from 'lucide-react';

export const Sidebar = ({ activeTab, setActiveTab, isOpen = false, onClose }) => {
  const theme = useTheme();
  const menuItems = [
    { id: 'dashboard', label: 'Overview Dashboard', icon: LayoutDashboard, section: 'core' },
    { id: 'funding', label: 'Funding Opportunity Discovery', icon: Search, section: 'core' },
    { id: 'research', label: 'Research Trend Intelligence', icon: TrendingUp, section: 'core' },
    { id: 'patents', label: 'Patent Landscape Analysis', icon: ShieldCheck, section: 'core' },
    { id: 'technology', label: 'Technology Intelligence (TRL)', icon: Cpu, section: 'core' },
    { id: 'scoring', label: 'Innovation Scoring Engine', icon: Award, section: 'core' },
    { id: 'saved', label: 'Saved Funding Opportunities', icon: Bookmark, section: 'advanced' },
    { id: 'ai', label: 'AI Research Concierge', icon: Sparkles, section: 'advanced' },
    { id: 'notifications', label: 'Notifications & Alerts', icon: Bell, section: 'advanced' },
    { id: 'reports', label: 'Reports & Export Center', icon: FileSpreadsheet, section: 'advanced' },
  ];

  return (
    <>
      <aside
        style={{
          backgroundColor: theme.colors.bg.secondary,
          borderRightColor: theme.colors.border,
        }}
        className="w-64 border-r min-h-[calc(100vh-61px)] p-4 flex flex-col justify-between hidden md:flex transition-colors duration-200"
      >
        <div className="space-y-1.5">
        {['core', 'advanced'].map((section) => {
          const sectionItems = menuItems.filter((item) => item.section === section);
          return (
            <div key={section} className="space-y-1.5">
              <div
                style={{ color: theme.colors.text.tertiary }}
                className="px-3 pb-2 text-[10px] uppercase font-bold tracking-wider"
              >
                {section === 'core' ? 'Intelligence Modules' : 'Advanced Tools'}
              </div>
              {sectionItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    style={{
                      backgroundColor: isActive ? theme.colors.accent + '20' : 'transparent',
                      color: isActive ? theme.colors.accent : theme.colors.text.tertiary,
                      borderColor: isActive ? theme.colors.accent + '50' : 'transparent',
                    }}
                    className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all border hover:transition-colors duration-200"
                    onMouseEnter={(e) => {
                      if (!isActive) {
                        e.currentTarget.style.backgroundColor = theme.colors.bg.tertiary;
                        e.currentTarget.style.color = theme.colors.text.primary;
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!isActive) {
                        e.currentTarget.style.backgroundColor = 'transparent';
                        e.currentTarget.style.color = theme.colors.text.tertiary;
                      }
                    }}
                  >
                    <div className="flex items-center space-x-3">
                      <Icon className="w-4 h-4" />
                      <span>{item.label}</span>
                    </div>
                    {isActive && <ChevronRight className="w-3.5 h-3.5" />}
                  </button>
                );
              })}
            </div>
          );
        })}
      </div>

    </aside>

      {isOpen && (
        <div className="fixed inset-0 z-50 flex md:hidden">
          <button
            type="button"
            onClick={onClose}
            className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm"
            aria-label="Close navigation menu"
          />
          <section
            style={{ backgroundColor: theme.colors.bg.secondary, borderColor: theme.colors.border }}
            className="relative z-10 w-[85vw] max-w-sm border-r p-4 overflow-y-auto"
          >
            <div className="flex items-center justify-between mb-5">
              <div className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-300">Menu</div>
              <button
                type="button"
                onClick={onClose}
                className="p-2 rounded-lg text-slate-300 hover:bg-slate-900/50"
                aria-label="Close menu"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-1.5">
              {['core', 'advanced'].map((section) => {
                const sectionItems = menuItems.filter((item) => item.section === section);
                return (
                  <div key={section} className="space-y-1.5">
                    <div
                      style={{ color: theme.colors.text.tertiary }}
                      className="px-3 pb-2 text-[10px] uppercase font-bold tracking-wider"
                    >
                      {section === 'core' ? 'Intelligence Modules' : 'Advanced Tools'}
                    </div>
                    {sectionItems.map((item) => {
                      const Icon = item.icon;
                      const isActive = activeTab === item.id;
                      return (
                        <button
                          key={item.id}
                          onClick={() => {
                            setActiveTab(item.id);
                            onClose?.();
                          }}
                          style={{
                            backgroundColor: isActive ? theme.colors.accent + '20' : 'transparent',
                            color: isActive ? theme.colors.accent : theme.colors.text.tertiary,
                            borderColor: isActive ? theme.colors.accent + '50' : 'transparent',
                          }}
                          className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all border hover:transition-colors duration-200"
                        >
                          <div className="flex items-center space-x-3">
                            <Icon className="w-4 h-4" />
                            <span>{item.label}</span>
                          </div>
                          {isActive && <ChevronRight className="w-3.5 h-3.5" />}
                        </button>
                      );
                    })}
                  </div>
                );
              })}
            </div>
          </section>
        </div>
      )}
    </>
  );
};
