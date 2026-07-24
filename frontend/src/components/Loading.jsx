export default function Loading({ message = 'Loading…' }) {
  return (
    <div className="loading-wrap">
      <div className="spinner" />
      <span>{message}</span>
    </div>
  )
}
