import React, { useState } from 'react';
import { Bell, CheckCircle2, Filter, AlertCircle, Bookmark, Sparkles } from 'lucide-react';

export const NotificationCenter = () => {
  const [filter, setFilter] = useState('ALL');
  const [notifications, setNotifications] = useState([
    {
      id: '1',
      title: 'New Grant Match: NSF AI & Quantum Systems',
      message: 'Your research profile matches the NSF AI & Quantum Information Systems Convergence Grant with a 92.5% eligibility match score.',
      category: 'funding',
      read: false,
      date: '10 mins ago'
    },
    {
      id: '2',
      title: 'Patent Citation Alert: US-11894562-B2',
      message: 'Your patent US-11894562-B2 was cited by Google Quantum AI Lab in a new filing.',
      category: 'patent',
      read: false,
      date: '2 hours ago'
    },
    {
      id: '3',
      title: 'Trend Surge: Neuromorphic Edge AI (+148% Growth)',
      message: 'Neuromorphic Edge AI topic publication velocity increased by 148.5% YoY in Nature & IEEE journals.',
      category: 'trend',
      read: true,
      date: '1 day ago'
    }
  ]);

  const markAllRead = () => {
    setNotifications(notifications.map(n => ({ ...n, read: true })));
  };

  const filtered = notifications.filter(n => filter === 'ALL' || n.category === filter);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-100 tracking-tight flex items-center space-x-2">
            <Bell className="w-6 h-6 text-cyan-400" />
            <span>Notification & Alert System</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time alerts for funding calls, patent citations, emerging research trends, and commercialization signals.
          </p>
        </div>

        <button 
          onClick={markAllRead}
          className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 hover:text-cyan-400 font-medium transition-colors"
        >
          Mark All as Read
        </button>
      </div>

      {/* Filter Chips */}
      <div className="flex items-center space-x-2">
        {['ALL', 'funding', 'patent', 'trend'].map(cat => (
          <button
            key={cat}
            onClick={() => setFilter(cat)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition-colors ${
              filter === cat
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                : 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-slate-200'
            }`}
          >
            {cat === 'ALL' ? 'All Alerts' : cat}
          </button>
        ))}
      </div>

      {/* Notifications List */}
      <div className="space-y-3">
        {filtered.map(n => (
          <div key={n.id} className={`p-4 rounded-xl glass-panel border flex items-start justify-between gap-4 ${n.read ? 'border-slate-800/80 opacity-80' : 'border-cyan-500/30 bg-cyan-950/10'}`}>
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                {!n.read && <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>}
                <span className="text-xs font-bold text-slate-100">{n.title}</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800 uppercase font-semibold">{n.category}</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">{n.message}</p>
            </div>
            <span className="text-[10px] text-slate-500 whitespace-nowrap">{n.date}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
