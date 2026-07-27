import { useNavigate } from "react-router-dom";
import { useState,useEffect } from "react";
function Research() {
  const navigate = useNavigate();
  const deleteResearch = (id) => {

  fetch(`http://127.0.0.1:8000/research/${id}`, {
    method: "DELETE",
  })
  .then(res => res.json())
  .then(data => {
    alert(data.message);

    // list refresh
    window.location.reload();
  })
  .catch(error => console.log(error));

};
  const [projects, setProjects] = useState([]);

useEffect(() => {

 fetch("http://127.0.0.1:8000/research")
 .then((response)=>response.json())
 .then((data)=>{
    setProjects(data);
 })
 .catch((error)=>console.log(error));

},[]);
  return (
    <div style={{ padding: "30px", background: "#f4f6f9", minHeight: "100vh" }}>
      <h1 style={{ marginBottom: "20px" }}>Research Projects</h1>
      <button
        onClick={() => navigate("/add-research")}
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
  + Add Research
</button>
      {projects.map((project) => (
        <div
          key={project.id}
          style={{
            background: "white",
            padding: "20px",
            marginBottom: "20px",
            borderRadius: "10px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
          }}
        >
          <h2 style={{ color: "#0d6efd" }}>{project.title}</h2>

          <p><b>Researcher:</b> {project.researcher}</p>

          <p><b>Department:</b> {project.department}</p>

          <p><b>Status:</b> {project.status}</p>

          <button
           onClick={() => navigate("/research-details")}
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
  onClick={() => deleteResearch(project.id)}
  style={{
    background: "red",
    color: "white",
    border: "none",
    padding: "10px 20px",
    borderRadius: "5px",
    cursor: "pointer",
    marginLeft: "10px"
  }}
>
  Delete
</button>
        </div>
      ))}
    </div>
  );
}

export default Research;