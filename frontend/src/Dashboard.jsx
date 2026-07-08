import { useEffect, useState } from "react";
import axios from "axios";

function Dashboard({ token, onLogout }) {
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState("");
  const [funding, setFunding] = useState([]);
  const [fundingError, setFundingError] = useState("");

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/auth/me", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setProfile(response.data);
      } catch (err) {
        setError("Could not load profile");
      }
    };

    fetchProfile();
  }, [token]);

  useEffect(() => {
    const fetchFunding = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/funding/recommended", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setFunding(response.data);
      } catch (err) {
        if (err.response && err.response.status === 404) {
          setFundingError("Create your research profile to see recommendations.");
        } else {
          setFundingError("Could not load funding recommendations.");
        }
      }
    };

    fetchFunding();
  }, [token]);

  return (
    <div style={{ maxWidth: "500px", margin: "60px auto", fontFamily: "sans-serif" }}>
      <h2>Dashboard</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {profile && (
        <div>
          <p><strong>Email:</strong> {profile.email}</p>
          <p><strong>Role:</strong> {profile.role}</p>
        </div>
      )}

      <hr style={{ margin: "24px 0" }} />

      <h3>Recommended Funding</h3>
      {fundingError && <p style={{ color: "gray" }}>{fundingError}</p>}

      {!fundingError && funding.length === 0 && (
        <p style={{ color: "gray" }}>No matching funding opportunities right now.</p>
      )}

      {funding.map((item) => (
        <div
          key={item.id}
          style={{
            border: "1px solid #444",
            borderRadius: "8px",
            padding: "12px",
            marginBottom: "10px",
          }}
        >
          <h4 style={{ margin: "0 0 6px 0" }}>{item.title}</h4>
          <p style={{ margin: "2px 0", fontSize: "14px" }}><strong>Source:</strong> {item.source}</p>
          <p style={{ margin: "2px 0", fontSize: "14px" }}><strong>Amount:</strong> {item.amount}</p>
          <p style={{ margin: "2px 0", fontSize: "14px" }}><strong>Deadline:</strong> {item.deadline}</p>
          <p style={{ margin: "2px 0", fontSize: "14px" }}>{item.description}</p>
        </div>
      ))}

      <button onClick={onLogout} style={{ marginTop: "20px", padding: "8px 16px" }}>
        Logout
      </button>
    </div>
  );
}

export default Dashboard;