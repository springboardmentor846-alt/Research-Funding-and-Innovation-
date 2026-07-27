
import { useState } from "react";

function Recommendation() {
  const [researchArea, setResearchArea] = useState("");
  const [grants, setGrants] = useState([]);

  function getRecommendation() {
    if (researchArea === "") {
      alert("Please enter a research area");
      return;
    }

    fetch(`http://127.0.0.1:8000/recommend/${researchArea}`)
      .then((res) => res.json())
      .then((data) => setGrants(data))
      .catch((err) => console.log(err));
  }

  return (
    <div style={{ padding: "20px" }}>
      <h1>Funding Recommendation Engine</h1>

      <input
        type="text"
        placeholder="Enter Research Area"
        value={researchArea}
        onChange={(e) => setResearchArea(e.target.value)}
        style={{
          padding: "10px",
          width: "250px",
          marginRight: "10px",
        }}
      />

      <button
        onClick={getRecommendation}
        style={{
          padding: "10px 20px",
          cursor: "pointer",
        }}
      >
        Get Recommendation
      </button>

      <div style={{ marginTop: "30px" }}>
        {grants.map((item, index) => (
          <div
            key={index}
            style={{
              border: "1px solid gray",
              borderRadius: "8px",
              padding: "15px",
              marginBottom: "15px",
            }}
          >
            <h3>{item.grant}</h3>
            <p>
              <b>Agency:</b> {item.agency}
            </p>
            <p>
              <b>Amount:</b> {item.amount}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Recommendation;