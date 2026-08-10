import { useState } from "react";
import { useNavigate } from "react-router-dom";

function AddInnovation() {
  const navigate = useNavigate();

  const [title, setTitle] = useState("");
  const [patents, setPatents] = useState("");
  const [trend, setTrend] = useState("");
  const [marketPotential, setMarketPotential] = useState("");

  const handleSave = async () => {
    if (!title || !patents || !trend || !marketPotential) {
      alert("Please fill all fields");
      return;
    }

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/innovation",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            title: title,
            patents: Number(patents),
            trend: trend,
            market_potential: marketPotential,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        alert("Error saving innovation");
        return;
      }

      alert(
        `Innovation Saved!\nScore: ${data.score}\nLevel: ${data.level}`
      );

      navigate("/innovation-scoring");
    } catch (error) {
      console.log(error);
      alert("Error connecting to backend");
    }
  };

  return (
    <div style={{ padding: "30px" }}>
      <h1>➕ Add Innovation</h1>

      {/* Innovation Title */}
      <input
        type="text"
        placeholder="Innovation Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        style={{
          padding: "10px",
          width: "300px",
        }}
      />

      <br />
      <br />

      {/* Patent Count */}
      <input
        type="number"
        placeholder="Patent Count"
        value={patents}
        onChange={(e) => setPatents(e.target.value)}
        style={{
          padding: "10px",
          width: "300px",
        }}
      />

      <br />
      <br />

      {/* Technology Trend */}
      <select
        value={trend}
        onChange={(e) => setTrend(e.target.value)}
        style={{
          padding: "10px",
          width: "325px",
        }}
      >
        <option value="">Select Technology Trend</option>
        <option value="Growing">Growing</option>
        <option value="Stable">Stable</option>
        <option value="Declining">Declining</option>
      </select>

      <br />
      <br />

      {/* Market Potential */}
      <select
        value={marketPotential}
        onChange={(e) => setMarketPotential(e.target.value)}
        style={{
          padding: "10px",
          width: "325px",
        }}
      >
        <option value="">Select Market Potential</option>
        <option value="High">High</option>
        <option value="Medium">Medium</option>
        <option value="Low">Low</option>
      </select>

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
          cursor: "pointer",
        }}
      >
        Calculate & Save Innovation
      </button>
    </div>
  );
}

export default AddInnovation;