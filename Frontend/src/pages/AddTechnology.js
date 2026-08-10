import { useState } from "react";
import { useNavigate } from "react-router-dom";

function AddTechnology() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [patents, setPatents] = useState("");

  const handleSave = async () => {
    if (!name || !patents) {
      alert("Please fill all fields");
      return;
    }

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/technology",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: name,
            patents: Number(patents),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        alert("Error saving technology");
        return;
      }

      alert(
        `Technology Saved!\nTrend: ${data.trend}`
      );

      navigate("/technology-intelligence");

    } catch (error) {
      console.log(error);
      alert("Error connecting to backend");
    }
  };

  return (
    <div style={{ padding: "30px" }}>
      <h1>➕ Add Technology</h1>

      <input
        type="text"
        placeholder="Technology Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        style={{
          padding: "10px",
          width: "300px"
        }}
      />

      <br />
      <br />

      <input
        type="number"
        placeholder="Number of Patents"
        value={patents}
        onChange={(e) => setPatents(e.target.value)}
        style={{
          padding: "10px",
          width: "300px"
        }}
      />

      <br />
      <br />

      <button
        onClick={handleSave}
        style={{
          padding: "10px 20px",
          background: "#0d6efd",
          color: "white",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer"
        }}
      >
        Save Technology
      </button>
    </div>
  );
}

export default AddTechnology;