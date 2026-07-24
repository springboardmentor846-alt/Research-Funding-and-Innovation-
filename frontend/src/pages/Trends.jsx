import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid,
  BarChart, Bar,
} from 'recharts'
import { trendsService, authService, extractErrorMessage } from '../services/api'
import Loading from '../components/Loading'

const CHART = { line: '#1e293b', bar: '#cca01a', grid: '#e3e7ee' }

const truncate = (s, n = 26) => (s.length > n ? `${s.slice(0, n - 1).trimEnd()}…` : s)

const TopicTick = ({ x, y, payload }) => (
  <text x={x} y={y} dy={4} textAnchor="end" fontSize={12} fill="var(--ink)">
    {truncate(payload.value)}
  </text>
)

const fmt = (n) => {
  const v = Number(n)
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`
  if (v >= 1000) return `${(v / 1000).toFixed(1)}K`
  return `${v}`
}

export default function Trends() {
  const [query, setQuery] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    trendsService.myDomain()
      .then((res) => { setData(res.data); setQuery(res.data.query) })
      .catch((err) => {
        if (err.response?.status === 401) { authService.logout(); navigate('/login') }
      })
      .finally(() => setLoading(false))
  }, [navigate])

  const analyze = async (e) => {
    e?.preventDefault()
    if (query.trim().length < 2) return
    setLoading(true); setError('')
    try {
      const res = await trendsService.analyze(query.trim())
      setData(res.data)
    } catch (err) {
      setError(extractErrorMessage(err, 'Could not load trends'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="dashboard" style={{ maxWidth: 1000 }}>
        <h1>Research Trend Intelligence</h1>

        <form onSubmit={analyze} className="search-row">
          <input placeholder="Analyze a research topic (e.g. quantum computing)..."
                 value={query} onChange={(e) => setQuery(e.target.value)} />
          <button type="submit">Analyze</button>
        </form>

        {error && <div className="error">{error}</div>}
        {loading && <Loading message="Analyzing research landscape…" />}

        {!loading && !data && (
          <div className="card">
            <p className="muted">
              Search a topic above, or add research domains to your profile to see
              trends for your field automatically.
            </p>
          </div>
        )}

        {!loading && data && (
          <>
            {data.from_profile && (
              <p className="muted" style={{ marginBottom: 12 }}>
                Showing trends for your profile: <strong>{data.query}</strong>
              </p>
            )}

            <div className="stat-grid">
              <div className="stat-card">
                <span className="stat-num">{fmt(data.total_works)}</span>
                Total Publications
              </div>
              <div className="stat-card">
                <span className="stat-num">{data.hotspots.length}</span>
                Active Research Topics
              </div>
              <div className="stat-card">
                <span className="stat-num">{data.emerging_topics.length}</span>
                Emerging Topics
              </div>
            </div>

            <div className="card">
              <h2>Publication Trend Over Time</h2>
              <p className="muted" style={{ marginBottom: 16 }}>Papers published per year</p>
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={data.works_by_year}>
                  <CartesianGrid strokeDasharray="3 3" stroke={CHART.grid} />
                  <XAxis dataKey="year" />
                  <YAxis tickFormatter={fmt} width={64} />
                  <Tooltip formatter={(v) => [v.toLocaleString(), 'Publications']} />
                  <Line type="monotone" dataKey="count" stroke={CHART.line} strokeWidth={2.5}
                        dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="card">
              <h2>Research Hotspots</h2>
              <p className="muted" style={{ marginBottom: 16 }}>Most active topics in this field</p>
              <ResponsiveContainer width="100%" height={Math.max(220, data.hotspots.length * 34)}>
                <BarChart data={data.hotspots} layout="vertical"
                          margin={{ left: 20, right: 20 }}>
                  <XAxis type="number" tickFormatter={fmt} />
                  <YAxis type="category" dataKey="topic" width={200}
                         tick={<TopicTick />} interval={0} />
                  <Tooltip formatter={(v) => [v.toLocaleString(), 'Publications']}
                           labelFormatter={(l) => l} />
                  <Bar dataKey="count" fill={CHART.bar} radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="card">
              <h2>Emerging Topics</h2>
              <p className="muted" style={{ marginBottom: 12 }}>
                Rising in relative share over the last ~3 years
              </p>
              {data.emerging_topics.length === 0 ? (
                <p className="muted">No strongly emerging topics detected for this query.</p>
              ) : (
                data.emerging_topics.map((t) => (
                  <div key={t.topic} className="entry" style={{ display: 'flex' }}>
                    <span>{t.topic}</span>
                    <span className="match-chip" style={{ background: 'var(--info-soft)', color: 'var(--info)' }}>
                      ▲ {t.growth}% rising
                    </span>
                  </div>
                ))
              )}
            </div>

            <div className="card">
              <h2>Most-Cited Papers</h2>
              <p className="muted" style={{ marginBottom: 12 }}>Citation analytics for this field</p>
              {data.top_papers.map((p, i) => (
                <div key={i} className="entry" style={{ display: 'block' }}>
                  <a href={p.url} target="_blank" rel="noreferrer" className="opp-title"
                     style={{ fontSize: 14 }}>{p.title}</a>
                  <div className="muted" style={{ fontSize: 12, marginTop: 4 }}>
                    {p.venue && `${p.venue} · `}{p.year} · {p.cited_by_count.toLocaleString()} citations
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
    </div>
  )
}
