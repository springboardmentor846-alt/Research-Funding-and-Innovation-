import { useEffect, useState } from "react";
import { ArrowRight, Building2, Code2, MapPin, Send, Search, Users } from "lucide-react";
import { searchStartups } from "../../api/startup";
import { sendCollaborationRequest } from "../../api/collaboration";

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
      setMessage(error.response?.data?.detail || "Unable to load startups.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(""); }, []);

  async function connect(startup) {
    const text = window.prompt(`Message for ${startup.startup_name}:`, "I would like to explore a collaboration between our startups.");
    if (text === null) return;
    setSending(startup.user_id);
    try {
      await sendCollaborationRequest(startup.user_id, text.trim());
      setMessage("Collaboration request sent successfully.");
    } catch (error) {
      setMessage(error.response?.data?.detail || "Unable to send the request.");
    } finally {
      setSending(null);
    }
  }

  return (
    <div className="startup-page">
      <div className="startup-page-header"><span className="startup-eyebrow">COLLABORATION</span><h1>Find Startups</h1><p>Discover startups working in related industries and technologies for partnerships, co-development and knowledge sharing.</p></div>
      <section className="startup-panel startup-search-panel">
        <form onSubmit={(event) => { event.preventDefault(); load(); }} className="startup-search-form">
          <div className="startup-search-input"><Search size={18} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search AI, fintech, healthcare, Bengaluru..." /></div>
          <button className="startup-primary-button" type="submit">Search</button>
        </form>
      </section>
      {message && <div className="startup-alert">{message}</div>}
      <section className="startup-results-section">
        <div className="startup-results-heading"><div><span className="startup-eyebrow">STARTUP NETWORK</span><h2>{startups.length} Startups</h2></div></div>
        {loading ? <div className="startup-loading">Finding startups...</div> : startups.length === 0 ? <div className="startup-empty-box">No startups matched your search.</div> : (
          <div className="startup-result-grid">
            {startups.map((startup) => (
              <article className="startup-result-card" key={startup.id}>
                <div className="startup-result-top"><div className="startup-result-avatar orange"><Building2 size={20} /></div><span className="startup-match-pill">{startup.stage || "Startup"}</span></div>
                <h3>{startup.startup_name}</h3>
                <p className="startup-result-role">{startup.tagline || startup.industry || "Innovation startup"}</p>
                <div className="startup-result-detail"><Building2 size={16} /> {startup.industry || "Industry not specified"}</div>
                <div className="startup-result-detail"><Code2 size={16} /> {startup.technology_stack || "Technology stack not specified"}</div>
                <div className="startup-result-detail"><MapPin size={16} /> {startup.location || "Location not specified"}</div>
                <div className="startup-result-detail"><Users size={16} /> Team size: {startup.team_size || "Not specified"}</div>
                <p className="startup-result-bio">{startup.description || "No startup description provided."}</p>
                <div className="startup-card-actions"><button className="startup-primary-button" onClick={() => connect(startup)} disabled={sending === startup.user_id}><Send size={16} /> {sending === startup.user_id ? "Sending..." : "Connect"}</button></div>
                <ArrowRight className="startup-card-watermark" size={48} />
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
