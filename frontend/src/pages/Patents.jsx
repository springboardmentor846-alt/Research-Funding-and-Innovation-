import { useEffect, useState } from "react";
import api from "../api/axios";

const emptyForm = {
  title: "",
  patent_number: "",
  inventors: "",
  patent_office: "",
  filing_date: "",
  grant_date: "",
  status: "",
  url: "",
  description: "",
};

function Patents() {
  const [patents, setPatents] = useState([]);
  const [formData, setFormData] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const fetchPatents = async () => {
    try {
      const response = await api.get(
        "/research-profiles/me/patents"
      );

      setPatents(response.data.patents || []);
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Failed to load patents."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatents();
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
          `/research-profiles/me/patents/${editingId}`,
          payload
        );

        setMessage("Patent updated successfully.");
      } else {
        await api.post(
          "/research-profiles/me/patents",
          payload
        );

        setMessage("Patent created successfully.");
      }

      setFormData(emptyForm);
      setEditingId(null);

      await fetchPatents();
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Failed to save patent."
      );
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (patent) => {
    setEditingId(patent.id);

    setFormData({
      title: patent.title || "",
      patent_number: patent.patent_number || "",
      inventors: patent.inventors || "",
      patent_office: patent.patent_office || "",
      filing_date: patent.filing_date || "",
      grant_date: patent.grant_date || "",
      status: patent.status || "",
      url: patent.url || "",
      description: patent.description || "",
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

  const handleDelete = async (patentId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this patent?"
    );

    if (!confirmed) return;

    try {
      setMessage("");

      await api.delete(
        `/research-profiles/me/patents/${patentId}`
      );

      setMessage("Patent deleted successfully.");

      await fetchPatents();
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Failed to delete patent."
      );
    }
  };

  return (
    <div className="module-page">
      <div className="module-page-header">
        <div>
          <span className="module-eyebrow">
            INTELLECTUAL PROPERTY
          </span>

          <h1>Patents</h1>

          <p>
            Maintain patent applications, granted inventions,
            and intellectual property records.
          </p>
        </div>

        <div className="module-count-badge">
          <strong>{patents.length}</strong>
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
                ? "Update Patent"
                : "Add Patent"}
            </h2>

            <p>
              Record invention and intellectual property
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
                Patent Title
                <span className="required-mark">*</span>
              </label>

              <input
                type="text"
                name="title"
                placeholder="Enter the complete invention or patent title"
                value={formData.title}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-section">
            <div className="form-section-title">
              Patent Details
            </div>

            <div className="professional-form-grid">
              <div className="professional-field">
                <label>
                  Patent Number
                  <span className="optional-label">
                    Optional
                  </span>
                </label>

                <input
                  type="text"
                  name="patent_number"
                  placeholder="Enter only if officially available"
                  value={formData.patent_number}
                  onChange={handleChange}
                />
              </div>

              <div className="professional-field">
                <label>Patent Office</label>

                <input
                  type="text"
                  name="patent_office"
                  placeholder="Example: Indian Patent Office"
                  value={formData.patent_office}
                  onChange={handleChange}
                />
              </div>

              <div className="professional-field">
                <label>Inventors</label>

                <input
                  type="text"
                  name="inventors"
                  placeholder="Inventor One, Inventor Two"
                  value={formData.inventors}
                  onChange={handleChange}
                />
              </div>

              <div className="professional-field">
                <label>Status</label>

                <select
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                >
                  <option value="">
                    Select patent status
                  </option>

                  <option value="Filed">
                    Filed
                  </option>

                  <option value="Pending">
                    Pending
                  </option>

                  <option value="Published">
                    Published
                  </option>

                  <option value="Granted">
                    Granted
                  </option>

                  <option value="Rejected">
                    Rejected
                  </option>
                </select>
              </div>
            </div>
          </div>

          <div className="form-section">
            <div className="form-section-title">
              Timeline & Reference
            </div>

            <div className="professional-form-grid">
              <div className="professional-field">
                <label>Filing Date</label>

                <input
                  type="date"
                  name="filing_date"
                  value={formData.filing_date}
                  onChange={handleChange}
                />
              </div>

              <div className="professional-field">
                <label>Grant Date</label>

                <input
                  type="date"
                  name="grant_date"
                  value={formData.grant_date}
                  onChange={handleChange}
                />
              </div>

              <div className="professional-field full-width-field">
                <label>
                  Patent URL
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
              <label>Description</label>

              <textarea
                name="description"
                rows="6"
                placeholder="Describe the invention, technical contribution, or innovation..."
                value={formData.description}
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
                  ? "Update Patent"
                  : "Add Patent"}
            </button>
          </div>
        </form>
      </div>

      <div className="records-card publication-records-card">
        <div className="records-card-header">
          <div>
            <h2>My Patents</h2>

            <p>
              Review and manage intellectual property records
              connected to your research profile.
            </p>
          </div>

          <span className="records-total">
            {patents.length} total
          </span>
        </div>

        {loading ? (
          <div className="records-empty">
            Loading patents...
          </div>
        ) : patents.length === 0 ? (
          <div className="records-empty">
            <div className="empty-state-icon">
              +
            </div>

            <h3>No patents yet</h3>

            <p>
              Add your first patent or invention record above.
            </p>
          </div>
        ) : (
          <div className="research-record-grid">
            {patents.map((patent) => (
              <article
                key={patent.id}
                className="research-record-card"
              >
                <div className="research-record-top">
                  <span className="research-type-badge">
                    {patent.status || "Patent"}
                  </span>

                  {patent.filing_date && (
                    <span className="research-record-date">
                      Filed {patent.filing_date}
                    </span>
                  )}
                </div>

                <h3>{patent.title}</h3>

                {patent.inventors && (
                  <p className="research-authors">
                    {patent.inventors}
                  </p>
                )}

                <div className="research-metadata">
                  {patent.patent_number && (
                    <div>
                      <span>Patent Number</span>
                      <strong>
                        {patent.patent_number}
                      </strong>
                    </div>
                  )}

                  {patent.patent_office && (
                    <div>
                      <span>Patent Office</span>
                      <strong>
                        {patent.patent_office}
                      </strong>
                    </div>
                  )}

                  {patent.grant_date && (
                    <div>
                      <span>Grant Date</span>
                      <strong>
                        {patent.grant_date}
                      </strong>
                    </div>
                  )}
                </div>

                <div className="research-record-actions">
                  <button
                    type="button"
                    className="record-edit-btn"
                    onClick={() => handleEdit(patent)}
                  >
                    Edit
                  </button>

                  <button
                    type="button"
                    className="record-delete-btn"
                    onClick={() =>
                      handleDelete(patent.id)
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

export default Patents;