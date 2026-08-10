import { useEffect, useState } from "react";
import { Bar, Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

import api from "../api/api";
import "./Dashboard.css";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Tooltip,
  Legend
);

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [trends, setTrends] = useState([]);
  const [patentTrends, setPatentTrends] = useState([]);
  const [technologyDomains, setTechnologyDomains] = useState([]);
  const [innovationScore, setInnovationScore] = useState(0);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const [
        summaryRes,
        trendRes,
        patentTrendRes,
        technologyRes,
        innovationRes,
      ] = await Promise.all([
        api.get("/analytics/dashboard-summary"),
        api.get("/analytics/publication-trends"),
        api.get("/analytics/patent-trends"),
        api.get("/analytics/technology-domains"),
        api.get("/analytics/innovation-score"),
      ]);

      setSummary(summaryRes.data);
      setTrends(trendRes.data);
      setPatentTrends(patentTrendRes.data);
      setTechnologyDomains(technologyRes.data);
      setInnovationScore(innovationRes.data.innovation_score);
    } catch (err) {
      console.error(err);
    }
  };

  const cards = [
    ["Research Profile", summary?.research_profiles ?? 0, "person-vcard"],
    ["Publications", summary?.publications ?? 0, "journal-text"],
    ["Patents", summary?.patents ?? 0, "lightbulb"],
    ["Funding", summary?.funding_opportunities ?? 0, "cash-stack"],
    ["Innovation Score", innovationScore, "award"],
  ];

  return (
    <section className="dashboard-page">
      <div className="dashboard-hero">
        <div>
          <p className="eyebrow">INTELLIGENCE HUB</p>
          <h1>Your Research Dashboard</h1>
          <p>
            Monitor publications, patents and funding opportunities from one
            place.
          </p>
        </div>

        <span className="dashboard-status">
          <i className="bi bi-circle-fill"></i> Live Insights
        </span>
      </div>

      <div className="dashboard-stats">
        {cards.map(([label, value, icon]) => (
          <article className="dashboard-stat" key={label}>
            <i className={`bi bi-${icon}`}></i>
            <span>{label}</span>
            <strong>{value}</strong>
          </article>
        ))}
      </div>

      <div
          className="dashboard-charts"
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit,minmax(420px,1fr))",
            gap: "24px",
            }}
            >
        <article className="dashboard-chart-card">
          <h2>Publication Trend</h2>

          <div className="dashboard-chart">
            <Bar
              data={{
                labels: trends.map((t) => t.year),
                datasets: [
                  {
                    label: "Publications",
                    data: trends.map((t) => t.count),
                    backgroundColor: "#5b5ce2",
                    borderRadius: 8,
                  },
                ],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
              }}
            />
          </div>
        </article>

        <article className="dashboard-chart-card">
          <h2>Research Portfolio</h2>

          <div className="dashboard-chart">
            <Doughnut
              data={{
                labels: ["Publications", "Patents"],
                datasets: [
                  {
                    data: [
                      summary?.publications ?? 0,
                      summary?.patents ?? 0,
                    ],
                    backgroundColor: ["#5b5ce2", "#28b48c"],
                    borderWidth: 0,
                  },
                ],
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
              }}
            />
          </div>
        </article>
        <article className="dashboard-chart-card">
  <h2>Patent Trend</h2>

  <div className="dashboard-chart">
    <Bar
      data={{
        labels: patentTrends.map((t) => t.year),
        datasets: [
          {
            label: "Patents",
            data: patentTrends.map((t) => t.count),
            backgroundColor: "#28b48c",
            borderRadius: 8,
          },
        ],
      }}
      options={{
        responsive: true,
        maintainAspectRatio: false,
      }}
    />
  </div>
</article>

<article className="dashboard-chart-card">
  <h2>Technology Distribution</h2>

  <div className="dashboard-chart">
    <Doughnut
      data={{
        labels: technologyDomains.map((t) => t.domain),
        datasets: [
          {
            data: technologyDomains.map((t) => t.count),
            backgroundColor: [
              "#5b5ce2",
              "#28b48c",
              "#f4a261",
              "#ef476f",
              "#06d6a0",
              "#118ab2",
            ],
          },
        ],
      }}
      options={{
        responsive: true,
        maintainAspectRatio: false,
      }}
    />
  </div>
</article>
      </div>
    </section>
  );
}