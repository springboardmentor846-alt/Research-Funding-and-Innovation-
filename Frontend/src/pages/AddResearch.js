import { useState } from "react";

function AddResearch() {
  const [title, setTitle] = useState("");
  const [researcher, setResearcher] = useState("");
  const [department, setDepartment] = useState("");
  const [researchArea, setResearchArea] = useState("");
  const [status, setStatus] = useState("");

  const saveResearch = () => {
    fetch("http://127.0.0.1:8000/research", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        title,
        researcher,
        department,
        research_area: researchArea,
        status,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        alert(data.message);
      })
      .catch((err) => console.log(err));
  };

  return (
    <div style={{ padding: "30px" }}>
      <h1>Add Research</h1>

      <input
        type="text"
        placeholder="Research Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      /><br /><br />

      <input
        type="text"
        placeholder="Researcher Name"
        value={researcher}
        onChange={(e) => setResearcher(e.target.value)}
      /><br /><br />

      <input
        type="text"
        placeholder="Department"
        value={department}
        onChange={(e) => setDepartment(e.target.value)}
      /><br /><br />

      <input
        type="text"
        placeholder="Research Area"
        value={researchArea}
        onChange={(e) => setResearchArea(e.target.value)}
      /><br /><br />

      <input
        type="text"
        placeholder="Status"
        value={status}
        onChange={(e) => setStatus(e.target.value)}
      /><br /><br />

      <button onClick={saveResearch}>Save</button>
    </div>
  );
}

export default AddResearch;