import TagRow from './TagRow'

export default function ProfileDetail({ p }) {
  return (
    <div style={{ marginTop: 12 }}>
      {p.headline && <p><strong>{p.headline}</strong></p>}
      {p.bio && <p className="muted" style={{ marginTop: 6 }}>{p.bio}</p>}
      {p.organization && <p className="muted">Org: {p.organization} {p.country && `· ${p.country}`}</p>}

      <TagRow label="Research Domains" items={p.research_domains} />
      <TagRow label="Keywords" items={p.keywords} />
      <TagRow label="Technology Areas" items={p.technology_areas} />

      <h3 style={{ marginTop: 20 }}>Publications ({p.publications?.length || 0})</h3>
      {p.publications && p.publications.length > 0 ? (
        p.publications.map((pub) => (
          <div key={pub.id} className="entry" style={{ display: 'block' }}>
            <strong>{pub.title}</strong>
            <div className="muted" style={{ fontSize: 12, marginTop: 4 }}>
              {pub.authors?.join(', ')} {pub.venue && `· ${pub.venue}`} {pub.year && `· ${pub.year}`}
            </div>
          </div>
        ))
      ) : (
        <p className="muted" style={{ fontSize: 13 }}>No publications listed.</p>
      )}

      <h3 style={{ marginTop: 20 }}>Patents ({p.patents?.length || 0})</h3>
      {p.patents && p.patents.length > 0 ? (
        p.patents.map((pat) => (
          <div key={pat.id} className="entry" style={{ display: 'block' }}>
            <strong>{pat.title}</strong>
            <div className="muted" style={{ fontSize: 12, marginTop: 4 }}>
              {pat.assignee} {pat.patent_number && `· ${pat.patent_number}`} {pat.technology_domain && `· ${pat.technology_domain}`}
            </div>
          </div>
        ))
      ) : (
        <p className="muted" style={{ fontSize: 13 }}>No patents listed.</p>
      )}
    </div>
  )
}
