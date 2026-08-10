import { useState,useEffect } from "react";
function InnovationScoring() {
  const[search,setSearch]=useState("");
  
    const [innovations, setInnovations] = useState([]);

useEffect(() => {
  fetch("http://127.0.0.1:8000/innovation")
    .then((response) => response.json())
    .then((data) => setInnovations(data))
    .catch((error) => console.log(error));
}, []);
const handleDelete = async (id) => {
  try {
    await fetch(`http://127.0.0.1:8000/innovation/${id}`, {
      method: "DELETE",
    });

    setInnovations(
      innovations.filter((item) => item.id !== id)
    );

    alert("Innovation Deleted Successfully");
  } catch (error) {
    console.log(error);
    alert("Error deleting innovation");
  }
};
  return (
    <div style={{ padding: "30px" }}>
      <h1>Innovation Scoring</h1>
        <input
  type="text"
  placeholder="🔍 Search Innovation"
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
    <h3>Total Innovations</h3>
    <h2>{innovations.length}</h2>
  </div>

  <div style={{ background: "#198754", color: "white", padding: "20px", borderRadius: "10px", width: "180px" }}>
    <h3>Excellent</h3>
    <h2>{innovations.filter(i => i.level === "Excellent").length}</h2>
  </div>

  <div style={{ background: "#ffc107", color: "black", padding: "20px", borderRadius: "10px", width: "180px" }}>
    <h3>Very Good</h3>
    <h2>{innovations.filter(i => i.level === "Very Good").length}</h2>
  </div>

  <div style={{ background: "#0dcaf0", color: "black", padding: "20px", borderRadius: "10px", width: "180px" }}>
    <h3>Good</h3>
    <h2>{innovations.filter(i => i.level === "Good").length}</h2>
  </div>
</div>
      <table
        border="1"
        cellPadding="10"
        style={{ borderCollapse: "collapse", width: "100%" }}
      >
        <thead>
          <tr>
            <th>Innovation</th>
            <th>Score</th>
            <th>Level</th>
            <th>Action</th>
          </tr>
        </thead>
          <tbody>
  {innovations
    .filter((item) =>
      item.title.toLowerCase().includes(search.toLowerCase())
    )
    .map((item, index) => (
      <tr key={index}>
        <td>{item.title}</td>
        <td>{item.score}</td>
        <td>{item.level}</td>
        <td>
  <button
    onClick={() => handleDelete(item.id)}
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

export default InnovationScoring;