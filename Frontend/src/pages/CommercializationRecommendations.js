import { useState, useEffect } from "react";

function CommercializationRecommendations() {
  const [search, setSearch] = useState("");
  const [commercializations, setCommercializations] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/commercialization")
      .then((response) => response.json())
      .then((data) => setCommercializations(data))
      .catch((error) => console.log(error));
  }, []);

  const handleDelete = async (id) => {
    try {
      await fetch(`http://127.0.0.1:8000/commercialization/${id}`, {
        method: "DELETE",
      });

      setCommercializations(
        commercializations.filter((item) => item.id !== id)
      );

      alert("Deleted Successfully");
    } catch (error) {
      console.log(error);
      alert("Error deleting");
    }
  };

  const high = commercializations.filter(
    (item) => item.market_potential === "High"
  ).length;

  const medium = commercializations.filter(
    (item) => item.market_potential === "Medium"
  ).length;

  const low = commercializations.filter(
    (item) => item.market_potential === "Low"
  ).length;

  return (
    <div style={{ padding: "30px" }}>
      <h1>Commercialization Recommendations</h1>

      <input
        type="text"
        placeholder="🔍 Search Technology"
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
        <div
          style={{
            background: "#0d6efd",
            color: "white",
            padding: "20px",
            borderRadius: "10px",
            width: "180px",
          }}
        >
          <h3>Total Technologies</h3>
          <h2>{commercializations.length}</h2>
        </div>

        <div
          style={{
            background: "#198754",
            color: "white",
            padding: "20px",
            borderRadius: "10px",
            width: "180px",
          }}
        >
          <h3>High Potential</h3>
          <h2>{high}</h2>
        </div>

        <div
          style={{
            background: "#ffc107",
            color: "black",
            padding: "20px",
            borderRadius: "10px",
            width: "180px",
          }}
        >
          <h3>Medium Potential</h3>
          <h2>{medium}</h2>
        </div>

        <div
          style={{
            background: "#6c757d",
            color: "white",
            padding: "20px",
            borderRadius: "10px",
            width: "180px",
          }}
        >
          <h3>Low Potential</h3>
          <h2>{low}</h2>
        </div>
      </div>

      <table
        border="1"
        cellPadding="10"
        style={{
          borderCollapse: "collapse",
          width: "100%",
        }}
      >
        <thead>
          <tr>
            <th>Technology</th>
            <th>Market Potential</th>
            <th>Recommendation</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
          {commercializations
            .filter((item) =>
              item.title.toLowerCase().includes(search.toLowerCase())
            )
            .map((item) => (
              <tr key={item.id}>
                <td>{item.title}</td>
                <td>{item.market_potential}</td>
                <td>{item.recommendation}</td>

                <td>
                  <button
                    onClick={() => handleDelete(item.id)}
                    style={{
                      background: "#dc3545",
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

export default CommercializationRecommendations;