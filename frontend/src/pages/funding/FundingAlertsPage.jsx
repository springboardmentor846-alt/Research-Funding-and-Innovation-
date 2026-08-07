import { useState, useEffect } from 'react'
import { Bell, Plus, Trash2, Tag, Sparkles, CheckCircle2, Shield } from 'lucide-react'
import toast from 'react-hot-toast'
import { fundingService } from '@/services/fundingService'

export default function FundingAlertsPage() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)

  // Form state
  const [name, setName] = useState('')
  const [domainsInput, setDomainsInput] = useState('')
  const [keywordsInput, setKeywordsInput] = useState('')
  const [fundingType, setFundingType] = useState('Grant')
  const [frequency, setFrequency] = useState('weekly')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    loadAlerts()
  }, [])

  const loadAlerts = async () => {
    try {
      setLoading(true)
      const res = await fundingService.getMyAlerts()
      setAlerts(res)
    } catch (err) {
      toast.error('Failed to load funding alerts')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateAlert = async (e) => {
    e.preventDefault()
    if (!name.trim()) {
      toast.error('Please provide an alert name')
      return
    }

    try {
      setSubmitting(true)
      const domains = domainsInput.split(',').map((s) => s.trim()).filter(Boolean)
      const keywords = keywordsInput.split(',').map((s) => s.trim()).filter(Boolean)

      const payload = {
        name,
        research_domains: domains,
        keywords,
        funding_type: fundingType !== 'All' ? fundingType : undefined,
        frequency,
      }

      const created = await fundingService.createAlert(payload)
      toast.success('Funding alert created successfully!')
      setAlerts((prev) => [created, ...prev])
      setShowModal(false)
      setName('')
      setDomainsInput('')
      setKeywordsInput('')
    } catch (err) {
      toast.error('Failed to create funding alert')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDeleteAlert = async (alertId) => {
    try {
      await fundingService.deleteAlert(alertId)
      toast.success('Alert deleted')
      setAlerts((prev) => prev.filter((a) => a.id !== alertId))
    } catch (err) {
      toast.error('Failed to delete alert')
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white">
            Funding Search & Match Alerts
          </h1>
          <p className="text-surface-400 text-sm mt-1">
            Get automated notifications when new research grants matching your criteria are published.
          </p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary flex-shrink-0">
          <Plus className="w-4 h-4" /> Create Funding Alert
        </button>
      </div>

      {/* ── Alerts List ── */}
      {loading ? (
        <div className="flex items-center justify-center min-h-[300px]">
          <div className="w-10 h-10 border-4 border-brand-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : alerts.length === 0 ? (
        <div className="glass p-12 text-center space-y-4 max-w-md mx-auto">
          <Bell className="w-12 h-12 text-surface-500 mx-auto" />
          <h3 className="text-lg font-bold text-white">No funding alerts active</h3>
          <p className="text-surface-400 text-sm">
            Create customized alerts to track upcoming deadlines in your research domain.
          </p>
          <button onClick={() => setShowModal(true)} className="btn-primary text-xs">
            Create Your First Alert
          </button>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-5">
          {alerts.map((alert) => (
            <div key={alert.id} className="glass p-6 space-y-4 hover:border-brand-500/40 transition-all">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-brand-500/20 text-brand-400 flex items-center justify-center">
                    <Bell className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white">{alert.name}</h3>
                    <span className="badge bg-white/5 text-surface-400 text-[10px]">
                      Frequency: {alert.frequency}
                    </span>
                  </div>
                </div>

                <button
                  onClick={() => handleDeleteAlert(alert.id)}
                  className="p-2 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors"
                  title="Delete Alert"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              {alert.research_domains?.length > 0 && (
                <div className="space-y-1">
                  <p className="text-[11px] font-semibold text-surface-400">Target Domains:</p>
                  <div className="flex flex-wrap gap-1.5">
                    {alert.research_domains.map((d) => (
                      <span key={d} className="badge bg-brand-500/10 text-brand-300 text-[10px]">
                        {d}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {alert.keywords?.length > 0 && (
                <div className="space-y-1">
                  <p className="text-[11px] font-semibold text-surface-400">Keywords:</p>
                  <div className="flex flex-wrap gap-1.5">
                    {alert.keywords.map((k) => (
                      <span key={k} className="badge bg-accent-500/10 text-accent-300 text-[10px]">
                        #{k}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* ── Create Modal ── */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="glass max-w-lg w-full p-6 space-y-6 animate-scale-up">
            <div className="flex items-center justify-between border-b border-white/5 pb-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Bell className="w-5 h-5 text-brand-400" /> Create Funding Match Alert
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-surface-400 hover:text-white text-lg font-bold"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleCreateAlert} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-surface-300 mb-1 block">Alert Name *</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. AI Quantum Grants Weekly"
                  className="input-field text-sm"
                  required
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-surface-300 mb-1 block">Research Domains (comma-separated)</label>
                <input
                  type="text"
                  value={domainsInput}
                  onChange={(e) => setDomainsInput(e.target.value)}
                  placeholder="Artificial Intelligence, Quantum Computing"
                  className="input-field text-sm"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-surface-300 mb-1 block">Keywords (comma-separated)</label>
                <input
                  type="text"
                  value={keywordsInput}
                  onChange={(e) => setKeywordsInput(e.target.value)}
                  placeholder="CRISPR, Qubits, Neural Networks"
                  className="input-field text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-semibold text-surface-300 mb-1 block">Funding Type</label>
                  <select
                    value={fundingType}
                    onChange={(e) => setFundingType(e.target.value)}
                    className="input-field text-sm"
                  >
                    <option value="All">All Types</option>
                    <option value="Grant">Grant</option>
                    <option value="Contract">Contract</option>
                    <option value="Fellowship">Fellowship</option>
                    <option value="Equity">Equity</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-semibold text-surface-300 mb-1 block">Alert Frequency</label>
                  <select
                    value={frequency}
                    onChange={(e) => setFrequency(e.target.value)}
                    className="input-field text-sm"
                  >
                    <option value="daily">Daily Digest</option>
                    <option value="weekly">Weekly Digest</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/5">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="btn-secondary text-xs"
                >
                  Cancel
                </button>
                <button type="submit" disabled={submitting} className="btn-primary text-xs">
                  {submitting ? 'Creating...' : 'Save Alert'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
