import { useEffect, useState } from "react";
import api from "../api/api";
import { toast } from "react-toastify";

export default function InnovationDashboard() {

  const [summary, setSummary] = useState(null);
  const [innovation, setInnovation] = useState(null);
  const [domains, setDomains] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [patentTrend, setPatentTrend] = useState([]);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {

      const [
        summaryRes,
        innovationRes,
        domainRes,
        organizationRes,
        trendRes,
      ] = await Promise.all([
        api.get("/analytics/dashboard-summary"),
        api.get("/analytics/innovation-score"),
        api.get("/analytics/technology-domains"),
        api.get("/patent-intelligence/top-organizations"),
        api.get("/analytics/patent-trends"),
      ]);

      setSummary(summaryRes.data);
      setInnovation(innovationRes.data);
      setDomains(domainRes.data);
      setOrganizations(organizationRes.data);
      setPatentTrend(trendRes.data);

    } catch {
      toast.error("Unable to load Innovation Dashboard");
    }
  };

  if (!summary || !innovation) {
    return (
      <section>
        <div className="loading">
          Loading Innovation Dashboard...
        </div>
      </section>
    );
  }

  return (
    <section>

      <div className="page-heading">
        <div>

          <p className="eyebrow">
            INNOVATION ANALYTICS DASHBOARD
          </p>

          <h1>Innovation Dashboard</h1>

          <p>
            Complete overview of research,
            patents, funding and innovation.
          </p>

        </div>
      </div>


      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit,minmax(220px,1fr))",
          gap: "20px",
        }}
      >

        <div className="panel">
          <h3>Innovation Score</h3>
          <h1>{innovation.innovation_score}</h1>
        </div>

        <div className="panel">
          <h3>Research Profiles</h3>
          <h1>{summary.research_profiles}</h1>
        </div>

        <div className="panel">
          <h3>Publications</h3>
          <h1>{summary.publications}</h1>
        </div>

        <div className="panel">
          <h3>Patents</h3>
          <h1>{summary.patents}</h1>
        </div>

        <div className="panel">
          <h3>Funding Opportunities</h3>
          <h1>{summary.funding_opportunities}</h1>
        </div>

      </div>


      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit,minmax(350px,1fr))",
          gap: "20px",
          marginTop: "30px",
        }}
      >

        <div className="panel">

          <h2>Technology Domains</h2>

          {domains.map((item) => (

            <div
              key={item.domain}
              style={{
                display: "flex",
                justifyContent: "space-between",
                padding: "8px 0",
                borderBottom: "1px solid #eee",
              }}
            >
              <span>{item.domain}</span>

              <strong>{item.count}</strong>

            </div>

          ))}

        </div>

        <div className="panel">

          <h2>Top Organizations</h2>

          {organizations.map((item) => (

            <div
              key={item.organization}
              style={{
                display: "flex",
                justifyContent: "space-between",
                padding: "8px 0",
                borderBottom: "1px solid #eee",
              }}
            >

              <span>{item.organization}</span>

              <strong>{item.count}</strong>

            </div>

          ))}

        </div>

      </div>


      <div
        className="panel"
        style={{ marginTop: "30px" }}
      >

        <h2>Patent Trend</h2>

        <table className="table">

          <thead>

            <tr>
              <th>Year</th>
              <th>Patents</th>
            </tr>

          </thead>

          <tbody>

            {patentTrend.map((item) => (

              <tr key={item.year}>

                <td>{item.year}</td>

                <td>{item.count}</td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>

    </section>
  );
}