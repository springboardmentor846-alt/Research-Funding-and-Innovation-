import { useState, useEffect } from "react";
import ResearchChart from "../components/ResearchChart";

function Dashboard() {
 const [funding, setFunding] = useState([]);
const [dashboard, setDashboard] = useState({
  researchers: 0,
  grants: 0,
  publications: 0,
  patents: 0,
});
useEffect(() => {
  fetch("http://127.0.0.1:8000/dashboard")
    .then((response) => response.json())
    .then((data) => setDashboard(data))
    .catch((error) => console.log(error));

  fetch("http://127.0.0.1:8000/funding")
    .then((response) => response.json())
    .then((data) => setFunding(data))
    .catch((error) => console.log(error));
}, []);
 
  return (
    <div style={{ padding: "20px" }}>
      <h1>Research Funding & Innovation Platform</h1>

      <div
        style={{
          display: "flex",
          gap: "20px",
          marginTop: "30px",
        }}
      >
        <div
          style={{
            background: "#f5f5f5",
            padding: "20px",
            borderRadius: "10px",
            width: "200px",
          }}
        >
          <h3>Researchers</h3>
          <h2>{dashboard.researchers}</h2>
        </div>

        <div
          style={{
            background: "#f5f5f5",
            padding: "20px",
            borderRadius: "10px",
            width: "200px",
          }}
        >
          <h3>Grants</h3>
          <h2>{dashboard.grants}</h2>
        </div>

        <div
          style={{
            background: "#f5f5f5",
            padding: "20px",
            borderRadius: "10px",
            width: "200px",
          }}
        >
          <h3>Publications</h3>
          <h2>{dashboard.publications}</h2>
        </div>
      </div>

      <h2 style={{ marginTop: "40px" }}>Funding Opportunities</h2>

      <table
        style={{
          width: "80%",
          borderCollapse: "collapse",
          marginTop: "10px",
        }}
      >
        <thead>
          <tr>
            <th style={{ border: "1px solid black", padding: "10px" }}>
              Agency
            </th>
            <th style={{ border: "1px solid black", padding: "10px" }}>
              Grant
            </th>
            <th style={{ border: "1px solid black", padding: "10px" }}>
              Amount
            </th>
          </tr>
        </thead>

        <tbody>
          {funding.map((item, index) => (
            <tr key={index}>
              <td style={{ border: "1px solid black", padding: "10px" }}>
                {item.agency}
              </td>
              <td style={{ border: "1px solid black", padding: "10px" }}>
                {item.grant}
              </td>
              <td style={{ border: "1px solid black", padding: "10px" }}>
                {item.amount}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2 style={{ marginTop: "40px" }}>Research Trends</h2>

      <ResearchChart />
    </div>
  );
}

export default Dashboard;
