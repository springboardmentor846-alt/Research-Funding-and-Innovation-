export default function TagRow({ label, items }) {
  if (!items || items.length === 0) return null
  return (
    <div style={{ marginTop: 10 }}>
      <strong style={{ fontSize: 13 }}>{label}:</strong>{' '}
      {items.map((t) => <span key={t} className="tag" style={{ marginRight: 4 }}>{t}</span>)}
    </div>
  )
}
