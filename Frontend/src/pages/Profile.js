function Profile() {
  return (
    <div style={{ padding: "20px" }}>
      <h1>User Profile</h1>

      <div
        style={{
          background: "#f5f5f5",
          padding: "20px",
          borderRadius: "10px",
          width: "300px",
          marginTop: "20px"
        }}
      >
        <h3>Name: Researcher</h3>
        <p>Email: debastutisahoo@gmail.com</p>
        <p>Projects: 12</p>
        <p>Funding Received: ₹2 Cr</p>
      </div>
    </div>
  );
}

export default Profile;