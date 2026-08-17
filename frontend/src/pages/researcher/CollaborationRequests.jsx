import { useEffect, useMemo, useState } from "react";
import {
  Check,
  Clock3,
  X,
  Send,
  Users,
} from "lucide-react";
import {
  getCollaborationRequests,
  updateCollaborationRequest,
} from "../../api/researcher/collaboration";
import "../../styles/researcher-collaboration.css";

export default function CollaborationRequests() {
  const [data, setData] = useState({
    incoming: [],
    outgoing: [],
  });
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
          item.sender_name ||
          item.counterpart_name ||
          "Connection",
        connection_role:
          item.sender_role ||
          item.counterpart_role ||
          "",
      }));

    const acceptedOutgoing = (data.outgoing || [])
      .filter((item) => item.status === "accepted")
      .map((item) => ({
        ...item,
        connection_name:
          item.recipient_name ||
          item.counterpart_name ||
          "Connection",
        connection_role:
          item.recipient_role ||
          item.counterpart_role ||
          "",
      }));

    const accepted = [
      ...acceptedIncoming,
      ...acceptedOutgoing,
    ];

    const seen = new Set();

    return accepted.filter((item) => {
      const key = [
        item.sender_user_id,
        item.recipient_user_id,
      ]
        .sort()
        .join("-");

      if (seen.has(key)) return false;

      seen.add(key);
      return true;
    });
  }, [data]);

  return (
    <div className="research-collab-page">
      <div className="research-collab-page-header">
        <span className="research-collab-eyebrow">
          COLLABORATION
        </span>

        <h1>Collaboration Requests</h1>

        <p>
          Accept, reject and track collaboration requests
          with startups and other researchers.
        </p>
      </div>

      {message && (
        <div className="research-collab-alert">
          {message}
        </div>
      )}

      {loading ? (
        <div className="research-collab-loading">
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
          

          <section className="research-collab-panel research-collab-request-section">
            <div className="research-collab-panel-heading">
              <span className="research-collab-eyebrow">
                NETWORK
              </span>

              <h2>
                Your Connections
                <span className="research-collab-connection-count">
                  {connections.length}
                </span>
              </h2>

              <p>
                Startups and researchers whose collaboration
                requests you have accepted.
              </p>
            </div>

            <br />

            {connections.length === 0 ? (
              <div className="research-collab-empty-box">
                No active connections yet.
              </div>
            ) : (
              <div className="research-collab-request-list">
                {connections.map((item) => (
                  <div
                    className="research-collab-request-row"
                    key={`connection-${item.id}`}
                  >
                    <div className="research-collab-connection-person">
                      <span className="research-collab-result-avatar">
                        <Users size={18} />
                      </span>

                      <div>
                        <strong>
                          {item.connection_name}
                        </strong>

                        {item.connection_role && (
                          <span>
                            {item.connection_role}
                          </span>
                        )}

                        <p>
                          {item.message ||
                            "Connected through InnovFund."}
                        </p>
                      </div>
                    </div>

                    <span className="research-collab-status accepted research-collab-connected-status">
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
    <section className="research-collab-panel research-collab-request-section">
      <div className="research-collab-panel-heading">
        <span className="research-collab-eyebrow">
          {eyebrow}
        </span>

        <h2>{title}</h2>
      </div>

      <br />

      {items.length === 0 ? (
        <div className="research-collab-empty-box">
          No requests here.
        </div>
      ) : (
        <div className="research-collab-request-list">
          {items.map((item) => {
            const person = incoming
              ? item.sender_name
              : item.recipient_name;

            const role = incoming
              ? item.sender_role
              : item.recipient_role;

            return (
              <div
                className="research-collab-request-row"
                key={item.id}
              >
                <div>
                  <strong>{person}</strong>
                  <span>{role}</span>
                  <p>
                    {item.message ||
                      "No message provided."}
                  </p>
                </div>

                <div className="research-collab-request-actions">
                  <span
                    className={`research-collab-status ${item.status}`}
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

                  {incoming &&
                    item.status === "pending" && (
                      <>
                        <button
                          className="research-collab-action accept"
                          title="Accept request"
                          aria-label="Accept request"
                          onClick={() =>
                            onUpdate(item.id, "accepted")
                          }
                          disabled={updating === item.id}
                        >
                          <Check
                            size={16}
                            strokeWidth={2.5}
                          />
                        </button>

                        <button
                          className="research-collab-action reject"
                          title="Reject request"
                          aria-label="Reject request"
                          onClick={() =>
                            onUpdate(item.id, "rejected")
                          }
                          disabled={updating === item.id}
                        >
                          <X
                            size={16}
                            strokeWidth={2.5}
                          />
                        </button>
                      </>
                    )}

                  {!incoming &&
                    item.status === "pending" && (
                      <button
                        className="research-collab-action cancel"
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
