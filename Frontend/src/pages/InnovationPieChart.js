import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

import { Pie } from "react-chartjs-2";

ChartJS.register(ArcElement, Tooltip, Legend);

function InnovationPieChart({ dashboard }) {
  const data = {
    labels: [
      "Patents",
      "Technologies",
      "Innovations",
      "Commercialization",
    ],
    datasets: [
      {
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
        width: "400px",
        background: "white",
        padding: "20px",
        borderRadius: "10px",
        marginTop: "40px",
      }}
    >
      <h2>Distribution</h2>

      <Pie data={data} />
    </div>
  );
}

export default InnovationPieChart;