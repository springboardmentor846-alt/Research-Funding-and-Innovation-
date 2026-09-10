import { useEffect, useState, useCallback } from "react";
import axios from "axios";

const API_BASE = "https://research-platform-backend-e0sf.onrender.com/api/v1/collaboration";

function CollaborationRequests({ token }) {
  const [received, setReceived] = useState([]);
  const [sent, setSent] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const [receiverId, setReceiverId] = useState("");
  const [message, setMessage] = useState("");
  const [sendStatus, setSendStatus] = useState("");

  const authHeaders = { headers: { Authorization: `Bearer ${token}` } };

  const loadRequests = useCallback(async () => {
    setLoading(true);
    try {
      const [receivedRes, sentRes] = await Promise.all([
        axios.get(`${API_BASE}/received`, authHeaders),
        axios.get(`${API_BASE}/sent`, authHeaders),
      ]);
      setReceived(receivedRes.data);
      setSent(sentRes.data);
      setError("");
    } catch (err) {
      setError("Could not load collaboration requests.");
    }
    setLoading(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  useEffect(() => {
    loadRequests();
  }, [loadRequests]);

  const handleSend = async (e) => {
    e.preventDefault();
    setSendStatus("");
    if (!receiverId.trim()) return;

    try {
      await axios.post(
        `${API_BASE}/`,
        { receiver_id: parseInt(receiverId, 10), message },
        authHeaders
      );
      setSendStatus("Request sent.");
      setReceiverId("");
      setMessage("");
      loadRequests();
    } catch (err) {
      setSendStatus(err.response?.data?.detail || "Could not send request.");
    }
  };

  const handleRespond = async (requestId, status) => {
    try {
      await axios.patch(`${API_BASE}/${requestId}`, { status }, authHeaders);
      loadRequests();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not update request.");
    }
  };

  const statusColor = (status) => {
    if (status === "accepted") return "#1C8C7A";
    if (status === "rejected") return "#B0479B";
    return "#C9862B";
  };

  return (
    <>
      <div className="dash-card">
        <h3>Send Collaboration Request</h3>
        <p className="dash-card-subtitle">
          Enter the user ID of the researcher or startup you'd like to collaborate with.
        </p>
        <form onSubmit={handleSend} style={{ display: "flex", flexDirection: "column", gap: "10px", maxWidth: "420px" }}>
          <input
            type="number"
            placeholder="Receiver user ID"
            value={receiverId}
            onChange={(e) => setReceiverId(e.target.value)}
            required
          />
          <textarea
            placeholder="Message (optional)"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={3}
          />
          <button type="submit" className="auth-submit" style={{ width: "fit-content" }}>
            Send Request
          </button>
        </form>
        {sendStatus && <p className="dash-card-subtitle">{sendStatus}</p>}
      </div>

      <div className="dash-card">
        <h3>Received Requests</h3>
        {loading && <p className="dash-empty">Loading...</p>}
        {error && <p className="dash-error">{error}</p>}
        {!loading && received.length === 0 && (
          <p className="dash-empty">No collaboration requests received yet.</p>
        )}
        {received.map((req) => (
          <div key={req.id} className="dash-card" style={{ marginTop: "10px" }}>
            <p><strong>From user #{req.sender_id}</strong></p>
            {req.message && <p className="dash-card-subtitle">{req.message}</p>}
            <p style={{ color: statusColor(req.status), fontWeight: 600 }}>
              {req.status.toUpperCase()}
            </p>
            {req.status === "pending" && (
              <div style={{ display: "flex", gap: "8px", marginTop: "8px" }}>
                <button className="auth-submit" onClick={() => handleRespond(req.id, "accepted")}>
                  Accept
                </button>
                <button className="auth-submit" style={{ background: "#B0479B" }} onClick={() => handleRespond(req.id, "rejected")}>
                  Reject
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="dash-card">
        <h3>Sent Requests</h3>
        {!loading && sent.length === 0 && (
          <p className="dash-empty">You haven't sent any collaboration requests yet.</p>
        )}
        {sent.map((req) => (
          <div key={req.id} className="dash-card" style={{ marginTop: "10px" }}>
            <p><strong>To user #{req.receiver_id}</strong></p>
            {req.message && <p className="dash-card-subtitle">{req.message}</p>}
            <p style={{ color: statusColor(req.status), fontWeight: 600 }}>
              {req.status.toUpperCase()}
            </p>
          </div>
        ))}
      </div>
    </>
  );
}

export default CollaborationRequests;
