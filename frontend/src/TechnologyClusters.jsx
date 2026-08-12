import { useEffect, useState } from "react";
import axios from "axios";

function TechnologyClusters() {
  const [clusters, setClusters] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchClusters = async () => {
      try {
        const response = await axios.get(
          "http://127.0.0.1:8000/api/v1/profile/patents/technology-clusters"
        );
        setClusters(response.data);
      } catch (err) {
        setError("Could not load technology clusters");
      }
    };

    fetchClusters();
  }, []);

  if (error) return <p className="dash-error">{error}</p>;

  if (clusters.length === 0) {
    return <p className="dash-empty">No technology clusters detected yet.</p>;
  }

  return (
    <div className="topics-grid">
      {clusters.map((c) => (
        <div key={c.technology} className="topic-chip new">
          <span className="topic-name">{c.technology}</span>
          <span className="topic-count">{c.mentions}</span>
        </div>
      ))}
    </div>
  );
}

export default TechnologyClusters;
