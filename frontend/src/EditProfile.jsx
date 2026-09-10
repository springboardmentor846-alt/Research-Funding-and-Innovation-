import { useState, useEffect } from "react";
import axios from "axios";

function EditProfile({ token, profile, onUpdated }) {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({
    research_domains: "",
    keywords: "",
    technology_areas: "",
    organization_name: "",
  });
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (profile) {
      setFormData({
        research_domains: profile.research_domains || "",
        keywords: profile.keywords || "",
        technology_areas: profile.technology_areas || "",
        organization_name: profile.organization_name || "",
      });
    }
  }, [profile]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    try {
      await axios.post(
        "https://research-platform-backend-e0sf.onrender.com/api/v1/profile/",
        { ...formData, publications: "", patents: "" },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage("Profile updated successfully!");
      onUpdated();
      setTimeout(() => setIsOpen(false), 1000);
    } catch (err) {
      setMessage("Could not update profile.");
    }
  };

  if (!isOpen) {
    return (
      <button className="edit-profile-btn" onClick={() => setIsOpen(true)}>
        Edit Profile
      </button>
    );
  }

  return (
    <form className="edit-profile-form" onSubmit={handleSubmit}>
      <div className="field">
        <label>Research Domains (comma separated)</label>
        <input
          type="text"
          name="research_domains"
          value={formData.research_domains}
          onChange={handleChange}
          placeholder="e.g. Artificial Intelligence, Healthcare Technology"
        />
      </div>
      <div className="field">
        <label>Keywords</label>
        <input
          type="text"
          name="keywords"
          value={formData.keywords}
          onChange={handleChange}
          placeholder="e.g. AI, machine learning, blockchain"
        />
      </div>
      <div className="field">
        <label>Technology Areas</label>
        <input
          type="text"
          name="technology_areas"
          value={formData.technology_areas}
          onChange={handleChange}
          placeholder="e.g. AI, IoT, Blockchain"
        />
      </div>
      <div className="field">
        <label>Organization Name</label>
        <input
          type="text"
          name="organization_name"
          value={formData.organization_name}
          onChange={handleChange}
          placeholder="e.g. Demo Research Lab"
        />
      </div>
      <div className="edit-profile-actions">
        <button type="submit" className="auth-submit" style={{ width: "auto", padding: "10px 20px" }}>
          Save Changes
        </button>
        <button type="button" className="edit-profile-cancel" onClick={() => setIsOpen(false)}>
          Cancel
        </button>
      </div>
      {message && <p className="dash-empty">{message}</p>}
    </form>
  );
}

export default EditProfile;

