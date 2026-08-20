import { useEffect, useState } from "react";
import { ArrowRight, Building2, Code2, Mail, Search, Send, UserRound } from "lucide-react";
import { searchResearchers } from "../../api/startup";
import { sendCollaborationRequest } from "../../api/collaboration";

export default function FindResearchers() {
  const [query, setQuery] = useState("");
  const [researchers, setResearchers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(null);
  const [message, setMessage] = useState("");

  async function load(value = query) {
    setLoading(true);
    setMessage("");
    try {
      const data = await searchResearchers(value);
      setResearchers(data.researchers || []);
    } catch (error) {
      setMessage(error.response?.data?.detail || "Unable to load researchers.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(""); }, []);

  async function connect(researcher) {
    const text = window.prompt(`Message for ${researcher.full_name}:`, "I would like to explore a research collaboration with your work.");
    if (text === null) return;
    setSending(researcher.user_id);
    try {
      await sendCollaborationRequest(researcher.user_id, text.trim());
      setMessage("Collaboration request sent successfully.");
    } catch (error) {
      setMessage(error.response?.data?.detail || "Unable to send the request.");
    } finally {
      setSending(null);
    }
  }

  return (
    <div className="startup-page">
      <PageHeader eyebrow="COLLABORATION" title="Find Researchers" text="Discover researchers whose domains, technologies and expertise align with your startup." />

      <section className="startup-panel startup-search-panel">
        <form onSubmit={(event) => { event.preventDefault(); load(); }} className="startup-search-form">
          <div className="startup-search-input"><Search size={18} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search AI, healthcare, robotics, university..." /></div>
          <button className="startup-primary-button" type="submit">Search</button>
        </form>
      </section>

      {message && <div className="startup-alert">{message}</div>}

      <section className="startup-results-section">
        <div className="startup-results-heading"><div><span className="startup-eyebrow">RESEARCH NETWORK</span><h2>{researchers.length} Researchers</h2></div></div>
        {loading ? <div className="startup-loading">Finding researchers...</div> : researchers.length === 0 ? <Empty text="No researchers matched your search." /> : (
          <div className="startup-result-grid">
            {researchers.map((researcher) => (
              <article className="startup-result-card" key={researcher.user_id}>
                <div className="startup-result-top"><div className="startup-result-avatar"><UserRound size={20} /></div><span className="startup-match-pill">Researcher</span></div>
                <h3>{researcher.full_name}</h3>
                <p className="startup-result-role">{researcher.current_position || "Researcher"}</p>
                <div className="startup-result-detail"><Building2 size={16} /> {researcher.organization_name || "Organization not specified"}</div>
                <div className="startup-result-detail"><Code2 size={16} /> {researcher.technology_areas?.join(", ") || researcher.research_domains?.join(", ") || "Research areas not specified"}</div>
                <p className="startup-result-bio">{researcher.bio || "No profile summary provided."}</p>
                <div className="startup-card-actions">
{researcher.email && (
  <a
    href={`https://mail.google.com/mail/u/0/?view=cm&fs=1&to=${encodeURIComponent(
      researcher.email
    )}&su=${encodeURIComponent(
      "Research Collaboration Opportunity - InnovFund"
    )}`}
    target="_blank"
    rel="noopener noreferrer"
    className="startup-secondary-button"
  >
    <Mail size={16} /> Email
  </a>
)}              <button className="startup-primary-button" onClick={() => connect(researcher)} disabled={sending === researcher.user_id}><Send size={16} /> {sending === researcher.user_id ? "Sending..." : "Connect"}</button>
                </div>
                <ArrowRight className="startup-card-watermark" size={48} />
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function PageHeader({ eyebrow, title, text }) {
  return <div className="startup-page-header"><span className="startup-eyebrow">{eyebrow}</span><h1>{title}</h1><p>{text}</p></div>;
}

function Empty({ text }) { return <div className="startup-empty-box">{text}</div>; }
