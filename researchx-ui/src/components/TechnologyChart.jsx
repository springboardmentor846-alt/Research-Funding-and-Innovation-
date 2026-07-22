import { useEffect, useState } from "react";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function TechnologyChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/technologies/")
      .then((res) => {
        const chartData = res.data.map((tech) => ({
          name: tech.technology_name,
          score: tech.growth_score,
        }));

        setData(chartData);
      })
      .catch((err) => {
        console.error("Error loading technologies:", err);
      });
  }, []);

  return (
    <div className="mt-8 bg-slate-900 border border-slate-700 rounded-2xl shadow-xl p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white">
            Technology Growth Analysis
          </h2>

          <p className="text-slate-400">
            Live technology data from backend
          </p>
        </div>

        <div className="bg-cyan-500/20 text-cyan-400 px-4 py-2 rounded-lg font-semibold">
          LIVE
        </div>
      </div>

      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={data}>
          <CartesianGrid
            stroke="#334155"
            strokeDasharray="4 4"
          />

          <XAxis
            dataKey="name"
            stroke="#94a3b8"
          />

          <YAxis
            stroke="#94a3b8"
          />

          <Tooltip
            contentStyle={{
              backgroundColor: "#0f172a",
              border: "1px solid #334155",
              borderRadius: "10px",
              color: "#fff",
            }}
          />

          <Line
            type="monotone"
            dataKey="score"
            stroke="#06b6d4"
            strokeWidth={4}
            dot={{
              r: 6,
              fill: "#06b6d4",
            }}
            activeDot={{
              r: 8,
            }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}