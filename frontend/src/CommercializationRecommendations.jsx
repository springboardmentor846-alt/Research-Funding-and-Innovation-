import { useEffect, useState } from "react";
import axios from "axios";

function CommercializationRecommendations({ token }) {
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        const response = await axios.get(
          "http://127.0.0.1:8000/api/profile/commercialization-recommendations",
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setRecommendations(response.data);
      } catch (err) {
        if (err.response && err.response.status === 404) {
          setError("Create your research profile to see recommendations.");
        } else {
          setError("Could not load commercialization recommendations.");
        }
      }
    };

    fetchRecommendations();
  }, [token]);

  if (error) return <p className="dash-empty">{error}</p>;

  if (recommendations.length === 0) {
    return <p className="dash-empty">No recommendations yet.</p>;
  }

  return (
    <div className="commercial-list">
      {recommendations.map((r, idx) => (
        <div key={idx} className="commercial-card">
          <div className="commercial-top">
            <span className="commercial-type">{r.type}</span>
            <span className={`priority-badge priority-${r.priority.toLowerCase()}`}>
              {r.priority} Priority
            </span>
          </div>
          <p className="commercial-text">{r.recommendation}</p>
        </div>
      ))}
    </div>
  );
}

export default CommercializationRecommendations;