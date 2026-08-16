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
import { toast } from "react-toastify";

import "./Dashboard.css";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Tooltip,
  Legend
);

export default function ExecutiveDashboard() {
  const [summary, setSummary] = useState(null);
  const [publicationTrends, setPublicationTrends] = useState([]);
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
        publicationRes,
        patentRes,
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
      setPublicationTrends(publicationRes.data);
      setPatentTrends(patentRes.data);
      setTechnologyDomains(technologyRes.data);
      setInnovationScore(
        innovationRes.data.innovation_score ?? 0
      );
    } catch (error) {
      console.error(error);
      toast.error("Unable to load executive dashboard");
    }
  };

  if (!summary) {
    return (
      <section>
        <div className="loading">
          Loading Executive Dashboard...
        </div>
      </section>
    );
  }

  const publications = summary.publications ?? 0;
  const patents = summary.patents ?? 0;
  const funding = summary.funding_opportunities ?? 0;
  const profiles = summary.research_profiles ?? 0;

  const portfolioStrength =
    innovationScore >= 70
      ? "Strong"
      : innovationScore >= 40
      ? "Moderate"
      : "Developing";

  const topTechnology =
    technologyDomains.length > 0
      ? [...technologyDomains].sort(
          (a, b) => b.count - a.count
        )[0]?.domain
      : "No data";

  return (
    <section className="dashboard-page">

      {/* HEADER */}

      <div className="dashboard-hero">
        <div>
          <p className="eyebrow">
            EXECUTIVE INTELLIGENCE
          </p>

          <h1>
            Executive Dashboard
          </h1>

          <p>
            High-level overview of research,
            innovation, patent and funding performance.
          </p>
        </div>

        <span className="dashboard-status">
          <i className="bi bi-circle-fill"></i>
          Live Insights
        </span>
      </div>


      {/* EXECUTIVE KPI CARDS */}

      <div className="dashboard-stats">

        <article className="dashboard-stat">
          <i className="bi bi-award"></i>

          <span>
            Innovation Score
          </span>

          <strong>
            {innovationScore}/100
          </strong>
        </article>


        <article className="dashboard-stat">
          <i className="bi bi-journal-text"></i>

          <span>
            Publications
          </span>

          <strong>
            {publications}
          </strong>
        </article>


        <article className="dashboard-stat">
          <i className="bi bi-lightbulb"></i>

          <span>
            Patents
          </span>

          <strong>
            {patents}
          </strong>
        </article>


        <article className="dashboard-stat">
          <i className="bi bi-cash-stack"></i>

          <span>
            Funding Opportunities
          </span>

          <strong>
            {funding}
          </strong>
        </article>

      </div>


      {/* EXECUTIVE SUMMARY */}

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit,minmax(260px,1fr))",
          gap: "22px",
          marginBottom: "28px",
        }}
      >

        <article className="dashboard-chart-card">

          <h2>
            Portfolio Overview
          </h2>

          <div
            style={{
              marginTop: "18px",
              lineHeight: "1.9",
            }}
          >
            <p>
              <strong>
                Research Profiles:
              </strong>{" "}
              {profiles}
            </p>

            <p>
              <strong>
                Publications:
              </strong>{" "}
              {publications}
            </p>

            <p>
              <strong>
                Patents:
              </strong>{" "}
              {patents}
            </p>

            <p>
              <strong>
                Innovation Level:
              </strong>{" "}
              {portfolioStrength}
            </p>

          </div>

        </article>


        <article className="dashboard-chart-card">

          <h2>
            Technology Intelligence
          </h2>

          <div
            style={{
              marginTop: "18px",
            }}
          >

            <p>
              <strong>
                Leading Technology Domain
              </strong>
            </p>

            <h2
              style={{
                fontSize: "24px",
                marginTop: "8px",
              }}
            >
              {topTechnology}
            </h2>

            <p>
              Technology distribution is based on
              the current research and patent portfolio.
            </p>

          </div>

        </article>

      </div>


      {/* CHARTS */}

      <div
        className="dashboard-charts"
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit,minmax(420px,1fr))",
          gap: "24px",
        }}
      >

        {/* PUBLICATION TREND */}

        <article className="dashboard-chart-card">

          <h2>
            Research Publication Trend
          </h2>

          <div className="dashboard-chart">

            <Bar
              data={{
                labels: publicationTrends.map(
                  (item) => item.year
                ),

                datasets: [
                  {
                    label: "Publications",

                    data: publicationTrends.map(
                      (item) => item.count
                    ),

                    backgroundColor:
                      "#5b5ce2",

                    borderRadius: 8,
                  },
                ],
              }}

              options={{
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                  legend: {
                    display: true,
                  },
                },
              }}
            />

          </div>

        </article>


        {/* PATENT TREND */}

        <article className="dashboard-chart-card">

          <h2>
            Patent Trend
          </h2>

          <div className="dashboard-chart">

            <Bar
              data={{
                labels: patentTrends.map(
                  (item) => item.year
                ),

                datasets: [
                  {
                    label: "Patents",

                    data: patentTrends.map(
                      (item) => item.count
                    ),

                    backgroundColor:
                      "#28b48c",

                    borderRadius: 8,
                  },
                ],
              }}

              options={{
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                  legend: {
                    display: true,
                  },
                },
              }}
            />

          </div>

        </article>


        {/* RESEARCH PORTFOLIO */}

        <article className="dashboard-chart-card">

          <h2>
            Research Portfolio
          </h2>

          <div className="dashboard-chart">

            <Doughnut
              data={{
                labels: [
                  "Publications",
                  "Patents",
                ],

                datasets: [
                  {
                    data: [
                      publications,
                      patents,
                    ],

                    backgroundColor: [
                      "#5b5ce2",
                      "#28b48c",
                    ],

                    borderWidth: 0,
                  },
                ],
              }}

              options={{
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                  legend: {
                    position: "bottom",
                  },
                },
              }}
            />

          </div>

        </article>


        {/* TECHNOLOGY DISTRIBUTION */}

        <article className="dashboard-chart-card">

          <h2>
            Technology Distribution
          </h2>

          <div className="dashboard-chart">

            <Doughnut
              data={{
                labels: technologyDomains.map(
                  (item) => item.domain
                ),

                datasets: [
                  {
                    data: technologyDomains.map(
                      (item) => item.count
                    ),

                    backgroundColor: [
                      "#5b5ce2",
                      "#28b48c",
                      "#f4a261",
                      "#ef476f",
                      "#06d6a0",
                      "#118ab2",
                    ],

                    borderWidth: 0,
                  },
                ],
              }}

              options={{
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                  legend: {
                    position: "bottom",
                  },
                },
              }}
            />

          </div>

        </article>

      </div>

    </section>
  );
}