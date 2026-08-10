import { useState, useEffect } from "react";
import InnovationChart from "./InnovationChart";
import InnovationPieChart from "./InnovationPieChart";

function InnovationDashboard() {
  const [dashboard, setDashboard] = useState({
    patents: 0,
    technologies: 0,
    innovations: 0,
    commercialization: 0,
  });

  useEffect(() => {
    fetch("http://127.0.0.1:8000/innovation-dashboard")
      .then((res) => res.json())
      .then((data) => setDashboard(data))
      .catch((err) => console.log(err));
  }, []);

  return (
    <div style={{ padding: "30px" }}>
      <h1>Innovation Intelligence Dashboard</h1>

      {/* Dashboard Cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "20px",
          marginTop: "30px",
        }}
      >
        <div
          style={{
            background: "#0d6efd",
            color: "white",
            padding: "20px",
            borderRadius: "10px",
            textAlign: "center",
          }}
        >
          <h3>Total Patents</h3>
          <h2>{dashboard.patents}</h2>
        </div>

        <div
          style={{
            background: "#198754",
            color: "white",
            padding: "20px",
            borderRadius: "10px",
            textAlign: "center",
          }}
        >
          <h3>Technologies</h3>
          <h2>{dashboard.technologies}</h2>
        </div>

        <div
          style={{
            background: "#ffc107",
            color: "black",
            padding: "20px",
            borderRadius: "10px",
            textAlign: "center",
          }}
        >
          <h3>Innovations</h3>
          <h2>{dashboard.innovations}</h2>
        </div>

        <div
          style={{
            background: "#dc3545",
            color: "white",
            padding: "20px",
            borderRadius: "10px",
            textAlign: "center",
          }}
        >
          <h3>Commercialization</h3>
          <h2>{dashboard.commercialization}</h2>
        </div>
      </div>

      {/* Charts */}
      <div
        style={{
          display: "flex",
          gap: "30px",
          marginTop: "40px",
          flexWrap: "wrap",
          justifyContent: "center",
        }}
      >
        <InnovationChart dashboard={dashboard} />
        <InnovationPieChart dashboard={dashboard} />
      </div>

      {/* Recent Activity */}
      <div
        style={{
          marginTop: "40px",
          background: "white",
          padding: "20px",
          borderRadius: "10px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
        }}
      >
        <h2>Recent Activity</h2>

        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            marginTop: "15px",
          }}
        >
          <thead>
            <tr style={{ background: "#f5f5f5" }}>
              <th style={{ padding: "10px", border: "1px solid #ddd" }}>
                Module
              </th>
              <th style={{ padding: "10px", border: "1px solid #ddd" }}>
                Status
              </th>
              <th style={{ padding: "10px", border: "1px solid #ddd" }}>
                Description
              </th>
            </tr>
          </thead>

          <tbody>
            <tr>
              <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                Patent
              </td>
              <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                ✔ Added
              </td>
              <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                Patent record saved successfully
              </td>
            </tr>

            <tr>
              <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                Technology
              </td>
              <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                ✔ Added
              </td>
              <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                Technology information updated
              </td>
            </tr>

            <tr>
              <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                Innovation
              </td>
              <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                ✔ Added
              </td>
              <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                Innovation score recorded
              </td>
            </tr>

            <tr>
              <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                Commercialization
              </td>
              <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                ✔ Added
              </td>
              <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                Recommendation generated
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default InnovationDashboard;