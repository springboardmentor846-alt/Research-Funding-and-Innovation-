import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { patentsAPI } from "../services/api.js";

export default function Patents() {
  const [q, setQ] = useState("");
  const [source, setSource] = useState("all");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  const [gap, setGap] = useState([]);
  const [explainInput, setExplainInput] = useState("");
  const [explanation, setExplanation] = useState("");
  const [explaining, setExplaining] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    patentsAPI.analytics().then((r) => setAnalytics(r.data));
    patentsAPI.gapAnalysis().then((r) => setGap(r.data.report));
  }, []);

  async function search(e) {
    e?.preventDefault();
    if (!q.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await patentsAPI.search(q, source);
      setResults(res.data.results);
    } catch (err) {
      setError("Search failed");
    } finally {
      setLoading(false);
    }
  }

  async function explain() {
    if (explainInput.length < 100) {
      setError("Please paste a longer patent text (at least 100 chars)");
      return;
    }
    setExplaining(true);
    setError("");
    try {
      const res = await patentsAPI.explain(explainInput);
      setExplanation(res.data.explanation);
    } catch (err) {
      setError("Failed to explain patent");
    } finally {
      setExplaining(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">🔬 Patent Intelligence</h1>
        <p className="text-slate-500 text-sm">
          Search across Google Patents, USPTO, and The Lens
        </p>
      </div>

      {error && <div className="card bg-red-50 text-red-700">{error}</div>}

      {/* Search */}
      <div className="card">
        <form onSubmit={search} className="flex flex-wrap gap-2">
          <input
            className="input flex-1 min-w-[200px]"
            placeholder="Search patents by title, abstract, or technology..."
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          <select
            className="input"
            value={source}
            onChange={(e) => setSource(e.target.value)}
          >
            <option value="all">All Sources</option>
            <option value="google_patents">Google Patents</option>
            <option value="uspto">USPTO</option>
            <option value="the_lens">The Lens</option>
          </select>
          <button className="btn-primary" disabled={loading}>
            {loading ? "Searching..." : "Search"}
          </button>
        </form>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="grid gap-4">
          {results.map((p) => (
            <div key={p.patent_number || p.id} className="card">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <h3 className="font-semibold text-slate-800">{p.title}</h3>
                  <div className="text-xs text-slate-500 mt-1">
                    {p.patent_number} · {p.source} · {p.publication_year || "—"}
                  </div>
                </div>
                <Link
                  to={`/patents/dashboard/${encodeURIComponent(p.patent_number || p.id)}`}
                  className="btn-primary text-xs whitespace-nowrap"
                >
                  🧠 Open Dashboard
                </Link>
              </div>
              <p className="text-sm text-slate-600 mt-2">{p.abstract}</p>
              <div className="flex flex-wrap gap-2 mt-3">
                {p.technology && (
                  <span className="badge-primary">{p.technology}</span>
                )}
                <span className="badge-success">
                  📚 {p.citations ?? 0} citations
                </span>
                {p.country && (
                  <span className="badge bg-slate-100 text-slate-700">🌍 {p.country}</span>
                )}
                {p.assignee && (
                  <span className="badge bg-purple-100 text-purple-800">
                    🏢 {p.assignee}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Analytics */}
      {analytics && (
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="font-semibold text-slate-800 mb-4">Patents by Source</h3>
            <div className="space-y-2">
              {analytics.by_source.map((b) => (
                <div
                  key={b.source}
                  className="flex items-center justify-between"
                >
                  <span className="text-sm text-slate-700">{b.source}</span>
                  <span className="badge-primary">{b.count}</span>
                </div>
              ))}
            </div>
            <div className="mt-4 text-sm text-slate-600">
              Total: <strong>{analytics.total_patents}</strong> patents ·{" "}
              {analytics.total_citations} citations
            </div>
          </div>

          <div className="card">
            <h3 className="font-semibold text-slate-800 mb-4">
              Technology Areas
            </h3>
            <div className="space-y-2">
              {analytics.by_technology.map((b) => (
                <div
                  key={b.technology}
                  className="flex items-center justify-between"
                >
                  <span className="text-sm text-slate-700">{b.technology}</span>
                  <span className="badge-purple">{b.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Technology Gap Analysis */}
      {gap.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-4">
            🔍 Technology Gap Analysis
          </h3>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {gap.map((g, i) => (
              <div
                key={i}
                className="p-4 border border-slate-200 rounded-lg"
              >
                <div className="font-semibold text-slate-800">{g.area}</div>
                <div className="text-sm text-slate-600 mt-1">
                  {g.opportunity}
                </div>
                <div
                  className={`mt-2 text-xs font-medium ${
                    g.potential === "High" ? "text-green-600" : "text-amber-600"
                  }`}
                >
                  Potential: {g.potential}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Patent Explainer */}
      <div className="card">
        <h3 className="font-semibold text-slate-800 mb-3">🤖 AI Patent Explainer</h3>
        <p className="text-sm text-slate-500 mb-3">
          Paste a patent abstract or description and the AI will explain it in
          simple language.
        </p>
        <textarea
          className="input min-h-[120px]"
          placeholder="Paste patent text here (min 100 chars)..."
          value={explainInput}
          onChange={(e) => setExplainInput(e.target.value)}
        />
        <button onClick={explain} className="btn-primary mt-3" disabled={explaining}>
          {explaining ? "Explaining..." : "Explain Patent"}
        </button>
        {explanation && (
          <div className="mt-4 p-4 bg-primary-50 border border-primary-200 rounded-lg">
            <div className="text-sm text-slate-700 whitespace-pre-wrap">
              {explanation}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
