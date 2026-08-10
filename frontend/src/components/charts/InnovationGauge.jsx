import {
  RadialBarChart,
  RadialBar,
  PolarAngleAxis,
  ResponsiveContainer
} from "recharts";

export default function InnovationGauge({ score }) {

  const data = [
    {
      name: "Innovation",
      value: score,
      fill: "#4F46E5"
    }
  ];

  return (

    <div className="panel">

      <h2>Innovation Score</h2>

      <ResponsiveContainer width="100%" height={300}>

        <RadialBarChart
          innerRadius="70%"
          outerRadius="100%"
          data={data}
          startAngle={180}
          endAngle={0}
        >

          <PolarAngleAxis
            type="number"
            domain={[0, 100]}
            tick={false}
          />

          <RadialBar
            background
            dataKey="value"
          />

        </RadialBarChart>

      </ResponsiveContainer>

      <h1
        style={{
          textAlign: "center"
        }}
      >
        {score}/100
      </h1>

    </div>

  );

}