import { useState } from "react";
import axios from "axios";

function PredictSuccessButton({ token, fundingId }) {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [open, setOpen] = useState(false);

  const handleClick = async () => {
    if (open) {
      setOpen(false);
      return;
    }

    setOpen(true);
    if (prediction || loading) return;

    setLoading(true);
    setError("");
    try {
      const response = await axios.get(
        `http://127.0.0.1:8000/api/v1/profile/funding/${fundingId}/predict-success`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setPrediction(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not load prediction.");
    }
    setLoading(false);
  };

  const ratingColor = (rating) => {
    if (rating === "Strong Match") return "#1C8C7A";
    if (rating === "Moderate Match") return "#C9862B";
    return "#B0479B";
  };

  return (
    <div style={{ marginTop: "6px" }}>
      <button
        type="button"
        onClick={handleClick}
        style={{
          background: "none",
          border: "none",
          color: "#2E5EAA",
          fontSize: "12.5px",
          fontWeight: 600,
          cursor: "pointer",
          padding: 0,
        }}
      >
        {open ? "Hide prediction" : "Predict Success"}
      </button>

      {open && (
        <div style={{ marginTop: "6px", fontSize: "12.5px" }}>
          {loading && <p className="dash-empty">Predicting...</p>}
          {error && <p className="dash-error">{error}</p>}
          {prediction && (
            <div>
              <p style={{ fontWeight: 700, color: ratingColor(prediction.rating) }}>
                {prediction.success_probability}% — {prediction.rating}
              </p>
              <p style={{ color: "#888", fontSize: "11.5px" }}>
                Based on your publications, patents, profile, and text match with this
                opportunity. This is a decision-support estimate, not a guarantee.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default PredictSuccessButton;