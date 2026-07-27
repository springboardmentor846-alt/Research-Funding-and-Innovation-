import { useParams } from "react-router-dom";

function PatentDetails() {
  const { id } = useParams();

  return (
    <div style={{ padding: "30px" }}>
      <h1>Patent Details</h1>

      <h2>Patent {id}</h2>

      <p><b>Patent Title:</b> AI Healthcare Monitoring System</p>
      <p><b>Inventor:</b> Debastuti Sahoo</p>
      <p><b>Patent ID:</b> PAT-2026-001</p>
      <p><b>Status:</b> Filed</p>
      <p><b>Department:</b> MCA</p>
      <p><b>Description:</b> AI-based healthcare monitoring system.</p>
    </div>
  );
}

export default PatentDetails;