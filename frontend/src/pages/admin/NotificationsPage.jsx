import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Bell, CheckCheck, Coins, Lightbulb, Handshake,
  BookOpen, CheckCircle2, ChevronRight, Sparkles
} from 'lucide-react'
import { reportsNotificationsService } from '@/services/reportsNotificationsService'
import toast from 'react-hot-toast'

const TYPE_ICONS = {
  funding_reminder: Coins,
  recommendation: BookOpen,
  patent_update: Lightbulb,
  commercialization_alert: Handshake,
}

const TYPE_COLORS = {
  funding_reminder: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
  recommendation: 'text-brand-400 bg-brand-500/10 border-brand-500/20',
  patent_update: 'text-accent-400 bg-accent-500/10 border-accent-500/20',
  commercialization_alert: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
}

export default function NotificationsPage() {
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchNotifications()
  }, [])

  const fetchNotifications = async () => {
    try {
      setIsLoading(true)
      const res = await reportsNotificationsService.getNotifications()
      setData(res)
    } catch (err) {
      toast.error('Failed to load notifications.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleMarkAsRead = async (notifId) => {
    try {
      await reportsNotificationsService.markAsRead(notifId)
      fetchNotifications()
    } catch (err) {
      toast.error('Failed to mark notification as read.')
    }
  }

  const handleMarkAllAsRead = async () => {
    try {
      const res = await reportsNotificationsService.markAllAsRead()
      toast.success(res.message)
      fetchNotifications()
    } catch (err) {
      toast.error('Failed to mark all as read.')
    }
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="w-12 h-12 rounded-full border-4 border-brand-500 border-t-transparent animate-spin" />
        <p className="text-surface-400 text-sm animate-pulse">Loading Notifications...</p>
      </div>
    )
  }

  const { notifications = [], unread_count = 0 } = data || {}

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass p-6 rounded-2xl border border-white/10">
        <div>
          <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs tracking-wider uppercase mb-1">
            <Bell className="w-4 h-4" /> Platform Alerts & Reminders
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white flex items-center gap-3">
            Notifications Center
            {unread_count > 0 && (
              <span className="text-xs font-bold px-3 py-1 rounded-full bg-accent-500/20 text-accent-400 border border-accent-500/30">
                {unread_count} Unread
              </span>
            )}
          </h1>
          <p className="text-surface-400 text-sm mt-1">
            Funding deadlines, AI research paper recommendations, patent updates, and commercialization inquiries.
          </p>
        </div>

        {unread_count > 0 && (
          <button
            onClick={handleMarkAllAsRead}
            className="btn-secondary text-xs py-2.5 px-4 flex items-center gap-2 flex-shrink-0"
          >
            <CheckCheck className="w-4 h-4 text-emerald-400" />
            Mark All as Read
          </button>
        )}
      </div>

      {/* ── Notifications List ── */}
      {notifications.length === 0 ? (
        <div className="glass p-12 rounded-2xl border border-white/10 text-center space-y-3">
          <Bell className="w-12 h-12 text-surface-500 mx-auto" />
          <h3 className="text-lg font-bold text-white">No Notifications</h3>
          <p className="text-surface-400 text-xs">You have no system alerts or notifications at this time.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {notifications.map((notif) => {
            const Icon = TYPE_ICONS[notif.notification_type] || Bell
            const style = TYPE_COLORS[notif.notification_type] || 'text-brand-400 bg-brand-500/10'

            return (
              <div
                key={notif.id}
                className={`glass p-5 rounded-2xl border transition-all flex items-start gap-4 ${
                  notif.is_read ? 'border-white/5 opacity-80' : 'border-brand-500/30 bg-brand-500/5'
                }`}
              >
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center border flex-shrink-0 mt-0.5 ${style}`}>
                  <Icon className="w-5 h-5" />
                </div>

                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between gap-2">
                    <h3 className="text-base font-bold text-white">{notif.title}</h3>
                    <span className="text-[11px] text-surface-500 font-mono">
                      {new Date(notif.created_at).toLocaleString()}
                    </span>
                  </div>

                  <p className="text-xs text-surface-300 leading-relaxed">{notif.message}</p>

                  {/* Actions Row */}
                  <div className="flex items-center justify-between pt-2">
                    {notif.link_url ? (
                      <Link
                        to={notif.link_url}
                        className="text-xs text-brand-400 hover:underline flex items-center gap-1 font-medium"
                      >
                        View Related Details <ChevronRight className="w-3.5 h-3.5" />
                      </Link>
                    ) : (
                      <span />
                    )}

                    {!notif.is_read && (
                      <button
                        onClick={() => handleMarkAsRead(notif.id)}
                        className="text-xs text-surface-400 hover:text-white flex items-center gap-1"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" /> Mark Read
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
