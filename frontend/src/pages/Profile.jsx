import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { profileService, authService, datasetService } from '../services/api'
import Loading from '../components/Loading'

function TagInput({ label, tags, onChange }) {
  const [draft, setDraft] = useState('')

  const add = () => {
    const v = draft.trim()
    if (v && !tags.includes(v)) onChange([...tags, v])
    setDraft('')
  }
  const remove = (t) => onChange(tags.filter((x) => x !== t))

  return (
    <div className="field">
      <label>{label}</label>
      <div className="tag-list">
        {tags.map((t) => (
          <span key={t} className="tag">
            {t}<button type="button" onClick={() => remove(t)}>×</button>
          </span>
        ))}
      </div>
      <input
        value={draft}
        placeholder="Type and press Enter"
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ',') { e.preventDefault(); add() }
        }}
      />
    </div>
  )
}

const EMPTY = {
  headline: '', bio: '', research_domains: [], keywords: [],
  technology_areas: [], organization: '', organization_type: '',
  country: '', website: '', orcid_id: '',
}

export default function Profile() {
  const [profile, setProfile] = useState(EMPTY)
  const [exists, setExists] = useState(false)
  const [pubs, setPubs] = useState([])
  const [patents, setPatents] = useState([])
  const [status, setStatus] = useState('')
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    profileService.get()
      .then((res) => {
        setProfile({ ...EMPTY, ...res.data })
        setExists(true)
        setPubs(res.data.publications || [])
        setPatents(res.data.patents || [])
      })
      .catch((err) => {
        if (err.response?.status === 401) { authService.logout(); navigate('/login') }
      })
      .finally(() => setLoading(false))
  }, [navigate])

  const set = (field) => (e) => setProfile({ ...profile, [field]: e.target.value })

  const saveProfile = async (e) => {
    e.preventDefault()
    setStatus('Saving...')
    try {
      const call = exists ? profileService.update : profileService.create
      const res = await call(profile)
      setProfile({ ...EMPTY, ...res.data })
      setExists(true)
      setStatus('✓ Profile saved')
    } catch (err) {
      setStatus(err.response?.data?.detail || 'Save failed')
    }
  }

  const deleteAccount = async () => {
    if (!window.confirm(
      'This will permanently delete your account along with your profile, publications, and patents. This action cannot be undone. Do you want to continue?'
    )) return
    try {
      await authService.deleteMyAccount()
      authService.logout()
      navigate('/register')
    } catch {
      setStatus('Could not delete your account. Please try again.')
    }
  }

  if (loading) return <Loading message="Loading your profile…" />

  return (
    <div className="dashboard">
      <h1>Research Profile</h1>
      {status && <div className="status">{status}</div>}

      <form className="card" onSubmit={saveProfile}>
          <h2>Profile Information</h2>
          <div className="field">
            <label>Headline</label>
            <input value={profile.headline || ''} onChange={set('headline')}
                   placeholder="e.g. Professor of Materials Science" />
          </div>
          <div className="field">
            <label>Bio</label>
            <textarea rows={3} value={profile.bio || ''} onChange={set('bio')} />
          </div>

          <TagInput label="Research Domains" tags={profile.research_domains}
                    onChange={(v) => setProfile({ ...profile, research_domains: v })} />
          <TagInput label="Keywords" tags={profile.keywords}
                    onChange={(v) => setProfile({ ...profile, keywords: v })} />
          <TagInput label="Technology Areas" tags={profile.technology_areas}
                    onChange={(v) => setProfile({ ...profile, technology_areas: v })} />

          <div className="grid-2">
            <div className="field">
              <label>Organization</label>
              <input value={profile.organization || ''} onChange={set('organization')} />
            </div>
            <div className="field">
              <label>Organization Type</label>
              <input value={profile.organization_type || ''} onChange={set('organization_type')}
                     placeholder="university / company / research council" />
            </div>
            <div className="field">
              <label>Country</label>
              <input value={profile.country || ''} onChange={set('country')} />
            </div>
            <div className="field">
              <label>Website</label>
              <input value={profile.website || ''} onChange={set('website')} />
            </div>
            <div className="field">
              <label>ORCID iD</label>
              <input value={profile.orcid_id || ''} onChange={set('orcid_id')} />
            </div>
          </div>

          <button type="submit">{exists ? 'Update Profile' : 'Create Profile'}</button>
        </form>

        {exists ? (
          <>
            <PublicationsSection items={pubs} setItems={setPubs} />
            <PatentsSection items={patents} setItems={setPatents} />
          </>
        ) : (
          <p style={{ color: '#718096' }}>
            Save your profile first to start adding publications and patents.
          </p>
        )}

        <div className="card account-card">
          <h2>Account</h2>
          <div className="account-row">
            <div>
              <strong>Delete account</strong>
              <p className="muted" style={{ marginTop: 4 }}>
                Permanently remove your account and all associated data, including your
                profile, publications, and patents. This cannot be undone.
              </p>
            </div>
            <button className="delete-account-btn" onClick={deleteAccount}>Delete account</button>
          </div>
        </div>
    </div>
  )
}

function DatasetSearch({ kind, onImport }) {
  const [q, setQ] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [importedKeys, setImportedKeys] = useState(new Set())
  const [showResults, setShowResults] = useState(false)
  const source = kind === 'publication' ? 'OpenAlex' : 'Google Patents'

  const search = async (e) => {
    e.preventDefault()
    if (q.trim().length < 2) return
    setLoading(true); setError(''); setResults([]); setShowResults(false)
    try {
      const call = kind === 'publication'
        ? datasetService.searchPublications : datasetService.searchPatents
      const res = await call(q.trim())
      setResults(res.data.results)
      setShowResults(true)
      if (res.data.results.length === 0) setError('No results found.')
    } catch (err) {
      setError(err.response?.data?.detail || `Could not reach ${source}.`)
      setShowResults(true)
    } finally {
      setLoading(false)
    }
  }

  const handleImport = async (rec, key) => {
    await onImport(rec)
    setImportedKeys((prev) => new Set(prev).add(key))
  }

  const closeResults = () => {
    setResults([])
    setError('')
    setShowResults(false)
    setImportedKeys(new Set())
  }

  return (
    <div className="dataset-search">
      <form className="search-bar" onSubmit={search}>
        <input value={q} onChange={(e) => setQ(e.target.value)}
               placeholder={`Search ${source} for ${kind}s to import...`} />
        <button type="submit" disabled={loading}>{loading ? 'Searching...' : 'Search'}</button>
      </form>

      {showResults && (
        <div className="search-results-panel">
          <div className="search-results-header">
            <span className="results-count">
              {results.length > 0
                ? `${results.length} result${results.length !== 1 ? 's' : ''} found`
                : 'No results'}
            </span>
            <button
              type="button"
              className="close-results-btn"
              onClick={closeResults}
              title="Close search results"
            >
              ✕ Close
            </button>
          </div>

          {error && <div className="muted" style={{ marginTop: 8 }}>{error}</div>}

          {results.map((r, i) => {
            const key = (kind === 'publication' ? r.doi : r.patent_number) || `${i}-${r.title}`
            const imported = importedKeys.has(key)
            return (
              <div key={key} className="result">
                <div>
                  <strong>{r.title}</strong>
                  <div className="muted">
                    {kind === 'publication'
                      ? `${(r.authors || []).slice(0, 3).join(', ')}${r.venue ? ' · ' + r.venue : ''}${r.year ? ' · ' + r.year : ''}${r.citation_count ? ' · ' + r.citation_count + ' cites' : ''}`
                      : `${r.patent_number || ''}${r.assignee ? ' · ' + r.assignee : ''}${r.filing_date ? ' · filed ' + r.filing_date : ''}`}
                  </div>
                </div>
                <button type="button" className="mini-import" disabled={imported}
                        onClick={() => handleImport(r, key)}>
                  {imported ? '✓ Imported' : 'Import'}
                </button>
              </div>
            )
          })}

          {results.length > 3 && (
            <div style={{ textAlign: 'center', marginTop: 12 }}>
              <button type="button" className="close-results-btn" onClick={closeResults}>
                ✕ Close Results
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function PublicationsSection({ items, setItems }) {
  const blank = { title: '', authors: [], venue: '', year: '', doi: '', url: '', citation_count: 0, abstract: '' }
  const [form, setForm] = useState(blank)
  const [error, setError] = useState('')

  const add = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const payload = { ...form, year: form.year ? Number(form.year) : null,
                        citation_count: Number(form.citation_count) || 0 }
      const res = await profileService.addPublication(payload)
      setItems([...items, res.data])
      setForm(blank)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add publication')
    }
  }

  const remove = async (id) => {
    await profileService.deletePublication(id)
    setItems(items.filter((p) => p.id !== id))
  }

  const importPublication = async (rec) => {
    const res = await profileService.addPublication(rec)
    setItems((cur) => [...cur, res.data])
  }

  return (
    <div className="card">
      <h2>Publications ({items.length})</h2>
      <DatasetSearch kind="publication" onImport={importPublication} />
      {items.map((p) => (
        <div key={p.id} className="entry">
          <div>
            <strong>{p.title}</strong>
            <div className="muted">
              {p.authors?.join(', ')} {p.venue && `· ${p.venue}`} {p.year && `· ${p.year}`}
              {p.citation_count ? ` · ${p.citation_count} citations` : ''}
            </div>
          </div>
          <button type="button" className="mini-del" onClick={() => remove(p.id)}>Delete</button>
        </div>
      ))}

      <form className="subform" onSubmit={add}>
        {error && <div className="error">{error}</div>}
        <input placeholder="Title *" required value={form.title}
               onChange={(e) => setForm({ ...form, title: e.target.value })} />
        <input placeholder="Authors (comma-separated)" value={form.authors.join(', ')}
               onChange={(e) => setForm({ ...form, authors: e.target.value.split(',').map((s) => s.trim()).filter(Boolean) })} />
        <div className="grid-2">
          <input placeholder="Venue / Journal" value={form.venue}
                 onChange={(e) => setForm({ ...form, venue: e.target.value })} />
          <input placeholder="Year" type="number" value={form.year}
                 onChange={(e) => setForm({ ...form, year: e.target.value })} />
          <input placeholder="DOI" value={form.doi}
                 onChange={(e) => setForm({ ...form, doi: e.target.value })} />
          <input placeholder="Citations" type="number" value={form.citation_count}
                 onChange={(e) => setForm({ ...form, citation_count: e.target.value })} />
        </div>
        <button type="submit">+ Add Publication</button>
      </form>
    </div>
  )
}

function PatentsSection({ items, setItems }) {
  const blank = { title: '', assignee: '', patent_number: '', filing_date: '',
                  classification: '', technology_domain: '', citation_count: 0, url: '', abstract: '' }
  const [form, setForm] = useState(blank)
  const [error, setError] = useState('')

  const add = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const payload = { ...form, filing_date: form.filing_date || null,
                        citation_count: Number(form.citation_count) || 0 }
      const res = await profileService.addPatent(payload)
      setItems([...items, res.data])
      setForm(blank)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add patent')
    }
  }

  const remove = async (id) => {
    await profileService.deletePatent(id)
    setItems(items.filter((p) => p.id !== id))
  }

  const importPatent = async (rec) => {
    const res = await profileService.addPatent(rec)
    setItems((cur) => [...cur, res.data])
  }

  return (
    <div className="card">
      <h2>Patents ({items.length})</h2>
      <DatasetSearch kind="patent" onImport={importPatent} />
      {items.map((p) => (
        <div key={p.id} className="entry">
          <div>
            <strong>{p.title}</strong>
            <div className="muted">
              {p.assignee} {p.technology_domain && `· ${p.technology_domain}`}
              {p.filing_date && ` · filed ${p.filing_date}`}
            </div>
          </div>
          <button type="button" className="mini-del" onClick={() => remove(p.id)}>Delete</button>
        </div>
      ))}

      <form className="subform" onSubmit={add}>
        {error && <div className="error">{error}</div>}
        <input placeholder="Title *" required value={form.title}
               onChange={(e) => setForm({ ...form, title: e.target.value })} />
        <div className="grid-2">
          <input placeholder="Assignee" value={form.assignee}
                 onChange={(e) => setForm({ ...form, assignee: e.target.value })} />
          <input placeholder="Patent Number" value={form.patent_number}
                 onChange={(e) => setForm({ ...form, patent_number: e.target.value })} />
          <input placeholder="Technology Domain" value={form.technology_domain}
                 onChange={(e) => setForm({ ...form, technology_domain: e.target.value })} />
          <input placeholder="Filing Date" type="date" value={form.filing_date}
                 onChange={(e) => setForm({ ...form, filing_date: e.target.value })} />
        </div>
        <button type="submit">+ Add Patent</button>
      </form>
    </div>
  )
}
