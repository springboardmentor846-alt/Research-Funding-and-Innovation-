import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";

function PublicationChart({ data }) {

  return (

    <div style={{ width: "100%", height: 350 }}>

      <ResponsiveContainer>

        <LineChart data={data}>

          <CartesianGrid strokeDasharray="3 3"/>

          <XAxis dataKey="year"/>

          <YAxis/>

          <Tooltip/>

          <Line
            type="monotone"
            dataKey="total_publications"
            stroke="#2563eb"
            strokeWidth={3}
          />

        </LineChart>

      </ResponsiveContainer>

    </div>

  );

}

export default PublicationChart;