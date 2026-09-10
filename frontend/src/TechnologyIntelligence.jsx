import { useEffect, useState } from "react";
import axios from "axios";

function TechnologyIntelligence() {
  const [techs, setTechs] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchTech = async () => {
      try {
        const response = await axios.get(
          "https://research-platform-backend-e0sf.onrender.com/api/v1/profile/technology-intelligence"
        );
        setTechs(response.data);
      } catch (err) {
        setError("Could not load technology intelligence");
      }
    };

    fetchTech();
  }, []);

  if (error) return <p className="dash-error">{error}</p>;

  if (techs.length === 0) {
    return <p className="dash-empty">No technology data yet.</p>;
  }

  return (
    <div className="tech-grid">
      {techs.map((t) => (
        <div key={t.technology} className="tech-card">
          <div className="tech-card-top">
            <span className="tech-name">{t.technology}</span>
            {t.cross_domain && <span className="tech-cross-badge">Cross-Domain</span>}
          </div>
          <div className="tech-maturity-row">
            <span className={`maturity-badge ${t.maturity.toLowerCase()}`}>
              {t.maturity}
            </span>
          </div>
          <div className="tech-meta">
            <span>Research: {t.research_mentions}</span>
            <span>Patents: {t.patent_mentions}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

export default TechnologyIntelligence;

