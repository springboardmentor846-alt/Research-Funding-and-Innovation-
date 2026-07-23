import { useEffect, useState } from "react";
import api from "../api/api";
import { toast } from "react-toastify";

export default function Recommendations() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadRecommendations = async () => {
    try {
      const res = await api.get("/funding/recommendations");
      setItems(res.data);
    } catch (err) {
      toast.error(
        err.response?.data?.detail ||
          "Complete your research profile to receive recommendations."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRecommendations();
  }, []);

  if (loading) {
    return (
      <section>
        <div className="loading">
          Loading recommendations...
        </div>
      </section>
    );
  }

  return (
    <section>
      <div className="page-heading">
        <div>
          <p className="eyebrow">
            AI FUNDING RECOMMENDATIONS
          </p>

          <h1>Recommended Funding</h1>

          <p>
            Personalized funding opportunities generated
            from your research profile, keywords,
            technology area and research domain.
          </p>
        </div>
      </div>

      <div className="opportunity-grid">
        {items.length === 0 ? (
          <div className="panel empty">
            <h3>No Recommendations Available</h3>

            <p>
              Complete your research profile and add
              funding opportunities to receive
              personalized recommendations.
            </p>
          </div>
        ) : (
          items.map((item) => (
            <article
              className="opportunity"
              key={item.id}
            >
              <span className="tag">
                Recommended
              </span>

              <h3>{item.title}</h3>

              <p>{item.funding_agency}</p>

              <div className="opportunity-meta">
                <span>{item.amount}</span>

                <span>Due {item.deadline}</span>
              </div>

              <small>
                {item.research_domain}
              </small>

              <br />

              <small>
                {item.technology_area}
              </small>

              <br />

              <small>{item.keywords}</small>

              {item.description && (
                <p className="description">
                  {item.description}
                </p>
              )}

              {item.score !== undefined && (
                <div
                  style={{
                    marginTop: "16px",
                    display: "inline-block",
                    background: "#eef2ff",
                    color: "#5b5ce2",
                    padding: "8px 12px",
                    borderRadius: "8px",
                    fontWeight: "700",
                  }}
                >
                  Match Score: {item.score}%
                </div>
              )}

              {item.link && (
                <a
                  className="apply-link"
                  href={item.link}
                  target="_blank"
                  rel="noreferrer"
                >
                  Apply Now ↗
                </a>
              )}
            </article>
          ))
        )}
      </div>
    </section>
  );
}