import { useEffect, useState } from "react";
import axios from "axios";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

export default function PatentChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/patents/")
      .then((res) => {
        // Count patents by technology domain
        const counts = {};

        res.data.forEach((patent) => {
          const domain = patent.technology_domain;

          counts[domain] = (counts[domain] || 0) + 1;
        });

        const chartData = Object.keys(counts).map((key) => ({
          domain: key,
          patents: counts[key],
        }));

        setData(chartData);
      })
      .catch(console.error);
  }, []);

  return (
    <div className="mt-8 bg-slate-900 border border-slate-700 rounded-2xl shadow-xl p-6">

      <div className="flex justify-between items-center mb-6">

        <div>
          <h2 className="text-2xl font-bold text-white">
            Patent Distribution
          </h2>

          <p className="text-slate-400">
            Patents grouped by technology domain
          </p>
        </div>

      </div>

      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={data}>

          <CartesianGrid
            stroke="#334155"
            strokeDasharray="4 4"
          />

          <XAxis
            dataKey="domain"
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
            }}
          />

          <Bar
            dataKey="patents"
            fill="#06b6d4"
            radius={[8, 8, 0, 0]}
          />

        </BarChart>
      </ResponsiveContainer>

    </div>
  );
}