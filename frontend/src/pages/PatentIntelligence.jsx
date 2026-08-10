import { useEffect, useState } from "react";
import api from "../api/api";
import { toast } from "react-toastify";

export default function PatentIntelligence() {
  const [patents, setPatents] = useState([]);
  const [distribution, setDistribution] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [keyword, setKeyword] = useState("");

  const loadDashboard = async () => {
    try {
      const [p, d, o] = await Promise.all([
        api.get("/patent-intelligence/search"),
        api.get("/patent-intelligence/technology-distribution"),
        api.get("/patent-intelligence/top-organizations"),
      ]);

      setPatents(p.data);
      setDistribution(d.data);
      setOrganizations(o.data);
    } catch {
      toast.error("Unable to load Patent Intelligence");
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const searchPatent = async () => {
    try {
      const res = await api.get(
        `/patent-intelligence/search?keyword=${keyword}`
      );
      setPatents(res.data);
    } catch {
      toast.error("Search failed");
    }
  };

  return (
    <section>

      <div className="page-heading">
        <div>
          <p className="eyebrow">
            PATENT LANDSCAPE ANALYSIS
          </p>

          <h1>Patent Intelligence</h1>

          <p>
            Analyze patent landscape, technology
            domains and innovation trends.
          </p>
        </div>
      </div>

      <div className="panel">

        <div
          style={{
            display: "flex",
            gap: "12px",
            marginBottom: "20px",
          }}
        >

          <input
            placeholder="Search Patent..."
            value={keyword}
            onChange={(e) =>
              setKeyword(e.target.value)
            }
          />

          <button
            className="btn-primary"
            onClick={searchPatent}
          >
            Search
          </button>

        </div>

      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit,minmax(320px,1fr))",
          gap: "20px",
        }}
      >

        <div className="panel">

          <h3>Technology Distribution</h3>

          {distribution.map((d) => (
            <div key={d.technology}>
              {d.technology}

              <strong
                style={{
                  float: "right",
                }}
              >
                {d.count}
              </strong>
            </div>
          ))}

        </div>

        <div className="panel">

          <h3>Top Organizations</h3>

          {organizations.map((o) => (
            <div key={o.organization}>
              {o.organization}

              <strong
                style={{
                  float: "right",
                }}
              >
                {o.count}
              </strong>
            </div>
          ))}

        </div>

      </div>

      <div
        className="record-list"
        style={{
          marginTop: "25px",
        }}
      >

        {patents.map((p) => (

          <article
            className="record"
            key={p.id}
          >

            <div>

              <h3>{p.title}</h3>

              <p>{p.assignee}</p>

              <small>
                {p.technology_domain}
              </small>

              <br />

              <small>
                {p.filing_date}
              </small>

            </div>

          </article>

        ))}

      </div>

    </section>
  );
}