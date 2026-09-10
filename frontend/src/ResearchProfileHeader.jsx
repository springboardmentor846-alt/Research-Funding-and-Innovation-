import { useEffect, useState } from "react";
import axios from "axios";

function ResearchProfileHeader({ token }) {
  const [profileExists, setProfileExists] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const check = async () => {
      try {
        await axios.get("https://research-platform-backend-e0sf.onrender.com/api/v1/profile/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setProfileExists(true);
      } catch (err) {
        setProfileExists(false);
      }
      setLoading(false);
    };
    check();
  }, [token]);

  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const quickLinks = [
    { id: "profile-organization-section", icon: "🏢", title: "Organization", desc: "Manage university, department and institution details." },
    { id: "profile-domains-section", icon: "🧪", title: "Research Domains", desc: "Define your primary research fields." },
    { id: "profile-keywords-section", icon: "🏷", title: "Keywords", desc: "Add focused research interests." },
    { id: "profile-tech-areas-section", icon: "💡", title: "Technology Areas", desc: "Maintain technologies and technical expertise." },
  ];

  return (
    <>
      <div className="dash-card" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "12px" }}>
        <div>
          <span style={{ fontSize: "11px", fontWeight: 700, letterSpacing: "0.06em", color: "#1C8C7A" }}>
            PROFILE MANAGEMENT
          </span>
          <h2 style={{ margin: "6px 0 4px" }}>Research Profile</h2>
          <p className="dash-card-subtitle" style={{ margin: 0 }}>
            Maintain your academic identity and professional research information.
          </p>
        </div>

        {!loading && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              padding: "6px 12px",
              borderRadius: "20px",
              fontSize: "12.5px",
              fontWeight: 600,
              background: profileExists ? "#e6f4ea" : "#fdecea",
              color: profileExists ? "#1e7e34" : "#b3261e",
            }}
          >
            <span
              style={{
                width: "7px",
                height: "7px",
                borderRadius: "50%",
                background: profileExists ? "#1e7e34" : "#b3261e",
                display: "inline-block",
              }}
            />
            {profileExists ? "Profile Created" : "Profile Not Created"}
          </div>
        )}
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
          gap: "12px",
          marginBottom: "20px",
        }}
      >
        {quickLinks.map((link) => (
          <div
            key={link.title}
            onClick={() => scrollTo(link.id)}
            className="dash-card"
            style={{ margin: 0, cursor: "pointer", display: "flex", gap: "10px", alignItems: "flex-start" }}
          >
            <div style={{ fontSize: "20px" }}>{link.icon}</div>
            <div>
              <h4 style={{ margin: "0 0 4px", fontSize: "14px" }}>{link.title}</h4>
              <p style={{ margin: 0, fontSize: "12px", color: "#667085" }}>{link.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

export default ResearchProfileHeader;
