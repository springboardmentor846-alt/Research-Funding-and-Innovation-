import React, { useState } from "react";
import { searchAPI } from "../services/api.js";

export default function Search() {
  const [q, setQ] = useState("");
  const [mode, setMode] = useState("publications");
  const [collection, setCollection] = useState("publications");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function run(e) {
    e?.preventDefault();
    if (!q.trim()) return;
    setLoading(true);
    setError("");
    try {
      if (mode === "semantic") {
        const r = await searchAPI.semantic(q, collection, 10);
        setResults(r.data.results);
      } else {
        const r = await searchAPI[mode](q, 1, 20);
        setResults(r.data.results);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Search failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">🔍 Semantic & Keyword Search</h1>
        <p className="text-slate-500 text-sm">Powered by Elasticsearch + FAISS vector search</p>
      </div>

      <div className="card">
        <form onSubmit={run} className="space-y-3">
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setMode("publications")}
              className={`px-3 py-1.5 rounded-md text-sm font-medium ${
                mode === "publications" ? "bg-primary-600 text-white" : "bg-slate-100 text-slate-700"
              }`}
            >
              📄 Publications
            </button>
            <button
              type="button"
              onClick={() => setMode("funding")}
              className={`px-3 py-1.5 rounded-md text-sm font-medium ${
                mode === "funding" ? "bg-primary-600 text-white" : "bg-slate-100 text-slate-700"
              }`}
            >
              💰 Funding
            </button>
            <button
              type="button"
              onClick={() => setMode("semantic")}
              className={`px-3 py-1.5 rounded-md text-sm font-medium ${
                mode === "semantic" ? "bg-primary-600 text-white" : "bg-slate-100 text-slate-700"
              }`}
            >
              🧠 Semantic (FAISS)
            </button>
          </div>
          {mode === "semantic" && (
            <div>
              <label className="label">Collection</label>
              <select className="input" value={collection} onChange={(e) => setCollection(e.target.value)}>
                <option value="publications">Publications</option>
                <option value="funding">Funding Opportunities</option>
                <option value="patents">Patents</option>
              </select>
            </div>
          )}
          <div className="flex flex-wrap gap-2">
            <input
              className="input flex-1 min-w-[200px]"
              placeholder="Search..."
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
            <button className="btn-primary" disabled={loading}>
              {loading ? "Searching..." : "Search"}
            </button>
          </div>
        </form>
      </div>

      {error && <div className="card bg-red-50 text-red-700">{error}</div>}

      {results.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-3">
            {results.length} Result{results.length !== 1 ? "s" : ""}
          </h3>
          <div className="space-y-3">
            {results.map((r, i) => (
              <div key={i} className="p-4 border border-slate-200 rounded-lg hover:border-primary-300 transition">
                <div className="flex items-start justify-between gap-2">
                  <div className="font-semibold text-slate-800">
                    {r.title || r.name || `Result #${i + 1}`}
                  </div>
                  {r.score != null && (
                    <span className="badge-success text-xs">{(r.score * 100).toFixed(1)}% match</span>
                  )}
                </div>
                {r.abstract && <p className="text-sm text-slate-600 mt-1 line-clamp-2">{r.abstract}</p>}
                {r.description && <p className="text-sm text-slate-600 mt-1 line-clamp-2">{r.description}</p>}
                {r.keywords && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {r.keywords.split(",").slice(0, 5).map((k, j) => (
                      <span key={j} className="text-xs text-slate-500">#{k.trim()}</span>
                    ))}
                  </div>
                )}
                {r.organization && (
                  <div className="text-xs text-slate-500 mt-1">{r.organization}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {q && !loading && results.length === 0 && !error && (
        <div className="card text-center text-slate-500">No results found for "{q}"</div>
      )}
    </div>
  );
}
