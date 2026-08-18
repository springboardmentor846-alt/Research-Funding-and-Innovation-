import React, { useEffect, useState } from "react";
import { fundingAPI } from "../services/api.js";

export default function Recommendations() {
  const [recs, setRecs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [generatedAt, setGeneratedAt] = useState(null);
  const [cacheHit, setCacheHit] = useState(null);
  const [topK, setTopK] = useState(10);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const res = await fundingAPI.recommendations(topK);
      setRecs(res.data.recommendations);
      setGeneratedAt(res.data.generated_at);
      setCacheHit(res.data.cache_hit);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to load recommendations. Add at least one research interest or publication."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    /* eslint-disable-next-line */
  }, [topK]);

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">
            🎯 AI Funding Recommendations
          </h1>
          <p className="text-slate-500 text-sm">
            Highly relevant matches using rule-based filtering + publication
            similarity (60%) and research-interest match (40%).
          </p>
        </div>
        <div className="flex gap-2">
          <select
            className="input"
            value={topK}
            onChange={(e) => setTopK(parseInt(e.target.value))}
          >
            <option value={5}>Top 5</option>
            <option value={10}>Top 10</option>
            <option value={20}>Top 20</option>
            <option value={30}>Top 30</option>
            <option value={40}>Top 40</option>
            <option value={50}>Top 50</option>
          </select>
          <button onClick={load} className="btn-primary" disabled={loading}>
            {loading ? "Loading..." : "🔄 Refresh"}
          </button>
        </div>
      </div>

      {error && (
        <div className="card bg-amber-50 text-amber-800 border border-amber-200">
          {error}
        </div>
      )}

      {generatedAt && (
        <div className="text-xs text-slate-500 flex flex-wrap items-center gap-3">
          <span>Generated at: {new Date(generatedAt).toLocaleString()}</span>
          {cacheHit === true && (
            <span className="badge bg-emerald-50 text-emerald-700 border border-emerald-200">
              ⚡ Served from cache
            </span>
          )}
          {cacheHit === false && (
            <span className="badge bg-slate-50 text-slate-600 border border-slate-200">
              🧮 Recomputed
            </span>
          )}
        </div>
      )}

      {loading ? (
        <div className="card text-center text-slate-500">
          Loading your recommendations...
        </div>
      ) : recs.length === 0 ? (
        <div className="card text-center text-slate-500">
          No recommendations yet. Add at least one research interest or
          publication on your profile, then refresh this page.
        </div>
      ) : (
        <div className="grid gap-4">
          {recs.map((r, idx) => (
            <div key={r.funding.id} className="card hover:shadow-md transition">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-16 h-16 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex flex-col items-center justify-center text-white">
                  <div className="text-xl font-bold">#{idx + 1}</div>
                  <div className="text-[10px] opacity-90">rank</div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2 flex-wrap">
                    <h3 className="font-semibold text-slate-800">
                      {r.funding.title}
                    </h3>
                    <div className="text-right flex-shrink-0">
                      <div className="text-2xl font-bold text-primary-600">
                        {r.matching_percentage}%
                      </div>
                      <div className="text-xs text-slate-500">overall match</div>
                    </div>
                  </div>
                  <div className="text-sm text-slate-500 mt-1">
                    {r.funding.organization} · {r.funding.country}
                  </div>
                  <p className="text-sm text-slate-600 mt-2 line-clamp-3">
                    {r.funding.description}
                  </p>
                  <div className="flex flex-wrap gap-2 mt-3">
                    {r.funding.research_domain && (
                      <span className="badge-primary">
                        {r.funding.research_domain}
                      </span>
                    )}
                    {r.funding.funding_type && (
                      <span className="badge-purple uppercase">
                        {r.funding.funding_type}
                      </span>
                    )}
                    <span className="badge-success">
                      Publications: {(r.similarity_score * 100).toFixed(1)}%
                    </span>
                    {r.interest_score > 0 && (
                      <span className="badge-primary">
                        Interests: {(r.interest_score * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                  {r.matching_keywords && r.matching_keywords.length > 0 && (
                    <div className="mt-2">
                      <span className="text-xs text-slate-500">
                        Matching keywords:{" "}
                      </span>
                      {r.matching_keywords.map((k, i) => (
                        <span
                          key={i}
                          className="text-xs text-primary-700 mr-1"
                        >
                          #{k}
                        </span>
                      ))}
                    </div>
                  )}
                  {r.explanation && (
                    <div className="mt-3 p-3 bg-slate-50 rounded-lg text-xs text-slate-600 whitespace-pre-line">
                      💡 {r.explanation}
                    </div>
                  )}
                  {r.funding.url && (
                    <a
                      href={r.funding.url}
                      target="_blank"
                      rel="noreferrer"
                      className="btn-primary text-sm mt-3 inline-block"
                    >
                      Apply Now →
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

