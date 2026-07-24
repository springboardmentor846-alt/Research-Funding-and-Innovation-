import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { fundingService, authService, extractErrorMessage } from '../services/api'
import Loading from '../components/Loading'
import EmptyState from '../components/EmptyState'

const SOURCE_LABELS = {
  government_grant: 'Government Grant',
  research_council: 'Research Council',
  innovation_fund: 'Innovation Fund',
  startup_accelerator: 'Startup Accelerator',
  venture_program: 'Venture Program',
  international_agency: 'International Agency',
}

const fmtAmount = (min, max, cur = 'USD') => {
  const f = (n) => {
    const v = Number(n)
    if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(v % 1_000_000 ? 1 : 0)}M`
    if (v >= 1000) return `${Math.round(v / 1000)}K`
    return `${v}`
  }
  if (min == null && max == null) return null
  if (min != null && max != null) return `${cur} ${f(min)}–${f(max)}`
  return `${cur} ${f(min ?? max)}`
}

function OpportunityCard({ opp, score, eligible, matched, reasons }) {
  const amount = fmtAmount(opp.amount_min, opp.amount_max, opp.currency)
  return (
    <div className="opp-card">
      <div className="opp-head">
        <div>
          <a href={opp.url} target="_blank" rel="noreferrer" className="opp-title">{opp.title}</a>
          <div className="muted">{opp.agency}</div>
        </div>
        {score != null && (
          <div className={`score-pill ${eligible ? '' : 'score-ineligible'}`}>
            {Math.round(score)}% match
          </div>
        )}
      </div>

      <p className="opp-desc">{opp.description}</p>

      <div className="opp-tags">
        <span className="src-tag">{SOURCE_LABELS[opp.source_type] || opp.source_type}</span>
        {amount && <span className="meta-tag">{amount}</span>}
        {opp.deadline && <span className="meta-tag">Deadline {opp.deadline}</span>}
        {opp.countries?.length > 0 && <span className="meta-tag">{opp.countries.join(', ')}</span>}
      </div>

      {matched?.length > 0 && (
        <div className="matched">Matches your profile: {matched.map((m) => (
          <span key={m} className="match-chip">{m}</span>
        ))}</div>
      )}

      {reasons?.length > 0 && (
        <div className={`elig-note ${eligible ? 'elig-ok' : 'elig-no'}`}>
          {eligible ? '✓ Eligible' : '✕ Not eligible'} — {reasons.join(' · ')}
        </div>
      )}
    </div>
  )
}

export default function Funding() {
  const [tab, setTab] = useState('recommended')
  const [recs, setRecs] = useState([])
  const [all, setAll] = useState([])
  const [eligibleOnly, setEligibleOnly] = useState(false)
  const [sourceFilter, setSourceFilter] = useState('')
  const [query, setQuery] = useState('')
  const [searchResults, setSearchResults] = useState(null)
  const [error, setError] = useState('')
  const [noProfile, setNoProfile] = useState(false)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    fundingService.recommendations({ limit: 20 })
      .then((res) => setRecs(res.data))
      .catch((err) => {
        if (err.response?.status === 401) { authService.logout(); navigate('/login') }
        else if (err.response?.status === 400) { setNoProfile(true); setTab('browse') }
        else setError(extractErrorMessage(err))
      })
      .finally(() => setLoading(false))

    fundingService.list().then((res) => setAll(res.data)).catch(() => {})
  }, [navigate])

  const runSearch = async (e) => {
    e.preventDefault()
    if (query.trim().length < 2) { setSearchResults(null); return }
    try {
      const res = await fundingService.search(query.trim())
      setSearchResults(res.data)
    } catch (err) { setError(extractErrorMessage(err)) }
  }

  const shownRecs = eligibleOnly ? recs.filter((r) => r.eligible) : recs
  const browseList = (searchResults ?? all).filter(
    (o) => !sourceFilter || o.source_type === sourceFilter
  )

  if (loading) return <Loading message="Loading funding opportunities…" />

  return (
    <div className="dashboard">
      <h1>Funding Discovery</h1>
        {error && <div className="error">{error}</div>}

        <div className="tabs">
          <button className={tab === 'recommended' ? 'tab active' : 'tab'}
                  onClick={() => setTab('recommended')} disabled={noProfile}>
            Recommended for you
          </button>
          <button className={tab === 'browse' ? 'tab active' : 'tab'}
                  onClick={() => setTab('browse')}>
            Browse & search all
          </button>
        </div>

        {tab === 'recommended' && (
          <>
            {noProfile ? (
              <div className="card">
                <p>Create your research profile to get personalized funding recommendations.</p>
                <Link to="/profile"><button style={{ marginTop: 12, width: 'auto', padding: '10px 18px' }}>
                  Go to My Profile</button></Link>
              </div>
            ) : (
              <>
                <label className="checkbox-row">
                  <input type="checkbox" checked={eligibleOnly}
                         onChange={(e) => setEligibleOnly(e.target.checked)} />
                  Show only opportunities I'm eligible for
                </label>
                <p className="muted" style={{ marginBottom: 12 }}>
                  Ranked against your research profile ({shownRecs.length} shown)
                </p>
                {shownRecs.length === 0
                  ? <EmptyState>No matching opportunities. Try adding more research domains or keywords to your profile.</EmptyState>
                  : shownRecs.map((r) => (
                      <OpportunityCard key={r.opportunity.id} opp={r.opportunity}
                        score={r.relevance_score} eligible={r.eligible}
                        matched={r.matched_terms} reasons={r.reasons} />
                    ))}
              </>
            )}
          </>
        )}

        {tab === 'browse' && (
          <>
            <form onSubmit={runSearch} className="search-row">
              <input placeholder="Search grants by title, agency or keyword..."
                     value={query} onChange={(e) => setQuery(e.target.value)} />
              <button type="submit">Search</button>
              {searchResults && (
                <button type="button" className="close-results-btn"
                        onClick={() => { setSearchResults(null); setQuery('') }}>Clear</button>
              )}
            </form>

            <select value={sourceFilter} onChange={(e) => setSourceFilter(e.target.value)}
                    style={{ maxWidth: 280, marginBottom: 16 }}>
              <option value="">All funding types</option>
              {Object.entries(SOURCE_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>

            <p className="muted" style={{ marginBottom: 12 }}>
              {searchResults ? `${browseList.length} search result(s)` : `${browseList.length} opportunities`}
            </p>
            {browseList.length === 0
              ? <EmptyState>No opportunities found.</EmptyState>
              : browseList.map((o) => <OpportunityCard key={o.id} opp={o} />)}
          </>
        )}
    </div>
  )
}
