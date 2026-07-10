import { useEffect, useState } from "react";
import api from "../api/axios";

const emptyForm = {
  department: "",
  organization_type: "",
  city: "",
  state: "",
  country: "",
  website: "",
  description: "",
};

function OrganizationInformation() {
  const [exists, setExists] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [formData, setFormData] = useState(emptyForm);

  useEffect(() => {
    const fetchOrganization = async () => {
      try {
        const response = await api.get(
          "/research-profiles/me/organization"
        );

        setFormData({
          department: response.data.department || "",
          organization_type:
            response.data.organization_type || "",
          city: response.data.city || "",
          state: response.data.state || "",
          country: response.data.country || "",
          website: response.data.website || "",
          description: response.data.description || "",
        });

        setExists(true);
      } catch (error) {
        if (error.response?.status !== 404) {
          setMessage(
            error.response?.data?.detail ||
              "Failed to load organization information."
          );
        }
      } finally {
        setLoading(false);
      }
    };

    fetchOrganization();
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

      if (exists) {
        await api.patch(
          "/research-profiles/me/organization",
          payload
        );

        setMessage(
          "Organization information updated successfully."
        );
      } else {
        await api.post(
          "/research-profiles/me/organization",
          payload
        );

        setExists(true);

        setMessage(
          "Organization information created successfully."
        );
      }
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Failed to save organization information."
      );
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="module-loading">
        <div className="spinner-border text-primary" />
        <span>Loading organization information...</span>
      </div>
    );
  }

  return (
    <div className="module-page">
      <div className="module-page-header">
        <div>
          <span className="module-eyebrow">
            INSTITUTIONAL PROFILE
          </span>

          <h1>Organization Information</h1>

          <p>
            Maintain the institutional context associated
            with your research activities.
          </p>
        </div>

        <div
          className={`record-status ${
            exists ? "complete" : "incomplete"
          }`}
        >
          <span className="record-status-dot"></span>

          {exists
            ? "Organization Added"
            : "Not Yet Added"}
        </div>
      </div>

      {message && (
        <div className="module-alert">
          {message}
        </div>
      )}

      <div className="module-content-grid">
        <div className="professional-form-card">
          <div className="form-card-header">
            <div>
              <h2>Institutional Details</h2>

              <p>
                Provide your department, organization type,
                location, and institutional information.
              </p>
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="form-section">
              <div className="form-section-title">
                Organization Structure
              </div>

              <div className="professional-form-grid">
                <div className="professional-field">
                  <label>Department</label>

                  <input
                    type="text"
                    name="department"
                    placeholder="Example: Computer Science and Engineering"
                    value={formData.department}
                    onChange={handleChange}
                  />
                </div>

                <div className="professional-field">
                  <label>Organization Type</label>

                  <select
                    name="organization_type"
                    value={formData.organization_type}
                    onChange={handleChange}
                  >
                    <option value="">
                      Select organization type
                    </option>

                    <option value="University">
                      University
                    </option>

                    <option value="Research Institute">
                      Research Institute
                    </option>

                    <option value="Startup">
                      Startup
                    </option>

                    <option value="Company">
                      Company
                    </option>

                    <option value="Government Organization">
                      Government Organization
                    </option>

                    <option value="Nonprofit">
                      Nonprofit
                    </option>

                    <option value="Other">
                      Other
                    </option>
                  </select>
                </div>
              </div>
            </div>

            <div className="form-section">
              <div className="form-section-title">
                Location
              </div>

              <div className="professional-form-grid">
                <div className="professional-field">
                  <label>City</label>

                  <input
                    type="text"
                    name="city"
                    placeholder="Example: Hubballi"
                    value={formData.city}
                    onChange={handleChange}
                  />
                </div>

                <div className="professional-field">
                  <label>State</label>

                  <input
                    type="text"
                    name="state"
                    placeholder="Example: Karnataka"
                    value={formData.state}
                    onChange={handleChange}
                  />
                </div>

                <div className="professional-field">
                  <label>Country</label>

                  <input
                    type="text"
                    name="country"
                    placeholder="Example: India"
                    value={formData.country}
                    onChange={handleChange}
                  />
                </div>

                <div className="professional-field">
                  <label>
                    Website
                    <span className="optional-label">
                      Optional
                    </span>
                  </label>

                  <input
                    type="url"
                    name="website"
                    placeholder="https://organization.example"
                    value={formData.website}
                    onChange={handleChange}
                  />
                </div>
              </div>
            </div>

            <div className="form-section">
              <div className="professional-field">
                <label>Organization Description</label>

                <textarea
                  name="description"
                  rows="5"
                  placeholder="Describe the institution's research focus, capabilities, or innovation activities..."
                  value={formData.description}
                  onChange={handleChange}
                />

                <span className="field-help">
                  Add information relevant to research and
                  innovation activities.
                </span>
              </div>
            </div>

            <div className="professional-form-actions">
              <button
                type="submit"
                className="primary-action-btn"
                disabled={saving}
              >
                {saving
                  ? "Saving..."
                  : exists
                    ? "Save Changes"
                    : "Create Organization"}
              </button>
            </div>
          </form>
        </div>

        <aside className="profile-guidance-card">
          <div className="guidance-icon">
            i
          </div>

          <h3>Institutional Context</h3>

          <p>
            Organization information provides context for
            future funding eligibility and collaboration
            workflows.
          </p>

          <div className="guidance-list">
            <div>
              <span>01</span>
              Funding eligibility context
            </div>

            <div>
              <span>02</span>
              Institutional classification
            </div>

            <div>
              <span>03</span>
              Collaboration discovery
            </div>

            <div>
              <span>04</span>
              Innovation ecosystem mapping
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}

export default OrganizationInformation;