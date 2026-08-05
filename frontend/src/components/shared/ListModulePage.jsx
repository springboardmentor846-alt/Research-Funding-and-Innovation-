function ListModulePage({
  eyebrow,
  title,
  description,
  inputLabel,
  placeholder,
  value,
  onChange,
  onSubmit,
  items,
  loading,
  message,
  emptyMessage,
  successHint,
  onDelete,
}) {
  return (
    <div className="module-page">
      <div className="module-page-header">
        <div>
          <span className="module-eyebrow">
            {eyebrow}
          </span>

          <h1>{title}</h1>

          <p>{description}</p>
        </div>

        <div className="module-count-badge">
          <strong>{items.length}</strong>
          <span>Records</span>
        </div>
      </div>

      {message && (
        <div className="module-alert">
          {message}
        </div>
      )}

      <div className="list-module-grid">
        <div className="professional-form-card">
          <div className="form-card-header">
            <div>
              <h2>Add New Entry</h2>

              <p>
                Add information to your structured
                researcher profile.
              </p>
            </div>
          </div>

          <form onSubmit={onSubmit}>
            <div className="form-section">
              <div className="professional-field">
                <label>{inputLabel}</label>

                <div className="inline-add-form">
                  <input
                    type="text"
                    value={value}
                    placeholder={placeholder}
                    onChange={(event) =>
                      onChange(event.target.value)
                    }
                    required
                  />

                  <button
                    type="submit"
                    className="primary-action-btn"
                  >
                    Add Entry
                  </button>
                </div>

                {successHint && (
                  <span className="field-help">
                    {successHint}
                  </span>
                )}
              </div>
            </div>
          </form>
        </div>

        <aside className="profile-guidance-card">
          <div className="guidance-icon">
            i
          </div>

          <h3>Profile Intelligence</h3>

          <p>
            Structured research information can support
            future matching, discovery and recommendation
            workflows.
          </p>

          <div className="guidance-list">
            <div>
              <span>01</span>
              Better profile classification
            </div>

            <div>
              <span>02</span>
              Improved opportunity matching
            </div>

            <div>
              <span>03</span>
              Stronger research discovery
            </div>
          </div>
        </aside>
      </div>

      <div className="records-card">
        <div className="records-card-header">
          <div>
            <h2>{title}</h2>

            <p>
              Review the entries currently associated
              with your profile.
            </p>
          </div>

          <span className="records-total">
            {items.length} total
          </span>
        </div>

        {loading ? (
          <div className="records-empty">
            Loading records...
          </div>
        ) : items.length === 0 ? (
          <div className="records-empty">
            <div className="empty-state-icon">
              +
            </div>

            <h3>No records yet</h3>

            <p>{emptyMessage}</p>
          </div>
        ) : (
          <div className="records-list">
            {items.map((item, index) => (
              <div
                key={item.id}
                className="record-row"
              >
                <div className="record-index">
                  {String(index + 1).padStart(2, "0")}
                </div>

                <div className="record-main">
                  <strong>{item.name}</strong>

                  <span>
                    Research profile entry
                  </span>
                </div>

                {onDelete && (
                  <button
                    type="button"
                    className="record-delete-btn"
                    onClick={() => onDelete(item.id)}
                  >
                    Delete
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default ListModulePage;