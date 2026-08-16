import React, { useEffect } from 'react';
import { Navbar } from '../components/common/Navbar';
import { Sidebar } from '../components/common/Sidebar';
import { Footer } from '../components/common/Footer';
import { useNotifications } from '../contexts/NotificationContext';
import { Bell, Check, Sparkles, Shield, DollarSign } from 'lucide-react';

export const NotificationsPage = () => {
  const { notifications, fetchNotifications, markAsRead } = useNotifications();

  useEffect(() => {
    fetchNotifications();
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />
      <div className="flex-1 flex">
        <Sidebar />
        <main className="flex-1 p-8 space-y-8 overflow-y-auto">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight gradient-text flex items-center space-x-2">
              <Bell className="w-8 h-8 text-blue-400" />
              <span>Real-Time Notifications & System Alerts</span>
            </h1>
            <p className="text-sm text-slate-400 mt-1">Live telemetry on grant eligibility changes, patent citations, and system notifications.</p>
          </div>

          <div className="space-y-4 max-w-4xl">
            {notifications.map((n) => (
              <div
                key={n.id}
                className={`glass-card p-6 flex items-start justify-between gap-4 border-l-4 ${
                  n.is_read ? 'border-l-slate-700 opacity-75' : 'border-l-blue-500'
                }`}
              >
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="px-2.5 py-0.5 bg-blue-500/10 text-blue-400 text-xs font-bold rounded-md uppercase">
                      {n.type}
                    </span>
                    <span className="text-xs text-slate-500">{new Date(n.created_at).toLocaleString()}</span>
                  </div>
                  <h4 className="text-lg font-bold text-slate-100">{n.title}</h4>
                  <p className="text-sm text-slate-300">{n.message}</p>
                </div>

                {!n.is_read && (
                  <button
                    onClick={() => markAsRead(n.id)}
                    className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs flex items-center space-x-1"
                  >
                    <Check className="w-4 h-4 text-emerald-400" />
                    <span>Mark Read</span>
                  </button>
                )}
              </div>
            ))}
          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
};
