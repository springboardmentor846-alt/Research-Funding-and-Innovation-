import { useEffect, useState } from "react";
import api from "../api/axios";

function ResearchProfile() {
  const [profile, setProfile] = useState(null);

  const [formData, setFormData] = useState({
    bio: "",
    highest_qualification: "",
    current_position: "",
    organization_name: "",
    orcid_id: "",
  });

  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await api.get(
          "/research-profiles/me"
        );

        setProfile(response.data);

        setFormData({
          bio: response.data.bio || "",
          highest_qualification:
            response.data.highest_qualification || "",
          current_position:
            response.data.current_position || "",
          organization_name:
            response.data.organization_name || "",
          orcid_id:
            response.data.orcid_id || "",
        });
      } catch (error) {
        if (error.response?.status !== 404) {
          setMessage(
            error.response?.data?.detail ||
              "Failed to load research profile."
          );
        }
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
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

      if (profile) {
        const response = await api.patch(
          "/research-profiles/me",
          payload
        );

        setProfile(response.data);

        setMessage(
          "Research profile updated successfully."
        );
      } else {
        const response = await api.post(
          "/research-profiles",
          payload
        );

        setProfile(response.data);

        setMessage(
          "Research profile created successfully."
        );
      }
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Failed to save research profile."
      );
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="module-loading">
        <div className="spinner-border text-primary" />
        <span>Loading research profile...</span>
      </div>
    );
  }

  return (
    <div className="module-page">
      <div className="module-page-header">
        <div>
          <span className="module-eyebrow">
            PROFILE MANAGEMENT
          </span>

          <h1>Research Profile</h1>

          <p>
            Maintain your academic identity and professional
            research information.
          </p>
        </div>

        <div
          className={`record-status ${
            profile ? "complete" : "incomplete"
          }`}
        >
          <span className="record-status-dot"></span>

          {profile
            ? "Profile Created"
            : "Profile Not Created"}
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
              <h2>Academic Information</h2>

              <p>
                Provide information used to build your
                structured researcher identity.
              </p>
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="form-section">
              <div className="professional-field">
                <label>Professional Bio</label>

                <textarea
                  name="bio"
                  rows="5"
                  placeholder="Describe your research background, interests and current work..."
                  value={formData.bio}
                  onChange={handleChange}
                />

                <span className="field-help">
                  Maximum 2000 characters.
                </span>
              </div>
            </div>

            <div className="form-section">
              <div className="form-section-title">
                Academic & Professional Details
              </div>

              <div className="professional-form-grid">
                <div className="professional-field">
                  <label>Highest Qualification</label>

                  <input
                    type="text"
                    name="highest_qualification"
                    placeholder="Example: Ph.D. Computer Science"
                    value={formData.highest_qualification}
                    onChange={handleChange}
                  />
                </div>

                <div className="professional-field">
                  <label>Current Position</label>

                  <input
                    type="text"
                    name="current_position"
                    placeholder="Example: Research Associate"
                    value={formData.current_position}
                    onChange={handleChange}
                  />
                </div>

                <div className="professional-field">
                  <label>Organization Name</label>

                  <input
                    type="text"
                    name="organization_name"
                    placeholder="University or institution"
                    value={formData.organization_name}
                    onChange={handleChange}
                  />
                </div>

                <div className="professional-field">
                  <label>
                    ORCID ID
                    <span className="optional-label">
                      Optional
                    </span>
                  </label>

                  <input
                    type="text"
                    name="orcid_id"
                    placeholder="0000-0000-0000-0000"
                    value={formData.orcid_id}
                    onChange={handleChange}
                  />

                  <span className="field-help">
                    Enter only if you have a registered ORCID.
                  </span>
                </div>
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
                  : profile
                    ? "Save Changes"
                    : "Create Profile"}
              </button>
            </div>
          </form>
        </div>

        <aside className="profile-guidance-card">
          <div className="guidance-icon">
            i
          </div>

          <h3>Why complete your profile?</h3>

          <p>
            Structured profile information will support future
            funding discovery and innovation intelligence
            workflows.
          </p>

          <div className="guidance-list">
            <div>
              <span>01</span>
              Research opportunity matching
            </div>

            <div>
              <span>02</span>
              Publication intelligence
            </div>

            <div>
              <span>03</span>
              Patent relevance analysis
            </div>

            <div>
              <span>04</span>
              Funding recommendation workflows
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}

export default ResearchProfile;