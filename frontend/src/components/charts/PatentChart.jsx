import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer
} from "recharts";

export default function PatentChart({ data }) {
  return (
    <div className="panel">
      <h2>Patent Trend</h2>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>

          <CartesianGrid strokeDasharray="3 3" />

          <XAxis dataKey="year" />

          <YAxis />

          <Tooltip />

          <Bar
            dataKey="count"
            fill="#10B981"
          />

        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}