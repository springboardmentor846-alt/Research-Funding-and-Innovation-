import { useState, useEffect } from "react";

function ResearchProfile() {
  const [name, setName] = useState("");
  const [department, setDepartment] = useState("");
  const [researchArea, setResearchArea] = useState("");
  const [email, setEmail] = useState("");

  const [profiles, setProfiles] = useState([]);

  useEffect(() => {
    loadProfiles();
  }, []);

  const loadProfiles = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/profiles");
      const data = await response.json();
      setProfiles(data);
    } catch (error) {
      console.log(error);
    }
  };

  const handleSubmit = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/profile", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          department,
          research_area: researchArea,
          email,
        }),
      });

      const data = await response.json();
      alert(data.message);

      setName("");
      setDepartment("");
      setResearchArea("");
      setEmail("");

      loadProfiles();

    } catch (error) {
      console.log(error);
      alert("Error saving profile");
    }
  };

  const handleDelete = async (id) => {
    try {
      await fetch(`http://127.0.0.1:8000/profile/${id}`, {
        method: "DELETE",
      });

      alert("Profile Deleted Successfully");

      loadProfiles();

    } catch (error) {
      console.log(error);
      alert("Error deleting profile");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Research Profile</h1>

      <div style={{ width: "400px" }}>
        <label>Name</label>
        <br />
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter Name"
        />

        <br /><br />

        <label>Department</label>
        <br />
        <input
          type="text"
          value={department}
          onChange={(e) => setDepartment(e.target.value)}
          placeholder="Enter Department"
        />

        <br /><br />

        <label>Research Area</label>
        <br />
        <input
          type="text"
          value={researchArea}
          onChange={(e) => setResearchArea(e.target.value)}
          placeholder="Enter Research Area"
        />

        <br /><br />

        <label>Email</label>
        <br />
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter Email"
        />

        <br /><br />

        <button onClick={handleSubmit}>
          Save Profile
        </button>
      </div>

      <hr />

      <h2>Saved Research Profiles</h2>

      <table
        border="1"
        cellPadding="10"
        style={{
          width: "100%",
          marginTop: "20px",
          borderCollapse: "collapse",
        }}
      >
        <thead>
          <tr>
            <th>Name</th>
            <th>Department</th>
            <th>Research Area</th>
            <th>Email</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
          {profiles.map((profile) => (
            <tr key={profile.id}>
              <td>{profile.name}</td>
              <td>{profile.department}</td>
              <td>{profile.research_area}</td>
              <td>{profile.email}</td>
              <td>
                <button
                  onClick={() => handleDelete(profile.id)}
                  style={{
                    background: "red",
                    color: "white",
                    border: "none",
                    padding: "5px 10px",
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

export default ResearchProfile;