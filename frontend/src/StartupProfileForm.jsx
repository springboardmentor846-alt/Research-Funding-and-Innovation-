import { useEffect, useState } from "react";
import axios from "axios";

const API_BASE = "https://research-platform-backend-e0sf.onrender.com/api/v1/startup";

const emptyForm = {
  startup_name: "",
  tagline: "",
  industry: "",
  stage: "Idea",
  founded_year: "",
  funding_stage: "Bootstrapped",
  startup_email: "",
  phone_number: "",
  website: "",
  linkedin_url: "",
  location: "",
  description: "",
  problem_statement: "",
  solution: "",
  technology_stack: "",
  research_interests: "",
  funding_needed: "",
  team_size: 1,
  pitch_deck_url: "",
  logo_url: "",
};

function StartupProfileForm({ token }) {
  const [form, setForm] = useState(emptyForm);
  const [profileExists, setProfileExists] = useState(false);
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  const authHeaders = { headers: { Authorization: `Bearer ${token}` } };

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const res = await axios.get(`${API_BASE}/profile`, authHeaders);
        setForm({ ...emptyForm, ...res.data });
        setProfileExists(true);
      } catch (err) {
        setProfileExists(false);
      }
      setLoading(false);
    };
    loadProfile();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const handleChange = (field) => (e) => {
    setForm({ ...form, [field]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage("");

    const payload = {
      ...form,
      founded_year: form.founded_year ? parseInt(form.founded_year, 10) : null,
      team_size: form.team_size ? parseInt(form.team_size, 10) : 1,
    };

    try {
      if (profileExists) {
        await axios.put(`${API_BASE}/profile`, payload, authHeaders);
        setMessage("Startup profile updated.");
      } else {
        await axios.post(`${API_BASE}/profile`, payload, authHeaders);
        setMessage("Startup profile created.");
        setProfileExists(true);
      }
    } catch (err) {
      setMessage(err.response?.data?.detail || "Could not save startup profile.");
    }
    setSaving(false);
  };

  if (loading) return <p className="dash-empty">Loading...</p>;

  const inputStyle = {
    width: "100%",
    padding: "10px 12px",
    marginBottom: "14px",
    border: "1px solid #d0d7de",
    borderRadius: "6px",
    fontSize: "14px",
  };
  const labelStyle = { fontSize: "13px", fontWeight: 600, marginBottom: "4px", display: "block" };

  return (
    <form onSubmit={handleSubmit}>
      <label style={labelStyle}>Startup Name *</label>
      <input style={inputStyle} type="text" value={form.startup_name} onChange={handleChange("startup_name")} required />

      <label style={labelStyle}>Tagline</label>
      <input style={inputStyle} type="text" value={form.tagline} onChange={handleChange("tagline")} placeholder="One-line pitch" />

      <div style={{ display: "flex", gap: "12px" }}>
        <div style={{ flex: 1 }}>
          <label style={labelStyle}>Industry</label>
          <input style={inputStyle} type="text" value={form.industry} onChange={handleChange("industry")} placeholder="e.g. Clean Energy" />
        </div>
        <div style={{ flex: 1 }}>
          <label style={labelStyle}>Stage</label>
          <select style={inputStyle} value={form.stage} onChange={handleChange("stage")}>
            <option>Idea</option>
            <option>Prototype</option>
            <option>Seed</option>
            <option>Series A</option>
            <option>Series B+</option>
            <option>Growth</option>
          </select>
        </div>
      </div>

      <div style={{ display: "flex", gap: "12px" }}>
        <div style={{ flex: 1 }}>
          <label style={labelStyle}>Founded Year</label>
          <input style={inputStyle} type="number" value={form.founded_year} onChange={handleChange("founded_year")} />
        </div>
        <div style={{ flex: 1 }}>
          <label style={labelStyle}>Funding Stage</label>
          <select style={inputStyle} value={form.funding_stage} onChange={handleChange("funding_stage")}>
            <option>Bootstrapped</option>
            <option>Pre-seed</option>
            <option>Seed</option>
            <option>Series A</option>
            <option>Series B+</option>
          </select>
        </div>
      </div>

      <label style={labelStyle}>Location</label>
      <input style={inputStyle} type="text" value={form.location} onChange={handleChange("location")} placeholder="City, Country" />

      <label style={labelStyle}>Description</label>
      <textarea style={{ ...inputStyle, minHeight: "70px" }} value={form.description} onChange={handleChange("description")} />

      <label style={labelStyle}>Problem Statement</label>
      <textarea style={{ ...inputStyle, minHeight: "60px" }} value={form.problem_statement} onChange={handleChange("problem_statement")} />

      <label style={labelStyle}>Solution</label>
      <textarea style={{ ...inputStyle, minHeight: "60px" }} value={form.solution} onChange={handleChange("solution")} />

      <label style={labelStyle}>Technology Stack</label>
      <input style={inputStyle} type="text" value={form.technology_stack} onChange={handleChange("technology_stack")} placeholder="e.g. IoT, Machine Learning" />

      <label style={labelStyle}>Research Interests</label>
      <input style={inputStyle} type="text" value={form.research_interests} onChange={handleChange("research_interests")} placeholder="Topics you'd want researcher collaboration on" />

      <div style={{ display: "flex", gap: "12px" }}>
        <div style={{ flex: 1 }}>
          <label style={labelStyle}>Funding Needed</label>
          <input style={inputStyle} type="text" value={form.funding_needed} onChange={handleChange("funding_needed")} placeholder="e.g. $50,000" />
        </div>
        <div style={{ flex: 1 }}>
          <label style={labelStyle}>Team Size</label>
          <input style={inputStyle} type="number" min="1" value={form.team_size} onChange={handleChange("team_size")} />
        </div>
      </div>

      <label style={labelStyle}>Website</label>
      <input style={inputStyle} type="text" value={form.website} onChange={handleChange("website")} />

      <label style={labelStyle}>Pitch Deck URL</label>
      <input style={inputStyle} type="text" value={form.pitch_deck_url} onChange={handleChange("pitch_deck_url")} />

      <button type="submit" className="auth-submit" disabled={saving} style={{ width: "auto", padding: "10px 24px" }}>
        {saving ? "Saving..." : profileExists ? "Update Profile" : "Create Profile"}
      </button>

      {message && <p style={{ marginTop: "10px", fontSize: "13px", color: "#1C8C7A" }}>{message}</p>}
    </form>
  );
}

export default StartupProfileForm;
