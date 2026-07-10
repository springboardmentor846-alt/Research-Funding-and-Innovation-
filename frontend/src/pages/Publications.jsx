import { useEffect, useState } from "react";
import api from "../api/axios";

const emptyForm = {
  title: "",
  publication_type: "",
  authors: "",
  journal_or_conference: "",
  publisher: "",
  publication_date: "",
  doi: "",
  url: "",
  abstract: "",
};

function Publications() {
  const [publications, setPublications] = useState([]);
  const [formData, setFormData] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const fetchPublications = async () => {
    try {
      const response = await api.get(
        "/research-profiles/me/publications"
      );

      setPublications(response.data.publications || []);
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Failed to load publications."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPublications();
  }, []);

  const handleChange = (event) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value,
    });
  };

  const preparePayload = () => {
    const payload = {};

    Object.entries(formData).forEach(([key, value]) => {
      payload[key] = value === "" ? null : value;
    });

    return payload;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      setSaving(true);
      setMessage("");

      const payload = preparePayload();

      if (editingId) {
        await api.patch(
          `/research-profiles/me/publications/${editingId}`,
          payload
        );

        setMessage("Publication updated successfully.");
      } else {
        await api.post(
          "/research-profiles/me/publications",
          payload
        );

        setMessage("Publication created successfully.");
      }

      setFormData(emptyForm);
      setEditingId(null);

      await fetchPublications();
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Failed to save publication."
      );
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (publication) => {
    setEditingId(publication.id);

    setFormData({
      title: publication.title || "",
      publication_type:
        publication.publication_type || "",
      authors: publication.authors || "",
      journal_or_conference:
        publication.journal_or_conference || "",
      publisher: publication.publisher || "",
      publication_date:
        publication.publication_date || "",
      doi: publication.doi || "",
      url: publication.url || "",
      abstract: publication.abstract || "",
    });

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setFormData(emptyForm);
    setMessage("");
  };

  const handleDelete = async (publicationId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this publication?"
    );

    if (!confirmed) return;

    try {
      setMessage("");

      await api.delete(
        `/research-profiles/me/publications/${publicationId}`
      );

      setMessage("Publication deleted successfully.");

      await fetchPublications();
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Failed to delete publication."
      );
    }
  };

  return (
    <div className="module-page">
      <div className="module-page-header">
        <div>
          <span className="module-eyebrow">
            RESEARCH OUTPUTS
          </span>

          <h1>Publications</h1>

          <p>
            Maintain journal articles, conference papers,
            and other scholarly research outputs.
          </p>
        </div>

        <div className="module-count-badge">
          <strong>{publications.length}</strong>
          <span>Records</span>
        </div>
      </div>

      {message && (
        <div className="module-alert">
          {message}
        </div>
      )}

      <div className="professional-form-card publication-form-card">
        <div className="form-card-header">
          <div>
            <h2>
              {editingId
                ? "Update Publication"
                : "Add Publication"}
            </h2>

            <p>
              Record bibliographic and research output
              information associated with your profile.
            </p>
          </div>

          {editingId && (
            <span className="editing-badge">
              Editing Record
            </span>
          )}
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-section">
            <div className="professional-field">
              <label>
                Publication Title
                <span className="required-mark">*</span>
              </label>

              <input
                type="text"
                name="title"
                placeholder="Enter the complete publication title"
                value={formData.title}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-section">
            <div className="form-section-title">
              Publication Details
            </div>

            <div className="professional-form-grid">
              <div className="professional-field">
                <label>Publication Type</label>

                <select
                  name="publication_type"
                  value={formData.publication_type}
                  onChange={handleChange}
                >
                  <option value="">
                    Select publication type
                  </option>
                  <option value="Journal Article">
                    Journal Article
                  </option>
                  <option value="Conference Paper">
                    Conference Paper
                  </option>
                  <option value="Book Chapter">
                    Book Chapter
                  </option>
                  <option value="Preprint">
                    Preprint
                  </option>
                  <option value="Other">
                    Other
                  </option>
                </select>
              </div>

              <div className="professional-field">
                <label>Publication Date</label>

                <input
                  type="date"
                  name="publication_date"
                  value={formData.publication_date}
                  onChange={handleChange}
                />
              </div>

              <div className="professional-field">
                <label>Authors</label>

                <input
                  type="text"
                  name="authors"
                  placeholder="Author One, Author Two"
                  value={formData.authors}
                  onChange={handleChange}
                />
              </div>

              <div className="professional-field">
                <label>Publisher</label>

                <input
                  type="text"
                  name="publisher"
                  placeholder="Publisher name"
                  value={formData.publisher}
                  onChange={handleChange}
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <div className="form-section-title">
              Publication Source
            </div>

            <div className="professional-form-grid">
              <div className="professional-field">
                <label>Journal or Conference</label>

                <input
                  type="text"
                  name="journal_or_conference"
                  placeholder="Journal or conference name"
                  value={formData.journal_or_conference}
                  onChange={handleChange}
                />
              </div>

              <div className="professional-field">
                <label>
                  DOI
                  <span className="optional-label">
                    Optional
                  </span>
                </label>

                <input
                  type="text"
                  name="doi"
                  placeholder="Enter only if available"
                  value={formData.doi}
                  onChange={handleChange}
                />
              </div>

              <div className="professional-field full-width-field">
                <label>
                  Publication URL
                  <span className="optional-label">
                    Optional
                  </span>
                </label>

                <input
                  type="url"
                  name="url"
                  placeholder="https://..."
                  value={formData.url}
                  onChange={handleChange}
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <div className="professional-field">
              <label>Abstract</label>

              <textarea
                name="abstract"
                rows="6"
                placeholder="Provide a concise abstract or summary of the research output..."
                value={formData.abstract}
                onChange={handleChange}
              />

              <span className="field-help">
                Maximum 5000 characters.
              </span>
            </div>
          </div>

          <div className="professional-form-actions">
            {editingId && (
              <button
                type="button"
                className="secondary-action-btn"
                onClick={handleCancelEdit}
              >
                Cancel Editing
              </button>
            )}

            <button
              type="submit"
              className="primary-action-btn"
              disabled={saving}
            >
              {saving
                ? "Saving..."
                : editingId
                  ? "Update Publication"
                  : "Add Publication"}
            </button>
          </div>
        </form>
      </div>

      <div className="records-card publication-records-card">
        <div className="records-card-header">
          <div>
            <h2>My Publications</h2>

            <p>
              Review and manage scholarly outputs connected
              to your research profile.
            </p>
          </div>

          <span className="records-total">
            {publications.length} total
          </span>
        </div>

        {loading ? (
          <div className="records-empty">
            Loading publications...
          </div>
        ) : publications.length === 0 ? (
          <div className="records-empty">
            <div className="empty-state-icon">
              +
            </div>

            <h3>No publications yet</h3>

            <p>
              Add your first scholarly research output above.
            </p>
          </div>
        ) : (
          <div className="research-record-grid">
            {publications.map((publication) => (
              <article
                key={publication.id}
                className="research-record-card"
              >
                <div className="research-record-top">
                  <span className="research-type-badge">
                    {publication.publication_type ||
                      "Publication"}
                  </span>

                  {publication.publication_date && (
                    <span className="research-record-date">
                      {publication.publication_date}
                    </span>
                  )}
                </div>

                <h3>{publication.title}</h3>

                {publication.authors && (
                  <p className="research-authors">
                    {publication.authors}
                  </p>
                )}

                <div className="research-metadata">
                  {publication.journal_or_conference && (
                    <div>
                      <span>Source</span>
                      <strong>
                        {
                          publication.journal_or_conference
                        }
                      </strong>
                    </div>
                  )}

                  {publication.publisher && (
                    <div>
                      <span>Publisher</span>
                      <strong>
                        {publication.publisher}
                      </strong>
                    </div>
                  )}

                  {publication.doi && (
                    <div>
                      <span>DOI</span>
                      <strong>{publication.doi}</strong>
                    </div>
                  )}
                </div>

                <div className="research-record-actions">
                  <button
                    type="button"
                    className="record-edit-btn"
                    onClick={() =>
                      handleEdit(publication)
                    }
                  >
                    Edit
                  </button>

                  <button
                    type="button"
                    className="record-delete-btn"
                    onClick={() =>
                      handleDelete(publication.id)
                    }
                  >
                    Delete
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Publications;