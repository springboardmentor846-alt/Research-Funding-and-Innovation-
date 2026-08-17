import { useEffect, useMemo, useState } from "react";
import { Check, Clock3, Handshake, X, Send, Users } from "lucide-react";
import {
  getCollaborationRequests,
  updateCollaborationRequest,
} from "../../api/collaboration";

export default function CollaborationRequests() {
  const [data, setData] = useState({ incoming: [], outgoing: [] });
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(null);
  const [message, setMessage] = useState("");

  async function load() {
    setLoading(true);
    setMessage("");

    try {
      setData(await getCollaborationRequests());
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Unable to load collaboration requests."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function update(id, status) {
    setUpdating(id);
    setMessage("");

    try {
      await updateCollaborationRequest(id, status);
      await load();
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Unable to update the request."
      );
    } finally {
      setUpdating(null);
    }
  }

  const connections = useMemo(() => {
    const acceptedIncoming = (data.incoming || [])
      .filter((item) => item.status === "accepted")
      .map((item) => ({
        ...item,
        connection_name:
          item.sender_name || item.counterpart_name || "Connection",
        connection_role:
          item.sender_role || item.counterpart_role || "",
      }));

    const acceptedOutgoing = (data.outgoing || [])
      .filter((item) => item.status === "accepted")
      .map((item) => ({
        ...item,
        connection_name:
          item.recipient_name || item.counterpart_name || "Connection",
        connection_role:
          item.recipient_role || item.counterpart_role || "",
      }));

    const accepted = [...acceptedIncoming, ...acceptedOutgoing];

    const seen = new Set();

    return accepted.filter((item) => {
      const key = [item.sender_user_id, item.recipient_user_id]
        .sort()
        .join("-");

      if (seen.has(key)) {
        return false;
      }

      seen.add(key);
      return true;
    });
  }, [data]);

  const connectionCount = connections.length;

  return (
    <div className="startup-page">
      <div className="startup-page-header">
        <span className="startup-eyebrow">COLLABORATION</span>

        <h1>Collaboration Requests</h1>

        <p>
          Accept, reject and track collaboration requests with researchers
          and other startup founders.
        </p>
      </div>

      {message && <div className="startup-alert">{message}</div>}

      {loading ? (
        <div className="startup-loading">
          Loading collaboration requests...
        </div>
      ) : (
        <>
          <RequestSection
            eyebrow="RECEIVED"
            title="Incoming Requests"
            items={data.incoming || []}
            incoming
            updating={updating}
            onUpdate={update}
          />

          <RequestSection
            eyebrow="SENT"
            title="Outgoing Requests"
            items={data.outgoing || []}
            updating={updating}
            onUpdate={update}
          />

          <section className="startup-panel startup-request-section">
            <div className="startup-panel-heading">
              <span className="startup-eyebrow">NETWORK</span>

              <h2>
                Your Connections
                <span className="startup-connection-count">
                  {connectionCount}
                </span>
              </h2>

              <p>
                People and startups whose collaboration requests you have
                accepted.
              </p>
            </div>

            {connections.length === 0 ? (
              <div className="startup-empty-box">
                No active connections yet.
              </div>
            ) : (
              <div className="startup-request-list">
                {connections.map((item) => (
                  <div
                    className="startup-request-row startup-connection-row"
                    key={`connection-${item.id}`}
                  >
                    <div className="startup-connection-person">
                      <span className="startup-result-avatar">
                        <Users size={18} />
                      </span>

                      <div>
                        <strong>{item.connection_name}</strong>

                        {item.connection_role && (
                          <span>{item.connection_role}</span>
                        )}

                        <p>
                          {item.message ||
                            "Connected through InnovFund."}
                        </p>
                      </div>
                    </div>

                    <span className="startup-status accepted startup-connected-status">
                      <Check size={14} />
                      Connected
                    </span>
                  </div>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}

function RequestSection({
  eyebrow,
  title,
  items,
  incoming,
  updating,
  onUpdate,
}) {
  return (
    <section className="startup-panel startup-request-section">
      <div className="startup-panel-heading">
        <span className="startup-eyebrow">{eyebrow}</span>

        <h2>{title}</h2>
      </div>

      {items.length === 0 ? (
        <div className="startup-empty-box">
          No requests here.
        </div>
      ) : (
        <div className="startup-request-list">
          {items.map((item) => {
            const person = incoming
              ? item.sender_name
              : item.recipient_name;

            const role = incoming
              ? item.sender_role
              : item.recipient_role;

            return (
              <div
                className="startup-request-row"
                key={item.id}
              >
                <div>
                  <strong>{person}</strong>

                  <span>{role}</span>

                  <p>
                    {item.message || "No message provided."}
                  </p>
                </div>

                <div className="startup-request-actions">
                  <span
                    className={`startup-status ${item.status}`}
                  >
                    {item.status === "pending" && (
                      <Clock3 size={14} />
                    )}

                    {item.status === "accepted" && (
                      <Check size={14} />
                    )}

                    {item.status === "rejected" && (
                      <X size={14} />
                    )}

                    {item.status}
                  </span>

                  {incoming && item.status === "pending" && (
                    <>
                      <button
                        className="startup-request-action accept"
                        title="Accept request"
                        aria-label="Accept request"
                        onClick={() =>
                          onUpdate(item.id, "accepted")
                        }
                        disabled={updating === item.id}
                      >
                        <Check size={16} strokeWidth={2.5} />
                      </button>

                      <button
                        className="startup-request-action reject"
                        title="Reject request"
                        aria-label="Reject request"
                        onClick={() =>
                          onUpdate(item.id, "rejected")
                        }
                        disabled={updating === item.id}
                      >
                        <X size={16} strokeWidth={2.5} />
                      </button>
                    </>
                  )}

                  {!incoming && item.status === "pending" && (
                    <button
                      className="startup-request-action cancel"
                      title="Cancel request"
                      aria-label="Cancel request"
                      onClick={() =>
                        onUpdate(item.id, "cancelled")
                      }
                      disabled={updating === item.id}
                    >
                      <Send size={14} />
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}