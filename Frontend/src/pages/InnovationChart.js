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

function InnovationChart({ dashboard }) {
  const data = {
    labels: [
      "Patents",
      "Technologies",
      "Innovations",
      "Commercialization",
    ],
    datasets: [
      {
        label: "Total Count",
        data: [
          dashboard.patents,
          dashboard.technologies,
          dashboard.innovations,
          dashboard.commercialization,
        ],
        backgroundColor: [
          "#0d6efd",
          "#198754",
          "#ffc107",
          "#dc3545",
        ],
      },
    ],
  };

  return (
    <div
      style={{
        width: "700px",
        marginTop: "40px",
        background: "white",
        padding: "20px",
        borderRadius: "10px",
      }}
    >
      <h2>Innovation Analytics</h2>

      <Bar data={data} />
    </div>
  );
}

export default InnovationChart;