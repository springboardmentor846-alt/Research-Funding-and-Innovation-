import { useState } from "react";
import axios from "axios";

function FundingExplanationButton({ token, fundingId }) {
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [open, setOpen] = useState(false);

  const handleClick = async () => {
    if (open) {
      setOpen(false);
      return;
    }

    setOpen(true);
    if (explanation || loading) return;

    setLoading(true);
    setError("");
    try {
      const response = await axios.get(
        `http://127.0.0.1:8000/api/v1/profile/funding/${fundingId}/explanation`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setExplanation(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not load explanation.");
    }
    setLoading(false);
  };

  return (
    <div style={{ marginTop: "8px" }}>
      <button
        type="button"
        onClick={handleClick}
        style={{
          background: "none",
          border: "none",
          color: "#1C8C7A",
          fontSize: "12.5px",
          fontWeight: 600,
          cursor: "pointer",
          padding: 0,
        }}
      >
        {open ? "Hide explanation" : "Why recommended?"}
      </button>

      {open && (
        <div style={{ marginTop: "6px", fontSize: "12.5px" }}>
          {loading && <p className="dash-empty">Loading...</p>}
          {error && <p className="dash-error">{error}</p>}
          {explanation && (
            <ul style={{ margin: 0, paddingLeft: "18px", color: "#555" }}>
              {explanation.reasons.map((reason, idx) => (
                <li key={idx}>{reason}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

export default FundingExplanationButton;