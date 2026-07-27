import { useState } from "react";

function GrantMatching() {
  const [researchArea, setResearchArea] = useState("");
  const [grants, setGrants] = useState([]);

  const searchGrant = async () => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/match/${researchArea}`
      );

      const data = await response.json();
      setGrants(data);
    } catch (error) {
      console.log(error);
      alert("Error fetching grants");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Grant Matching Workflow</h1>

      <input
        type="text"
        placeholder="Enter Research Area"
        value={researchArea}
        onChange={(e) => setResearchArea(e.target.value)}
      />

      <button
        onClick={searchGrant}
        style={{ marginLeft: "10px" }}
      >
        Search
      </button>

      <br /><br />

      {grants.map((grant) => (
        <div
          key={grant.id}
          style={{
            border: "1px solid gray",
            padding: "10px",
            marginBottom: "10px",
          }}
        >
          <h3>{grant.title}</h3>
          <p><b>Research Field:</b> {grant.research_field}</p>
          <p><b>Funding:</b> ₹{grant.funding_amount}</p>
          <p><b>Eligibility:</b> {grant.eligibility}</p>
          <p>{grant.description}</p>
        </div>
      ))}
    </div>
  );
}

export default GrantMatching;