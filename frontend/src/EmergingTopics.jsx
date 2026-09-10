import { useEffect, useState } from "react";
import axios from "axios";

function EmergingTopics() {
  const [topics, setTopics] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const response = await axios.get(
          "https://research-platform-backend-e0sf.onrender.com/api/v1/profile/publications/emerging-topics"
        );
        setTopics(response.data);
      } catch (err) {
        setError("Could not load emerging topics");
      }
    };

    fetchTopics();
  }, []);

  if (error) return <p className="dash-error">{error}</p>;

  if (topics.length === 0) {
    return <p className="dash-empty">No emerging topics detected yet.</p>;
  }

  return (
    <div className="topics-grid">
      {topics.map((t) => (
        <div key={t.topic} className={`topic-chip ${t.status}`}>
          <span className="topic-name">{t.topic}</span>
          <span className="topic-count">{t.recent_mentions}</span>
        </div>
      ))}
    </div>
  );
}

export default EmergingTopics;

