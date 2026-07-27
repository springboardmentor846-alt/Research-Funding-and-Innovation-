import { useNavigate} from "react-router-dom";
import { useState,useEffect } from "react";
function Patents() {
    const navigate = useNavigate();

const [patents, setPatents] = useState([]);

useEffect(() => {
  fetch("http://127.0.0.1:8000/patent")
    .then((res) => res.json())
    .then((data) => setPatents(data))
    .catch((err) => console.log(err));
}, []);
const deletePatent = (id) => {
  fetch(`http://127.0.0.1:8000/patent/${id}`, {
    method: "DELETE",
  })
    .then((res) => res.json())
    .then((data) => {
      alert(data.message);
      window.location.reload();
    })
    .catch((err) => console.log(err));
};
  return (
    <div style={{ padding: "30px", background: "#f4f6f9", minHeight: "100vh" }}>
      <h1>Patents</h1>
       <button
  onClick={() => navigate("/add-patent")}
  style={{
    background: "#198754",
    color: "white",
    border: "none",
    padding: "10px 20px",
    borderRadius: "5px",
    cursor: "pointer",
    marginBottom: "20px",
  }}
>
  + Add Patent
</button>
      {patents.map((patent, index) => (
        <div
          key={index}
          style={{
            background: "white",
            padding: "20px",
            marginBottom: "20px",
            borderRadius: "10px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
          }}
        >
          <h2 style={{ color: "#0d6efd" }}>{patent.title}</h2>

          <p><b>Inventor:</b> {patent.inventor}</p>

          <p><b>Patent ID:</b> {patent.patentId}</p>

          <p><b>Status:</b> {patent.status}</p>

          <button
            onClick={() => navigate(`/patents/${index}`)}
            style={{
            background: "#0d6efd",
            color: "white",
            border: "none",
            padding: "10px 20px",
            borderRadius: "5px",
            cursor: "pointer",
             }}
            >
  View Details
</button>
<button
  onClick={() => deletePatent(patent.id)}
  style={{
    background: "red",
    color: "white",
    border: "none",
    padding: "10px 20px",
    borderRadius: "5px",
    cursor: "pointer",
    marginLeft: "10px",
  }}
>
  Delete
</button>
        </div>
      ))}
    </div>
  );
}

export default Patents;
