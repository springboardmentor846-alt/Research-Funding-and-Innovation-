import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function ResearchChart() {
  const data = {
    labels: ["2021", "2022", "2023", "2024", "2025"],
    datasets: [
      {
        label: "Research Projects",
        data: [20, 40, 60, 90, 120],
        borderColor: "blue",
      },
    ],
  };

  return (
    <div style={{ width: "700px" }}>
      <Line data={data} />
    </div>
  );
}

export default ResearchChart;