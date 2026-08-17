import { useEffect, useState } from "react";
import {
  ArrowRight,
  Building2,
  Code2,
  MapPin,
  Search,
  Send,
  Users,
} from "lucide-react";
import {
  searchStartups,
  sendCollaborationRequest,
} from "../../api/researcher/collaboration";
import "../../styles/researcher-collaboration.css";

export default function FindStartups() {
  const [query, setQuery] = useState("");
  const [startups, setStartups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(null);
  const [message, setMessage] = useState("");

  async function load(value = query) {
    setLoading(true);
    setMessage("");

    try {
      const data = await searchStartups(value);
      setStartups(data.startups || []);
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Unable to load startups."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load("");
  }, []);

  async function connect(startup) {
    const text = window.prompt(
      `Message for ${startup.startup_name}:`,
      "I would like to explore a collaboration with your startup."
    );

    if (text === null) return;

    setSending(startup.user_id);
    setMessage("");

    try {
      await sendCollaborationRequest(
        startup.user_id,
        text.trim()
      );
      setMessage(
        "Collaboration request sent successfully."
      );
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Unable to send the request."
      );
    } finally {
      setSending(null);
    }
  }

  return (
    <div className="research-collab-page">
      <div className="research-collab-page-header">
        <span className="research-collab-eyebrow">
          COLLABORATION
        </span>

        <h1>Find Startups</h1>

        <p>
          Discover startups working in related industries and
          technologies for partnerships, co-development and
          knowledge sharing.
        </p>
      </div>

      <section className="research-collab-panel research-collab-search-panel">
        <form
          className="research-collab-search-form"
          onSubmit={(event) => {
            event.preventDefault();
            load();
          }}
        >
          <div className="research-collab-search-input">
            <Search size={18} />

            <input
              value={query}
              onChange={(event) =>
                setQuery(event.target.value)
              }
              placeholder="Search AI, fintech, healthcare, Bengaluru..."
            />
          </div>

          <button
            className="research-collab-primary-button"
            type="submit"
          >
            Search
          </button>
        </form>
      </section>

      {message && (
        <div className="research-collab-alert">
          {message}
        </div>
      )}

      <section className="research-collab-results-section">
        <div className="research-collab-results-heading">
          <div>
            <span className="research-collab-eyebrow">
              STARTUP NETWORK
            </span>

            <h2>{startups.length} Startups</h2>
          </div>
        </div>

        {loading ? (
          <div className="research-collab-loading">
            Finding startups...
          </div>
        ) : startups.length === 0 ? (
          <div className="research-collab-empty-box">
            No startups matched your search.
          </div>
        ) : (
          <div className="research-collab-result-grid">
            {startups.map((startup) => (
              <article
                className="research-collab-result-card"
                key={startup.id}
              >
                <div className="research-collab-result-top">
                  <div className="research-collab-result-avatar orange">
                    <Building2 size={20} />
                  </div>

                  <span className="research-collab-match-pill">
                    {startup.stage || "Startup"}
                  </span>
                </div>

                <h3>{startup.startup_name}</h3>

                <p className="research-collab-result-role">
                  {startup.tagline ||
                    startup.industry ||
                    "Innovation startup"}
                </p>

                <div className="research-collab-result-detail">
                  <Building2 size={16} />
                  {startup.industry ||
                    "Industry not specified"}
                </div>

                <div className="research-collab-result-detail">
                  <Code2 size={16} />
                  {startup.technology_stack ||
                    "Technology stack not specified"}
                </div>

                <div className="research-collab-result-detail">
                  <MapPin size={16} />
                  {startup.location ||
                    "Location not specified"}
                </div>

                <div className="research-collab-result-detail">
                  <Users size={16} />
                  Team size:{" "}
                  {startup.team_size || "Not specified"}
                </div>

                <p className="research-collab-result-bio">
                  {startup.description ||
                    "No startup description provided."}
                </p>

                <div className="research-collab-card-actions">
                  <button
                    className="research-collab-primary-button"
                    onClick={() => connect(startup)}
                    disabled={sending === startup.user_id}
                  >
                    <Send size={16} />

                    {sending === startup.user_id
                      ? "Sending..."
                      : "Connect"}
                  </button>
                </div>

                <ArrowRight
                  className="research-collab-card-watermark"
                  size={48}
                />
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
