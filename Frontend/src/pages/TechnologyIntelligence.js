import { useState,useEffect } from "react";
function TechnologyIntelligence() {
  const[search,setSearch]=useState("");
 const [technologies, setTechnologies] = useState([]);

useEffect(() => {
  fetch("http://127.0.0.1:8000/technology")
    .then((response) => response.json())
    .then((data) => setTechnologies(data))
    .catch((error) => console.log(error));
}, []);
const handleDelete = async (id) => {
  try {
    await fetch(`http://127.0.0.1:8000/technology/${id}`, {
      method: "DELETE",
    });

    setTechnologies(
      technologies.filter((technology) => technology.id !== id)
    );

    alert("Technology Deleted Successfully");
  } catch (error) {
    console.log(error);
    alert("Error deleting technology");
  }
};
  return (
    <div style={{ padding: "30px" }}>
      <h1>Technology Intelligence</h1>
      <input
  type="text"
  placeholder="🔍 Search Technology"
  value={search}
  onChange={(e) => setSearch(e.target.value)}
  style={{
    padding: "10px",
    width: "300px",
    marginBottom: "20px",
    borderRadius: "5px",
    border: "1px solid #ccc",
  }}
/>
<div
  style={{
    display: "flex",
    gap: "20px",
    marginBottom: "30px",
    flexWrap: "wrap",
  }}
>
  <div style={{ background: "#0d6efd", color: "white", padding: "20px", borderRadius: "10px", width: "180px" }}>
    <h3>Total Technologies</h3>
    <h2>{technologies.length}</h2>
  </div>

  <div style={{ background: "#198754", color: "white", padding: "20px", borderRadius: "10px", width: "180px" }}>
    <h3>High Growth</h3>
    <h2>{technologies.filter(t => t.trend === "High Growth").length}</h2>
  </div>

  <div style={{ background: "#ffc107", color: "black", padding: "20px", borderRadius: "10px", width: "180px" }}>
    <h3>Growing</h3>
    <h2>{technologies.filter(t => t.trend === "Growing").length}</h2>
  </div>

  <div style={{ background: "#0dcaf0", color: "black", padding: "20px", borderRadius: "10px", width: "180px" }}>
    <h3>Emerging</h3>
    <h2>{technologies.filter(t => t.trend === "Emerging").length}</h2>
  </div>
</div>
      <table
        border="1"
        cellPadding="10"
        style={{ borderCollapse: "collapse", width: "100%" }}
      >
        <thead>
          <tr>
            <th>Technology</th>
            <th>Patent Count</th>
            <th>Trend</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
          {technologies
  .filter((tech) =>
    tech.name.toLowerCase().includes(search.toLowerCase())
  )
  .map((tech, index) => (
            <tr key={index}>
              <td>{tech.name}</td>
              <td>{tech.patents}</td>
              <td>
  <span
    style={{
      background:
        tech.trend === "High Growth"
          ? "#198754"
          : tech.trend === "Growing"
          ? "#ffc107"
          : "#0d6efd",
      color: tech.trend === "Growing" ? "black" : "white",
      padding: "6px 12px",
      borderRadius: "20px",
      fontWeight: "bold",
    }}
  >
    {tech.trend}
  </span>
</td>
<td>
  <button
    onClick={() => handleDelete(tech.id)}
    style={{
      backgroundColor: "#dc3545",
      color: "white",
      border: "none",
      padding: "8px 15px",
      borderRadius: "5px",
      cursor: "pointer",
    }}
  >
    Delete
  </button>
</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TechnologyIntelligence;