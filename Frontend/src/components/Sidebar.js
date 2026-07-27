import React from "react";
import { Link } from "react-router-dom";

function Sidebar() {
  return (
    <div
      style={{
        width: "250px",
        height: "100vh",
        backgroundColor: "#0f172a",
        color: "white",
        padding: "20px",
        position: "fixed",
        top: 0,
        left: 0,
        overflow:"scroll",
      }}
    >
      <h2 style={{ textAlign: "center", marginBottom: "30px" }}>
        Innovation Platform
      </h2>

      <nav
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "15px",
        }}
      >
        <Link to="/" style={menuStyle}>📊 Dashboard</Link>

        <Link to="/funding" style={menuStyle}>💰 Funding</Link>

        <Link to="/research" style={menuStyle}>🔬 Research Project</Link>

        <Link to="/research-profile" style={menuStyle}>
          👨‍🔬 Research Profile
        </Link>

        <Link to="/publication-trends" style={menuStyle}>
          📈 Publication Trends
        </Link>

        <Link to="/recommendation" style={menuStyle}>
          ⭐ Recommendation
        </Link>

        <Link to="/grant-matching" style={menuStyle}>
          🎯 Grant Matching
        </Link>

        <Link to="/patents" style={menuStyle}>
          📄 Patents
        </Link>
        <Link to="/profile" style={menuStyle}>👤 Profile</Link>
      </nav>
    </div>
  );
}

const menuStyle = {
  color: "white",
  textDecoration: "none",
  background: "#1e293b",
  padding: "12px 15px",
  borderRadius: "8px",
  fontSize: "16px",
};

export default Sidebar;