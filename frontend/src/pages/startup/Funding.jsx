import { useEffect, useState } from "react";
import { ArrowRight, CalendarDays, ExternalLink, IndianRupee, Search, Sparkles } from "lucide-react";
import { getStartupFunding } from "../../api/startup";
import { Link } from "react-router-dom";

export default function Funding() {
  const [query, setQuery] = useState("");
  const [opportunities, setOpportunities] = useState([]);
  const [warnings, setWarnings] = useState([]);
  const [loading, setLoading] = useState(true);

  async function load(value = query) {
    setLoading(true);
    try {
      const data = await getStartupFunding(value);
      setOpportunities(data.funding_opportunities || []);
      setWarnings(data.source_warnings || []);
    } catch (error) {
      setWarnings([error.response?.data?.detail || "Unable to load funding opportunities."]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(""); }, []);

  return (
    <div className="startup-page">
      <div className="startup-page-header"><span className="startup-eyebrow">FUNDING DISCOVERY</span><h1>Funding Opportunities</h1><p>Explore live grants and funding opportunities matched to your startup's industry, technology and funding needs.</p></div>
      <section className="startup-panel startup-search-panel">
        <form onSubmit={(event) => { event.preventDefault(); load(); }} className="startup-search-form">
          <div className="startup-search-input"><Search size={18} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search startup grants, AI, biotech, climate..." /></div>
          <button className="startup-primary-button" type="submit">Search</button>
        </form>
      </section>
      {warnings.length > 0 && <div className="startup-warning">Some funding sources could not be reached. Other sources are still shown.</div>}
      <section className="startup-results-section">
        <div className="startup-results-heading"><div><span className="startup-eyebrow">LIVE SOURCES</span><h2>{opportunities.length} Opportunities</h2></div></div>
        {loading ? <div className="startup-loading">Loading funding opportunities...</div> : opportunities.length === 0 ? <div className="startup-empty-box">No funding opportunities were found for this search.</div> : (
          <div className="startup-funding-grid">
            {opportunities.map((item) => <FundingCard key={item.id || `${item.source}-${item.title}`} item={item} />)}
          </div>
        )}
      </section>
    </div>
  );
}

function FundingCard({ item }) {
  return (
    <article className="startup-funding-card">
      <div className="startup-funding-top"><span className="startup-source-pill">{item.source || "Funding source"}</span>{item.funding_type && <span className="startup-type-pill">{item.funding_type}</span>}</div>
      <h3>{item.title}</h3>
      <p className="startup-funding-org">{item.organization || "Organization not specified"}</p>
      <div className="startup-funding-details">
        <div><IndianRupee size={16} /><span>{item.funding_amount || "Amount not specified"}</span></div>
        {item.deadline && <div><CalendarDays size={16} /><span>{item.deadline}</span></div>}
      </div>
      <p className="startup-funding-description">{item.description || "No description available."}</p>
      <div className="startup-card-actions">
        <Link className="startup-primary-button" to={`/startup/predict-success/${encodeURIComponent(item.id)}`}><Sparkles size={16} /> Predict Success</Link>
        {item.official_link && <a className="startup-secondary-button" href={item.official_link} target="_blank" rel="noreferrer"><ExternalLink size={16} /> Official Website</a>}
      </div>
      <ArrowRight className="startup-card-watermark" size={52} />
    </article>
  );
}
