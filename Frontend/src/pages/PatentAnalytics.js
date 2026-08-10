import { useState, useEffect } from "react";
import { Pie } from "react-chartjs-2";

import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);
function PatentAnalytics() {
  const [patents, setPatents] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/patent")
      .then((response) => response.json())
      .then((data) => setPatents(data))
      .catch((error) => console.log(error));
  }, []);

  const total = patents.length;
  const filed = patents.filter((p) => p.status === "Filed").length;
  const granted = patents.filter((p) => p.status === "Granted").length;
  const review = patents.filter((p) => p.status === "Ongoing").length;
  const chartData = {
  labels: ["Filed", "Granted", "Under Review"],
  datasets: [
    {
      data: [filed, granted, review],
      backgroundColor: [
        "#198754",
        "#ffc107",
        "#dc3545",
      ],
    },
  ],
};
  return (
    <div style={{ padding: "30px" }}>
      <h1>Patent Analytics</h1>
       <div
  style={{
    display: "flex",
    gap: "20px",
    marginTop: "30px",
    flexWrap: "wrap",
  }}
>
  <div
    style={{
      background: "#0d6efd",
      color: "white",
      padding: "20px",
      borderRadius: "10px",
      width: "200px",
    }}
  >
    <h3>Total Patents</h3>
    <h2>{total}</h2>
  </div>

  <div
    style={{
      background: "#198754",
      color: "white",
      padding: "20px",
      borderRadius: "10px",
      width: "200px",
    }}
  >
    <h3>Filed</h3>
    <h2>{filed}</h2>
  </div>

  <div
    style={{
      background: "#ffc107",
      color: "black",
      padding: "20px",
      borderRadius: "10px",
      width: "200px",
    }}
  >
    <h3>Granted</h3>
    <h2>{granted}</h2>
  </div>

  <div
    style={{
      background: "#dc3545",
      color: "white",
      padding: "20px",
      borderRadius: "10px",
      width: "200px",
    }}
  >
    <h3>Under Review</h3>
    <h2>{review}</h2>
  </div>
  <h2 style={{ marginTop: "40px" }}>Patent Status Distribution</h2>
   <div style={{ width: "400px" }}>
       <Pie data={chartData} />
     </div>
     <h2 style={{ marginTop: "40px" }}>📋 Patent Status Summary</h2>

<table
  border="1"
  cellPadding="10"
  style={{
    width: "500px",
    borderCollapse: "collapse",
    marginTop: "20px",
    textAlign: "center",
  }}
>
  <thead style={{ backgroundColor: "#0d6efd", color: "white" }}>
    <tr>
      <th>Status</th>
      <th>Count</th>
    </tr>
  </thead>

  <tbody>
    <tr>
      <td>Filed</td>
      <td>{filed}</td>
    </tr>

    <tr>
      <td>Granted</td>
      <td>{granted}</td>
    </tr>

    <tr>
      <td>Under Review</td>
      <td>{review}</td>
    </tr>
  </tbody>
</table>
<h2 style={{ marginTop: "40px" }}>📝 Recent Patents</h2>

<table
  border="1"
  cellPadding="10"
  style={{
    width: "100%",
    borderCollapse: "collapse",
    marginTop: "20px",
    textAlign: "center",
  }}
>
  <thead style={{ backgroundColor: "#198754", color: "white" }}>
    <tr>
      <th>Title</th>
      <th>Inventor</th>
      <th>Patent ID</th>
      <th>Status</th>
    </tr>
  </thead>

  <tbody>
    {patents.map((patent) => (
      <tr key={patent.id}>
        <td>{patent.title}</td>
        <td>{patent.inventor}</td>
        <td>{patent.patent_id}</td>
        <td>{patent.status}</td>
      </tr>
    ))}
  </tbody>
</table>
     </div>
     </div>
  );
}

export default PatentAnalytics;