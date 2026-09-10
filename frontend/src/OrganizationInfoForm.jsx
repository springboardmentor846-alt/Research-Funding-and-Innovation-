import { useEffect, useState } from "react";
import axios from "axios";

const API_BASE = "https://research-platform-backend-e0sf.onrender.com/api/v1/profile";

const emptyForm = {
  department: "",
  organization_type: "",
  city: "",
  state: "",
  country: "",
  website: "",
  description: "",
};

function OrganizationInfoForm({ token }) {
  const [form, setForm] = useState(emptyForm);
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  const authHeaders = { headers: { Authorization: `Bearer ${token}` } };

  useEffect(() => {
    const load = async () => {
      try {
        const res = await axios.get(`${API_BASE}/organization-info`, authHeaders);
        setForm({ ...emptyForm, ...res.data });
      } catch (err) {
        // No organization info set yet — that's fine, keep the empty form.
      }
      setLoading(false);
    };
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const handleChange = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage("");
    try {
      await axios.put(`${API_BASE}/organization-info`, form, authHeaders);
      setMessage("Organization information saved.");
    } catch (err) {
      setMessage(err.response?.data?.detail || "Could not save organization information.");
    }
    setSaving(false);
  };

  if (loading) return <p className="dash-empty">Loading...</p>;

  const inputStyle = {
    width: "100%",
    padding: "9px 12px",
    marginBottom: "12px",
    border: "1px solid #d0d7de",
    borderRadius: "6px",
    fontSize: "13.5px",
  };
  const labelStyle = { fontSize: "12.5px", fontWeight: 600, marginBottom: "4px", display: "block" };

  return (
    <div className="dash-card" id="profile-organization-section">
      <h3>Organization Information</h3>
      <p className="dash-card-subtitle" style={{ marginBottom: "14px" }}>
        Extended details about your organization or institution.
      </p>

      <form onSubmit={handleSubmit}>
        <div style={{ display: "flex", gap: "10px" }}>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>Department</label>
            <input style={inputStyle} type="text" value={form.department || ""} onChange={handleChange("department")} />
          </div>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>Organization Type</label>
            <input style={inputStyle} type="text" value={form.organization_type || ""} onChange={handleChange("organization_type")} placeholder="University, Company, etc." />
          </div>
        </div>

        <div style={{ display: "flex", gap: "10px" }}>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>City</label>
            <input style={inputStyle} type="text" value={form.city || ""} onChange={handleChange("city")} />
          </div>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>State</label>
            <input style={inputStyle} type="text" value={form.state || ""} onChange={handleChange("state")} />
          </div>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>Country</label>
            <input style={inputStyle} type="text" value={form.country || ""} onChange={handleChange("country")} />
          </div>
        </div>

        <label style={labelStyle}>Website</label>
        <input style={inputStyle} type="text" value={form.website || ""} onChange={handleChange("website")} />

        <label style={labelStyle}>Description</label>
        <textarea
          style={{ ...inputStyle, minHeight: "60px" }}
          value={form.description || ""}
          onChange={handleChange("description")}
        />

        <button type="submit" className="auth-submit" disabled={saving} style={{ width: "auto", padding: "8px 20px" }}>
          {saving ? "Saving..." : "Save Organization Info"}
        </button>

        {message && <p style={{ marginTop: "8px", fontSize: "12.5px", color: "#1C8C7A" }}>{message}</p>}
      </form>
    </div>
  );
}

export default OrganizationInfoForm;
