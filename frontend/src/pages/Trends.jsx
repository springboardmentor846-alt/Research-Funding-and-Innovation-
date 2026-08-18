import React, { useEffect, useState } from "react";
import { trendsAPI } from "../services/api.js";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement, LineElement, ArcElement, Title, Tooltip, Legend } from "chart.js";
import { Bar, Line, Doughnut } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, ArcElement, Title, Tooltip, Legend);

export default function Trends() {
  const [myTrends, setMyTrends] = useState(null);
  const [emerging, setEmerging] = useState(null);
  const [tab, setTab] = useState("me");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    load();
  }, []);

  async function load() {
    setLoading(true);
    try {
      const [m, e] = await Promise.all([trendsAPI.my(), trendsAPI.emerging()]);
      setMyTrends(m.data);
      setEmerging(e.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div></div>;
  }

  const data = tab === "me" ? myTrends : emerging;

  const keywordsChart = {
    labels: (data?.trending_keywords || []).slice(0, 15).map((k) => k.keyword || k.technology),
    datasets: [
      {
        label: "Frequency",
        data: (data?.trending_keywords || []).slice(0, 15).map((k) => k.count || k.mentions),
        backgroundColor: "#3b82f6",
      },
    ],
  };

  const domainChart = {
    labels: (data?.domain_distribution || []).map((d) => d.domain),
    datasets: [
      {
        data: (data?.domain_distribution || []).map((d) => d.count),
        backgroundColor: ["#3b82f6", "#8b5cf6", "#ec4899", "#10b981", "#f59e0b", "#06b6d4", "#ef4444"],
      },
    ],
  };

  const growthChart = {
    labels: (data?.research_growth || []).map((g) => g.year),
    datasets: [
      {
        label: "Publications",
        data: (data?.research_growth || []).map((g) => g.publications),
        borderColor: "rgb(139, 92, 246)",
        backgroundColor: "rgba(139, 92, 246, 0.1)",
        tension: 0.4,
        fill: true,
      },
    ],
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">📈 Research Trend Intelligence</h1>
          <p className="text-slate-500 text-sm">Track emerging topics, domain distribution, and growth</p>
        </div>
        <div className="flex gap-2 bg-slate-100 rounded-lg p-1">
          <button
            onClick={() => setTab("me")}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition ${
              tab === "me" ? "bg-white text-primary-700 shadow" : "text-slate-600"
            }`}
          >
            My Trends
          </button>
          <button
            onClick={() => setTab("emerging")}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition ${
              tab === "emerging" ? "bg-white text-primary-700 shadow" : "text-slate-600"
            }`}
          >
            Platform Wide
          </button>
        </div>
      </div>

      {data?.trending_keywords && data.trending_keywords.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">
            {tab === "me" ? "My Top Trending Keywords" : "Platform-wide Emerging Keywords"}
          </h3>
          <Bar data={keywordsChart} options={{ indexAxis: "y", responsive: true }} />
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-6">
        {data?.domain_distribution && data.domain_distribution.length > 0 && (
          <div className="card">
            <h3 className="font-semibold text-slate-800 mb-4">Domain Distribution</h3>
            <Doughnut data={domainChart} />
          </div>
        )}
        {data?.research_growth && data.research_growth.length > 0 && (
          <div className="card">
            <h3 className="font-semibold text-slate-800 mb-4">Research Growth</h3>
            <Line data={growthChart} />
          </div>
        )}
      </div>

      {tab === "me" && data?.technology_evolution && data.technology_evolution.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">🚀 Technology Evolution (Recent)</h3>
          <div className="grid sm:grid-cols-3 gap-3">
            {data.technology_evolution.map((t) => (
              <div key={t.technology} className="p-3 bg-slate-50 rounded-lg">
                <div className="font-medium text-slate-800">{t.technology}</div>
                <div className="text-xs text-slate-500">{t.mentions} recent mentions</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {(!data?.trending_keywords || data.trending_keywords.length === 0) && (
        <div className="card text-center text-slate-500">
          No trend data available yet. {tab === "me" ? "Add publications to see your personal trends." : "Check back later."}
        </div>
      )}
    </div>
  );
}
