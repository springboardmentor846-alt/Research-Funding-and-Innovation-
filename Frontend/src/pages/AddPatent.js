import { useState } from "react";
import { useNavigate } from "react-router-dom";

function AddPatent() {
  const navigate = useNavigate();

  const [title, setTitle] = useState("");
  const [inventor, setInventor] = useState("");
  const [patentId, setPatentId] = useState("");
  const [status, setStatus] = useState("");

  const handleSave = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/patent", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title,
          inventor,
          patent_id: patentId,
          status,
        }),
      });

      const data = await response.json();
      alert(data.message);
      navigate("/patents");
    } catch (error) {
      console.log(error);
      alert("Error saving patent");
    }
  };

  return (
    <div style={{ padding: "30px" }}>
      <h1>Add Patent</h1>

      <input
        type="text"
        placeholder="Patent Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <br /><br />

      <input
        type="text"
        placeholder="Inventor Name"
        value={inventor}
        onChange={(e) => setInventor(e.target.value)}
      />
      <br /><br />

      <input
        type="text"
        placeholder="Patent ID"
        value={patentId}
        onChange={(e) => setPatentId(e.target.value)}
      />
      <br /><br />

      <input
        type="text"
        placeholder="Status"
        value={status}
        onChange={(e) => setStatus(e.target.value)}
      />
      <br /><br />

      <button onClick={handleSave}>Save</button>
    </div>
  );
}

export default AddPatent;