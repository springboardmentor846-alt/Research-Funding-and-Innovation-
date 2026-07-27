import { useEffect, useState } from "react";

function Funding() {
  const [grants, setGrants] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/grants")
      .then((response) => response.json())
      .then((data) => {console.log(data);setGrants(data);})
      .catch((error) => console.log(error));
  }, []);

  return (
    <div style={{ padding: "30px" }}>
      <h1>Funding Opportunities</h1>

      <table border="1" cellPadding="10" style={{ width: "100%" }}>
        <thead>
          <tr>
            <th>Title</th>
            <th>Research Field</th>
            <th>Funding Amount</th>
            <th>Eligibility</th>
          </tr>
        </thead>

        <tbody>
          {grants.map((grant) => (
            <tr key={grant.id}>
              <td>{grant.title}</td>
              <td>{grant.research_field}</td>
              <td>₹{grant.funding_amount}</td>
              <td>{grant.eligibility}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Funding;