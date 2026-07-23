import { useEffect, useState } from "react";
import api from "../api/api";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

import { Bar } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function PublicationTrends() {
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTrends();
  }, []);

  const loadTrends = async () => {
    try {
      const res = await api.get("/analytics/publication-trends");
      setTrends(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const data = {
    labels: trends.map((t) => t.year),
    datasets: [
      {
        label: "Publications",
        data: trends.map((t) => t.count),
        backgroundColor: "rgba(37,99,235,0.8)",
        borderColor: "rgba(37,99,235,1)",
        borderWidth: 2,
        borderRadius: 8,
        hoverBackgroundColor: "rgba(29,78,216,1)",
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top",
      },
      title: {
        display: true,
        text: "Publications by Year",
        font: {
          size: 18,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          precision: 0,
          stepSize: 1,
        },
        title: {
          display: true,
          text: "Number of Publications",
        },
      },
      x: {
        title: {
          display: true,
          text: "Publication Year",
        },
      },
    },
  };

  if (loading) {
    return (
      <div className="container">
        <h2>Publication Trend Analysis</h2>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="container">
      <h2 style={{ marginBottom: "25px" }}>Publication Trend Analysis</h2>

      <div
        style={{
          background: "#fff",
          padding: "25px",
          borderRadius: "12px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
          height: "500px",
        }}
      >
        <Bar data={data} options={options} />
      </div>
    </div>
  );
}