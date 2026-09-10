import { useEffect, useState } from "react";
import axios from "axios";

function ResearchHotspots() {
  const [hotspots, setHotspots] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchHotspots = async () => {
      try {
        const response = await axios.get(
          "https://research-platform-backend-e0sf.onrender.com/api/v1/profile/publications/research-hotspots"
        );
        setHotspots(response.data);
      } catch (err) {
        setError("Could not load research hotspots");
      }
    };

    fetchHotspots();
  }, []);

  if (error) return <p className="dash-error">{error}</p>;

  if (hotspots.length === 0) {
    return <p className="dash-empty">No research hotspots detected yet.</p>;
  }

  const maxMentions = Math.max(...hotspots.map((h) => h.mentions));

  return (
    <div className="hotspot-list">
      {hotspots.map((h) => (
        <div key={h.topic} className="hotspot-row">
          <span className="hotspot-name">{h.topic}</span>
          <div className="hotspot-bar-track">
            <div
              className="hotspot-bar-fill"
              style={{ width: `${(h.mentions / maxMentions) * 100}%` }}
            />
          </div>
          <span className="hotspot-count">{h.mentions}</span>
        </div>
      ))}
    </div>
  );
}

export default ResearchHotspots;

