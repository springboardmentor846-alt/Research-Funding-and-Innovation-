import { useEffect, useState } from "react";
import api from "../api/api";
import { toast } from "react-toastify";

export default function GrantMatching() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadMatches = async () => {
    try {
      const res = await api.get("/funding/match");
      setMatches(res.data);
    } catch (err) {
      toast.error(
        err.response?.data?.detail ||
          "Complete your research profile to calculate grant matches."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMatches();
  }, []);

  if (loading) {
    return (
      <section>
        <div className="loading">
          Loading grant matches...
        </div>
      </section>
    );
  }

  return (
    <section>
      <div className="page-heading">
        <div>
          <p className="eyebrow">GRANT MATCHING</p>

          <h1>Opportunity Fit Analysis</h1>

          <p>
            Funding opportunities are ranked using research
            domain, technology area, keyword similarity and
            organization eligibility.
          </p>
        </div>
      </div>

      <div className="panel">
        {matches.length === 0 ? (
          <div className="empty">
            <h3>No Matching Opportunities</h3>

            <p>
              Add funding opportunities and complete your
              research profile to generate grant matches.
            </p>
          </div>
        ) : (
          <>
            <div className="match-head">
              <span>Opportunity</span>
              <span>Research Fit</span>
              <span>Score</span>
            </div>

            {matches.map((item, index) => (
              <div
                className="match-row"
                key={item.id ?? item.title ?? index}
              >
                <div>
                  <strong>{item.title}</strong>

                  <small>{item.funding_agency}</small>

                  <small>
                    {item.research_domain} • {item.technology_area}
                  </small>
                </div>

                <div className="score-track">
                  <i
                    style={{
                      width: `${item.match_score}%`,
                    }}
                  />
                </div>

                <b>{item.match_score}%</b>
              </div>
            ))}
          </>
        )}
      </div>
    </section>
  );
}