import React, { useEffect, useMemo, useRef, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { patentDashboardAPI, savedPatentsAPI } from "../services/api.js";
import { useToasts, ToastStack } from "../components/admin/ui.jsx";
import { useSavedPatents } from "../context/SavedPatentsContext.jsx";
import {
  getCachedSection,
  setCachedSection,
  invalidateSection,
  invalidatePatent,
} from "../utils/patentAIcache.js";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { Bar, Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

// ---------------------------------------------------------------------------
// Theme — same palette as the rest of the app so the dashboard blends in.
// ---------------------------------------------------------------------------
const CHART_PALETTE = [
  "#3b82f6",
  "#8b5cf6",
  "#10b981",
  "#f59e0b",
  "#ef4444",
  "#06b6d4",
  "#ec4899",
  "#6366f1",
];

// Tone → colour map for score bars / cards.  Mirrors the rest of the app.
function scoreTone(score) {
  if (score == null || Number.isNaN(score)) return "slate";
  if (score >= 75) return "green";
  if (score >= 50) return "primary";
  if (score >= 30) return "amber";
  return "red";
}

function fmtPct(v) {
  if (v == null || Number.isNaN(v)) return "—";
  return `${Math.round(Number(v))}%`;
}

function fmtNum(v) {
  if (v == null) return "—";
  return Number(v).toLocaleString();
}

function fmtDate(iso) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleDateString();
  } catch {
    return iso;
  }
}

// ---------------------------------------------------------------------------
// Generic helpers
// ---------------------------------------------------------------------------

/**
 * Tiny hook that fetches one section's payload, caches it in localStorage,
 * and exposes a manual refresh action.  Falls back to a graceful error
 * object instead of throwing so the dashboard never breaks on a single
 * failed section.
 */
function useSection(patentNumber, section, fetcher, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = async (force = false) => {
    if (!patentNumber) return;
    if (!force) {
      const cached = getCachedSection(patentNumber, section);
      if (cached?.data) {
        setData(cached.data);
        setLoading(false);
      }
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetcher();
      const payload = res?.data ?? res;
      setData(payload);
      setCachedSection(patentNumber, section, payload);
    } catch (exc) {
      setError(exc?.response?.data?.detail || exc?.message || "Failed to load");
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  };

  useEffect(() => {
    load(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [patentNumber, ...deps]);

  return { data, loading, error, refresh: () => load(true) };
}

/** Inline loading skeleton — keeps the page from looking empty. */
function Skeleton({ lines = 3 }) {
  return (
    <div className="space-y-2 animate-pulse">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="h-3 bg-slate-200 rounded"
          style={{ width: `${100 - i * 10}%` }}
        />
      ))}
    </div>
  );
}

/** Collapsible AI card — header is always visible; body collapses on click. */
function CollapsibleCard({ title, icon, badge, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="card">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">{icon}</span>
          <h3 className="font-semibold text-slate-800">{title}</h3>
          {badge}
        </div>
        <span className="text-slate-400 text-sm">{open ? "▾" : "▸"}</span>
      </button>
      {open && <div className="mt-4">{children}</div>}
    </div>
  );
}

/** Animated horizontal progress bar used by the innovation score section. */
function ProgressBar({ value, label, tone }) {
  const safe = Math.max(0, Math.min(100, Number(value) || 0));
  const toneClass = {
    primary: "bg-primary-500",
    green: "bg-green-500",
    amber: "bg-amber-500",
    red: "bg-red-500",
    purple: "bg-purple-500",
    slate: "bg-slate-400",
  }[tone || scoreTone(safe)];
  return (
    <div>
      <div className="flex items-center justify-between text-sm mb-1">
        <span className="font-medium text-slate-700">{label}</span>
        <span className="font-semibold text-slate-700">{safe.toFixed(0)}%</span>
      </div>
      <div className="h-2.5 bg-slate-100 rounded-full overflow-hidden">
        <div
          className={`h-full ${toneClass} transition-all duration-700`}
          style={{ width: `${safe}%` }}
        />
      </div>
    </div>
  );
}

/** Pill badge used by the overview metadata grid. */
function MetaTile({ icon, label, value, tone = "slate" }) {
  const tones = {
    slate: "bg-slate-50 border-slate-200 text-slate-700",
    primary: "bg-primary-50 border-primary-200 text-primary-800",
    purple: "bg-purple-50 border-purple-200 text-purple-800",
    green: "bg-green-50 border-green-200 text-green-800",
    amber: "bg-amber-50 border-amber-200 text-amber-800",
    red: "bg-red-50 border-red-200 text-red-800",
  };
  return (
    <div className={`p-3 rounded-lg border ${tones[tone] || tones.slate}`}>
      <div className="flex items-center gap-1 text-xs opacity-75">
        <span>{icon}</span>
        <span>{label}</span>
      </div>
      <div className="font-semibold mt-1 text-sm break-words">{value || "—"}</div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// 1. Patent Overview
// ---------------------------------------------------------------------------
function PatentOverview({ data, loading, error }) {
  if (loading && !data) return <div className="card"><Skeleton lines={4} /></div>;
  if (error && !data) {
    return (
      <div className="card bg-red-50 border-red-200 text-red-700">{error}</div>
    );
  }
  if (!data) return null;

  const p = data.patent || {};
  const score = data.innovation_score || {};
  const innovation = score.final_score != null ? Math.round(score.final_score * 100) : null;
  const inventors = p.inventors || (p.applicants || []).join(", ");
  return (
    <div className="card">
      <div className="flex flex-wrap items-start justify-between gap-4 mb-4">
        <div className="min-w-0">
          <div className="text-xs uppercase tracking-wide text-slate-400 mb-1">
            Patent Number · {p.patent_number || "—"}
          </div>
          <h2 className="text-2xl font-bold text-slate-900 break-words">
            {p.title || "Untitled patent"}
          </h2>
          <div className="flex flex-wrap gap-2 mt-3">
            {p.country && <span className="badge-primary">🌍 {p.country}</span>}
            {p.legal_status && <span className="badge-success">⚖️ {p.legal_status}</span>}
            {p.technology_area && <span className="badge-purple">🔬 {p.technology_area}</span>}
            {p.source && (
              <span className="badge bg-slate-100 text-slate-700">📡 {p.source}</span>
            )}
            {innovation != null && (
              <span className="badge-warning">⭐ Innovation {innovation}%</span>
            )}
            {data.commercialization_label && (
              <span className="badge bg-blue-100 text-blue-800">
                💼 {data.commercialization_label}
              </span>
            )}
          </div>
        </div>
      </div>

      {p.abstract && (
        <p className="text-sm text-slate-700 leading-relaxed border-l-4 border-primary-200 pl-3 mb-4">
          {p.abstract}
        </p>
      )}

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        <MetaTile icon="👤" label="Inventor(s)" value={inventors} tone="primary" />
        <MetaTile icon="🏢" label="Assignee" value={p.assignee} tone="purple" />
        <MetaTile icon="📅" label="Filing Date" value={fmtDate(p.filing_date)} />
        <MetaTile icon="📅" label="Publication" value={fmtDate(p.publication_date)} />
        <MetaTile icon="🗓️" label="Year" value={fmtNum(p.publication_year)} />
        <MetaTile icon="⚖️" label="Status" value={p.legal_status} tone="green" />
        <MetaTile icon="🌐" label="Country" value={p.country} />
        <MetaTile icon="🔬" label="Tech Domain" value={p.technology_area} tone="purple" />
        <MetaTile icon="📡" label="Source" value={p.source} />
        <MetaTile icon="📚" label="Citations" value={fmtNum(p.citation_count)} tone="amber" />
        {p.classification && (
          <MetaTile icon="🏷️" label="Classification" value={p.classification} />
        )}
        {p.family_size != null && (
          <MetaTile
            icon="👪"
            label="Family Size"
            value={fmtNum(p.family_size)}
            tone="primary"
          />
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// 2. AI Patent Summary
// ---------------------------------------------------------------------------
function AISummaryCard({ data, loading, error, onExplainAgain }) {
  if (loading && !data) return <div className="card"><Skeleton lines={6} /></div>;
  if (error && !data)
    return <div className="card bg-red-50 border-red-200 text-red-700">{error}</div>;
  if (!data) return null;

  const Bullets = ({ items, empty }) =>
    (items || []).length ? (
      <ul className="list-disc pl-5 space-y-1 text-sm text-slate-700">
        {items.map((it, i) => (
          <li key={i}>{it}</li>
        ))}
      </ul>
    ) : (
      <div className="text-sm text-slate-400 italic">{empty || "Not provided."}</div>
    );

  return (
    <CollapsibleCard
      title="AI Patent Summary"
      icon="🤖"
      badge={
        <span className="badge bg-primary-100 text-primary-800 ml-2">OpenRouter AI</span>
      }
      defaultOpen
    >
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <h4 className="font-semibold text-slate-700 mb-1">Simple Explanation</h4>
          <p className="text-sm text-slate-700">
            {data.simple_explanation || data.raw || "Not provided."}
          </p>
        </div>
        <div>
          <h4 className="font-semibold text-slate-700 mb-1">Technical Explanation</h4>
          <p className="text-sm text-slate-700">
            {data.technical_explanation || data.raw || "Not provided."}
          </p>
        </div>
        <div>
          <h4 className="font-semibold text-slate-700 mb-1">Problem Solved</h4>
          <p className="text-sm text-slate-700">{data.problem || "Not provided."}</p>
        </div>
        <div>
          <h4 className="font-semibold text-slate-700 mb-1">Key Innovation</h4>
          <p className="text-sm text-slate-700">{data.innovation || "Not provided."}</p>
        </div>
        <div>
          <h4 className="font-semibold text-slate-700 mb-1">Advantages</h4>
          <Bullets items={data.advantages} empty="No advantages listed." />
        </div>
        <div>
          <h4 className="font-semibold text-slate-700 mb-1">Limitations</h4>
          <Bullets items={data.limitations} empty="No limitations listed." />
        </div>
        <div className="md:col-span-2">
          <h4 className="font-semibold text-slate-700 mb-1">Future Improvements</h4>
          <Bullets
            items={data.future_improvements}
            empty="No future improvements listed."
          />
        </div>
      </div>
      <div className="mt-4 flex justify-end">
        <button className="btn-secondary" onClick={onExplainAgain}>
          🔄 Explain Again
        </button>
      </div>
    </CollapsibleCard>
  );
}

// ---------------------------------------------------------------------------
// 3. AI Innovation Analysis
// ---------------------------------------------------------------------------
function InnovationScores({ data, loading, error }) {
  if (loading && !data)
    return (
      <div className="card">
        <Skeleton lines={4} />
      </div>
    );
  if (error && !data)
    return <div className="card bg-red-50 border-red-200 text-red-700">{error}</div>;
  if (!data) return null;

  // Deterministic scores from the DB live in data.deterministic; AI verdict
  // (when present) lives in data.ai_verdict.
  const ai = data.ai_verdict && !data.ai_verdict.error ? data.ai_verdict : null;
  const scores = [
    { key: "innovation_score", label: "Innovation Score" },
    { key: "novelty_score", label: "Novelty" },
    { key: "commercial_potential", label: "Commercial Potential" },
    { key: "research_difficulty", label: "Research Difficulty" },
    { key: "technology_maturity", label: "Technology Maturity" },
    { key: "future_demand", label: "Future Demand" },
    { key: "investment_potential", label: "Investment Potential" },
  ];

  return (
    <CollapsibleCard
      title="AI Innovation Analysis"
      icon="⭐"
      badge={
        ai ? (
          <span className="badge bg-purple-100 text-purple-800 ml-2">AI verdict</span>
        ) : null
      }
    >
      {!ai && (
        <div className="text-sm text-slate-500 italic mb-4">
          The AI verdict was not requested.  Scores below come from the
          deterministic innovation engine that scores every patent in the
          corpus.
        </div>
      )}
      <div className="grid md:grid-cols-2 gap-x-8 gap-y-4">
        {scores.map((s) => (
          <ProgressBar
            key={s.key}
            label={s.label}
            value={ai ? ai[s.key] : (data.deterministic?.[s.key] ?? 0) * 100}
            tone={scoreTone(ai ? ai[s.key] : (data.deterministic?.[s.key] ?? 0) * 100)}
          />
        ))}
      </div>
      {ai?.rationale && (
        <p className="mt-4 text-sm text-slate-600 italic border-l-4 border-purple-200 pl-3">
          {ai.rationale}
        </p>
      )}
      {data.ai_verdict?.error && (
        <p className="mt-3 text-sm text-amber-700">
          AI verdict unavailable: {data.ai_verdict.error}
        </p>
      )}
    </CollapsibleCard>
  );
}

// ---------------------------------------------------------------------------
// 4. Technology Gap Analysis
// ---------------------------------------------------------------------------
function TechGap({ data, loading, error }) {
  if (loading && !data)
    return <div className="card"><Skeleton lines={4} /></div>;
  if (error && !data)
    return <div className="card bg-red-50 border-red-200 text-red-700">{error}</div>;
  if (!data) return null;

  const sections = [
    { key: "missing_features", title: "Missing Features", icon: "🧩", tone: "red" },
    { key: "untapped_opportunities", title: "Untapped Opportunities", icon: "💡", tone: "amber" },
    { key: "possible_improvements", title: "Possible Improvements", icon: "🛠️", tone: "primary" },
    { key: "future_research_directions", title: "Future Research Directions", icon: "🚀", tone: "purple" },
    { key: "emerging_combinations", title: "Emerging Technologies to Combine", icon: "🔗", tone: "green" },
  ];

  const tones = {
    red: "border-red-200 bg-red-50",
    amber: "border-amber-200 bg-amber-50",
    primary: "border-primary-200 bg-primary-50",
    purple: "border-purple-200 bg-purple-50",
    green: "border-green-200 bg-green-50",
  };

  return (
    <CollapsibleCard
      title="Technology Gap Analysis"
      icon="🔍"
      badge={
        <span className="badge bg-primary-100 text-primary-800 ml-2">OpenRouter AI</span>
      }
    >
      {data.error && !data.missing_features?.length && (
        <div className="text-sm text-amber-700 mb-3">{data.error}</div>
      )}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sections.map((s) => (
          <div key={s.key} className={`rounded-lg border p-4 ${tones[s.tone]}`}>
            <div className="flex items-center gap-2 mb-2 font-semibold text-slate-800">
              <span>{s.icon}</span>
              <span>{s.title}</span>
            </div>
            <ul className="text-sm text-slate-700 space-y-1 list-disc pl-5">
              {(data[s.key] || []).map((it, i) => (
                <li key={i}>{it}</li>
              ))}
              {(!data[s.key] || data[s.key].length === 0) && (
                <li className="list-none italic text-slate-400">Not provided.</li>
              )}
            </ul>
          </div>
        ))}
      </div>
    </CollapsibleCard>
  );
}

// ---------------------------------------------------------------------------
// 5. Commercial Applications
// ---------------------------------------------------------------------------
function CommercialApplications({ data, loading, error }) {
  if (loading && !data)
    return <div className="card"><Skeleton lines={4} /></div>;
  if (error && !data)
    return <div className="card bg-red-50 border-red-200 text-red-700">{error}</div>;
  if (!data) return null;

  const apps = data.applications || data;
  return (
    <CollapsibleCard
      title="Commercial Applications"
      icon="💼"
      badge={
        <span className="badge bg-primary-100 text-primary-800 ml-2">OpenRouter AI</span>
      }
    >
      {data.error && (!apps || apps.length === 0) && (
        <div className="text-sm text-amber-700 mb-3">{data.error}</div>
      )}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {(apps || []).map((a, i) => (
          <div key={i} className="rounded-lg border border-slate-200 p-4 hover:shadow-sm transition">
            <div className="flex items-center gap-2 mb-1">
              <span className="badge-primary">{a.industry || "Industry"}</span>
            </div>
            <p className="text-sm text-slate-700 mt-2">{a.reason}</p>
            {a.example_use_case && (
              <p className="text-xs text-slate-500 mt-2 italic">
                Example: {a.example_use_case}
              </p>
            )}
          </div>
        ))}
        {(!apps || apps.length === 0) && (
          <div className="text-sm text-slate-400 italic">
            No applications returned by the AI.
          </div>
        )}
      </div>
    </CollapsibleCard>
  );
}

// ---------------------------------------------------------------------------
// 6. Related Funding
// ---------------------------------------------------------------------------
function RelatedFunding({ data, loading, error }) {
  if (loading && !data)
    return <div className="card"><Skeleton lines={3} /></div>;
  if (error && !data)
    return <div className="card bg-red-50 border-red-200 text-red-700">{error}</div>;
  if (!data) return null;

  const items = data.items || [];
  return (
    <CollapsibleCard title="Related Funding" icon="💰" defaultOpen>
      {items.length === 0 ? (
        <div className="text-sm text-slate-400 italic">
          No closely matching grants found in the funding corpus.
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          {items.map((f) => (
            <div
              key={f.funding_id}
              className="border border-slate-200 rounded-lg p-4 hover:shadow-sm transition"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <h4 className="font-semibold text-slate-800 break-words">
                    {f.title}
                  </h4>
                  <div className="text-xs text-slate-500 mt-1">
                    {f.organization || "Unknown org"}
                    {f.country ? ` · ${f.country}` : ""}
                  </div>
                </div>
                <span className="badge-primary whitespace-nowrap">
                  {fmtNum(f.match_score)}% match
                </span>
              </div>
              <div className="mt-3 flex flex-wrap gap-2 text-xs">
                <span className="badge bg-slate-100 text-slate-700">
                  {f.eligibility_hint || "Eligibility n/a"}
                </span>
                {f.application_deadline && (
                  <span className="badge bg-amber-100 text-amber-800">
                    ⏰ {fmtDate(f.application_deadline)}
                  </span>
                )}
                {f.research_domain && (
                  <span className="badge bg-purple-100 text-purple-800">
                    {f.research_domain}
                  </span>
                )}
              </div>
              <div className="mt-3 flex items-center justify-end">
                {f.url ? (
                  <a
                    href={f.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-primary text-xs"
                  >
                    Apply ↗
                  </a>
                ) : (
                  <button className="btn-primary text-xs" disabled>
                    Apply
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </CollapsibleCard>
  );
}

// ---------------------------------------------------------------------------
// 7. Related Publications
// ---------------------------------------------------------------------------
function RelatedPublications({ data, loading, error }) {
  if (loading && !data)
    return <div className="card"><Skeleton lines={3} /></div>;
  if (error && !data)
    return <div className="card bg-red-50 border-red-200 text-red-700">{error}</div>;
  if (!data) return null;

  const items = data.items || [];
  return (
    <CollapsibleCard title="Related Publications" icon="📚" defaultOpen>
      {items.length === 0 ? (
        <div className="text-sm text-slate-400 italic">
          No related publications indexed for this patent yet.
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((p) => (
            <div
              key={p.id || p.doi || p.title}
              className="border border-slate-200 rounded-lg p-4 hover:shadow-sm transition"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <h4 className="font-semibold text-slate-800 break-words">{p.title}</h4>
                  <div className="text-xs text-slate-500 mt-1">
                    {p.authors || "Unknown authors"}
                    {p.year ? ` · ${p.year}` : ""}
                  </div>
                </div>
                <div className="flex flex-col items-end gap-1">
                  {p.similarity != null && (
                    <span className="badge bg-primary-100 text-primary-800">
                      {Math.round((p.similarity || 0) * 100)}% similar
                    </span>
                  )}
                  {p.citation_count != null && (
                    <span className="badge bg-slate-100 text-slate-700">
                      📚 {fmtNum(p.citation_count)} citations
                    </span>
                  )}
                </div>
              </div>
              <div className="mt-3 flex justify-end">
                {p.url ? (
                  <a
                    href={p.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-secondary text-xs"
                  >
                    Open ↗
                  </a>
                ) : (
                  <button className="btn-secondary text-xs" disabled>
                    Open
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </CollapsibleCard>
  );
}

// ---------------------------------------------------------------------------
// 8. Similar Patents
// ---------------------------------------------------------------------------
function SimilarPatents({ data, loading, error, onCompare }) {
  if (loading && !data)
    return <div className="card"><Skeleton lines={3} /></div>;
  if (error && !data)
    return <div className="card bg-red-50 border-red-200 text-red-700">{error}</div>;
  if (!data) return null;

  const items = data.items || [];
  return (
    <CollapsibleCard title="Similar Patents" icon="🔗" defaultOpen>
      {items.length === 0 ? (
        <div className="text-sm text-slate-400 italic">
          No similar patents identified in the corpus.
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          {items.map((p) => (
            <div
              key={p.patent_id || p.patent_number}
              className="border border-slate-200 rounded-lg p-4 hover:shadow-sm transition"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <h4 className="font-semibold text-slate-800 break-words">
                    {p.title}
                  </h4>
                  <div className="text-xs text-slate-500 mt-1">
                    {p.patent_number} · {p.source || "—"}
                    {p.publication_year ? ` · ${p.publication_year}` : ""}
                  </div>
                </div>
                <span className="badge bg-primary-100 text-primary-800">
                  {Math.round((p.similarity || 0) * 100)}% similar
                </span>
              </div>
              {p.assignee && (
                <div className="text-xs text-slate-500 mt-2">
                  Assignee: {p.assignee}
                </div>
              )}
              <div className="mt-3 flex justify-end gap-2">
                {p.url && (
                  <a
                    href={p.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-secondary text-xs"
                  >
                    Open ↗
                  </a>
                )}
                <button
                  className="btn-primary text-xs"
                  onClick={() => onCompare && onCompare(p)}
                >
                  Compare
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </CollapsibleCard>
  );
}

// ---------------------------------------------------------------------------
// 9. Technology Trend
// ---------------------------------------------------------------------------
function TechnologyTrend({ data, loading, error }) {
  if (loading && !data)
    return <div className="card"><Skeleton lines={4} /></div>;
  if (error && !data)
    return <div className="card bg-red-50 border-red-200 text-red-700">{error}</div>;
  if (!data) return null;

  const filings = data.filings_by_year || [];
  const citations = data.citation_growth || [];
  const adoption = data.adoption || [];
  const countries = data.top_countries || [];
  const assignees = data.top_assignees || [];
  const inventors = data.top_inventors || [];

  const filingsChart = {
    labels: filings.map((r) => r.year),
    datasets: [
      {
        label: "New filings",
        data: filings.map((r) => r.count),
        backgroundColor: CHART_PALETTE[0],
        borderRadius: 4,
      },
    ],
  };

  const citationChart = {
    labels: citations.map((r) => r.year),
    datasets: [
      {
        label: "Cumulative citations",
        data: citations.map((r) => r.cumulative_citations),
        borderColor: CHART_PALETTE[2],
        backgroundColor: "rgba(16, 185, 129, 0.15)",
        fill: true,
        tension: 0.3,
      },
    ],
  };

  const adoptionChart = {
    labels: adoption.map((r) => r.year),
    datasets: [
      {
        label: "Rolling 3-year filings",
        data: adoption.map((r) => r.rolling_3y_filings),
        backgroundColor: CHART_PALETTE[1],
        borderRadius: 4,
      },
    ],
  };

  const topList = (rows, labelKey) => (
    <ul className="space-y-2">
      {rows.length === 0 && (
        <li className="text-sm text-slate-400 italic">No data.</li>
      )}
      {rows.map((r) => (
        <li
          key={`${labelKey}-${r[labelKey]}`}
          className="flex items-center justify-between text-sm"
        >
          <span className="text-slate-700 truncate">{r[labelKey]}</span>
          <span className="badge-primary">{r.count}</span>
        </li>
      ))}
    </ul>
  );

  return (
    <CollapsibleCard
      title="Technology Trend"
      icon="📈"
      badge={
        data.technology_area ? (
          <span className="badge bg-purple-100 text-purple-800 ml-2">
            {data.technology_area}
          </span>
        ) : null
      }
    >
      <div className="grid md:grid-cols-2 gap-4">
        <div className="rounded-lg border border-slate-200 p-4">
          <h4 className="font-semibold text-slate-700 mb-2">
            Patent Filings Over Years
          </h4>
          <div className="h-48">
            {filings.length > 0 ? (
              <Bar
                data={filingsChart}
                options={{ maintainAspectRatio: false, responsive: true }}
              />
            ) : (
              <div className="h-full flex items-center justify-center text-sm text-slate-400 italic">
                No filings for this area yet.
              </div>
            )}
          </div>
        </div>
        <div className="rounded-lg border border-slate-200 p-4">
          <h4 className="font-semibold text-slate-700 mb-2">Citation Growth</h4>
          <div className="h-48">
            {citations.length > 0 ? (
              <Line
                data={citationChart}
                options={{ maintainAspectRatio: false, responsive: true }}
              />
            ) : (
              <div className="h-full flex items-center justify-center text-sm text-slate-400 italic">
                No citation history yet.
              </div>
            )}
          </div>
        </div>
        <div className="rounded-lg border border-slate-200 p-4">
          <h4 className="font-semibold text-slate-700 mb-2">
            Technology Adoption
          </h4>
          <div className="h-48">
            {adoption.length > 0 ? (
              <Line
                data={adoptionChart}
                options={{ maintainAspectRatio: false, responsive: true }}
              />
            ) : (
              <div className="h-full flex items-center justify-center text-sm text-slate-400 italic">
                Not enough history.
              </div>
            )}
          </div>
        </div>
        <div className="rounded-lg border border-slate-200 p-4">
          <h4 className="font-semibold text-slate-700 mb-2">Top Countries</h4>
          {topList(countries, "country")}
        </div>
        <div className="rounded-lg border border-slate-200 p-4">
          <h4 className="font-semibold text-slate-700 mb-2">Top Organizations</h4>
          {topList(assignees, "assignee")}
        </div>
        <div className="rounded-lg border border-slate-200 p-4">
          <h4 className="font-semibold text-slate-700 mb-2">Top Inventors</h4>
          {topList(inventors, "inventor")}
        </div>
      </div>
    </CollapsibleCard>
  );
}

// ---------------------------------------------------------------------------
// 10. AI Recommendations
// ---------------------------------------------------------------------------
function AIRecommendations({ data, loading, error }) {
  if (loading && !data)
    return (
      <div className="card bg-gradient-to-br from-primary-50 to-purple-50 border-primary-200">
        <Skeleton lines={4} />
      </div>
    );
  if (error && !data)
    return <div className="card bg-red-50 border-red-200 text-red-700">{error}</div>;
  if (!data) return null;

  const yesNo = (val) => {
    if (!val) return "slate";
    const v = String(val).toLowerCase();
    if (v.startsWith("yes") || v.startsWith("high")) return "green";
    if (v.startsWith("no") || v.startsWith("low")) return "red";
    return "amber";
  };

  const toneBg = {
    green: "bg-green-100 text-green-800",
    amber: "bg-amber-100 text-amber-800",
    red: "bg-red-100 text-red-800",
    slate: "bg-slate-100 text-slate-700",
  };

  return (
    <div className="card bg-gradient-to-br from-primary-50 via-white to-purple-50 border-primary-200">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-xl">💎</span>
        <h3 className="font-bold text-slate-800">AI Recommendations</h3>
        <span className="badge bg-primary-100 text-primary-800 ml-auto">
          OpenRouter AI
        </span>
      </div>
      {data.error && !data.overall_recommendation && (
        <div className="text-sm text-amber-700 mb-3">{data.error}</div>
      )}
      <div className="grid md:grid-cols-3 gap-3 mb-4">
        <div className={`p-3 rounded-lg ${toneBg[yesNo(data.continue_in_area)]}`}>
          <div className="text-xs uppercase tracking-wide opacity-75">
            Continue in Area
          </div>
          <div className="font-semibold mt-1">{data.continue_in_area || "—"}</div>
        </div>
        <div className={`p-3 rounded-lg ${toneBg[yesNo(data.commercialization_recommended)]}`}>
          <div className="text-xs uppercase tracking-wide opacity-75">
            Commercialize?
          </div>
          <div className="font-semibold mt-1">
            {data.commercialization_recommended || "—"}
          </div>
        </div>
        <div className={`p-3 rounded-lg ${toneBg[yesNo(data.expected_future_demand)]}`}>
          <div className="text-xs uppercase tracking-wide opacity-75">
            Future Demand
          </div>
          <div className="font-semibold mt-1">
            {data.expected_future_demand || "—"}
          </div>
        </div>
        <div className={`p-3 rounded-lg ${toneBg[yesNo(data.funding_possibility)]}`}>
          <div className="text-xs uppercase tracking-wide opacity-75">
            Funding Possibility
          </div>
          <div className="font-semibold mt-1">
            {data.funding_possibility || "—"}
          </div>
        </div>
      </div>
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <h4 className="font-semibold text-slate-700 mb-1">What to Improve</h4>
          <ul className="list-disc pl-5 text-sm text-slate-700 space-y-1">
            {(data.improvements || []).map((it, i) => (
              <li key={i}>{it}</li>
            ))}
            {(!data.improvements || data.improvements.length === 0) && (
              <li className="list-none italic text-slate-400">Not provided.</li>
            )}
          </ul>
        </div>
        <div>
          <h4 className="font-semibold text-slate-700 mb-1">
            Suggested Collaborations
          </h4>
          <ul className="list-disc pl-5 text-sm text-slate-700 space-y-1">
            {(data.suggested_collaborations || []).map((it, i) => (
              <li key={i}>{it}</li>
            ))}
            {(!data.suggested_collaborations ||
              data.suggested_collaborations.length === 0) && (
              <li className="list-none italic text-slate-400">Not provided.</li>
            )}
          </ul>
        </div>
      </div>
      {data.overall_recommendation && (
        <div className="mt-4 p-4 rounded-lg bg-white border border-primary-200 text-sm text-slate-700">
          <span className="font-semibold text-primary-700">Overall: </span>
          {data.overall_recommendation}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Action bar — Save, Download, Export, Compare, Open Original, Share, etc.
// ---------------------------------------------------------------------------
function ActionBar({
  patent,
  onExplainAgain,
  onRefresh,
  onFindFunding,
  onRelatedPapers,
  onCompare,
  compareCount,
}) {
  const { isSaved, refresh: refreshSaved, addLocal, removeLocal } =
    useSavedPatents();
  const { toasts, pushToast, dismissToast } = useToasts();
  const [savedId, setSavedId] = useState(null);
  const [busy, setBusy] = useState(false);

  const saved = patent ? isSaved(patent.patent_number, patent.source) : false;

  // When the displayed patent changes (or the saved-state flips), look
  // up its DB row id so we can DELETE by id. Falls back gracefully if
  // the list cache is still warming.
  useEffect(() => {
    let cancelled = false;
    async function loadSavedId() {
      if (!patent?.patent_number || !patent?.source || !saved) {
        setSavedId(null);
        return;
      }
      try {
        const res = await savedPatentsAPI.list({
          page: 1,
          page_size: 100,
          search: patent.patent_number,
        });
        if (cancelled) return;
        const match = (res.data?.items || []).find(
          (it) =>
            it.patent_number === patent.patent_number &&
            it.source === patent.source
        );
        setSavedId(match?.id ?? null);
      } catch {
        setSavedId(null);
      }
    }
    loadSavedId();
    return () => {
      cancelled = true;
    };
  }, [patent?.patent_number, patent?.source, saved]);

  function buildSnapshot() {
    if (!patent) return null;
    return {
      patent_number: patent.patent_number,
      title: patent.title || "",
      source: patent.source || "the_lens",
      inventors: patent.inventors,
      assignee: patent.assignee,
      technology_area: patent.technology_area,
      publication_date: patent.publication_date,
      publication_year: patent.publication_year,
      citation_count: patent.citation_count ?? 0,
      url: patent.url,
      lens_url: patent.lens_url,
      abstract: patent.abstract,
    };
  }

  async function savePatent() {
    if (busy) return;
    setBusy(true);
    try {
      if (saved) {
        if (savedId) {
          await savedPatentsAPI.remove(savedId);
          removeLocal(savedId, patent);
        } else {
          // Defensive: the patent is "saved" by isSaved() but the id is
          // missing. POST first so we have a row, then remove it so the
          // button state returns to "Save Patent".
          const created = await savedPatentsAPI.create(buildSnapshot());
          await savedPatentsAPI.remove(created.data.id);
          removeLocal(created.data.id, patent);
        }
        pushToast("Removed from saved", "success");
      } else {
        const res = await savedPatentsAPI.create(buildSnapshot());
        setSavedId(res.data.id);
        addLocal(res.data);
        pushToast("Patent saved", "success");
      }
      // Revalidate the count + keys so /saved-patents and the Dashboard
      // KPI pick up the change immediately.
      refreshSaved();
    } catch (err) {
      pushToast(
        err.response?.data?.detail ||
          "Could not update saved patents",
        "error"
      );
    } finally {
      setBusy(false);
    }
  }

  function downloadJson() {
    if (!patent) return;
    const blob = new Blob([JSON.stringify(patent, null, 2)], {
      type: "application/json",
    });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `patent-${patent.patent_number}.json`;
    a.click();
  }

  function exportReport() {
    if (!patent) return;
    // A minimal printable HTML export — opens in a new tab so the user can
    // save as PDF via the browser dialog.
    const html = `<!doctype html><html><head><title>Patent ${patent.patent_number}</title></head>
<body style="font-family:Inter,sans-serif;padding:24px;line-height:1.5">
<h1>${patent.title || ""}</h1>
<p><b>Patent number:</b> ${patent.patent_number || ""}</p>
<p><b>Assignee:</b> ${patent.assignee || "—"}</p>
<p><b>Inventors:</b> ${patent.inventors || "—"}</p>
<p><b>Country:</b> ${patent.country || "—"}</p>
<p><b>Publication year:</b> ${patent.publication_year || "—"}</p>
<p><b>Technology area:</b> ${patent.technology_area || "—"}</p>
<p><b>Citations:</b> ${patent.citation_count ?? 0}</p>
<h3>Abstract</h3>
<p>${patent.abstract || "—"}</p>
<p><i>Generated ${new Date().toLocaleString()}</i></p>
</body></html>`;
    const win = window.open("", "_blank");
    if (win) {
      win.document.write(html);
      win.document.close();
    }
  }

  function openOriginal() {
    if (!patent) return;
    const url = patent.url || patent.lens_url;
    if (url) window.open(url, "_blank", "noopener,noreferrer");
  }

  function share() {
    const url = window.location.href;
    if (navigator.share) {
      navigator
        .share({ title: patent?.title || "Patent", url })
        .catch(() => {});
    } else if (navigator.clipboard) {
      navigator.clipboard.writeText(url).catch(() => {});
      pushToast("Link copied", "success");
    }
  }

  return (
    <div className="card">
      <ToastStack toasts={toasts} onDismiss={dismissToast} />
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap gap-2">
          <button
            className="btn-primary"
            onClick={savePatent}
            disabled={busy}
            aria-pressed={saved}
          >
            {saved ? "★ Saved" : "☆ Save Patent"}
          </button>
          <button className="btn-secondary" onClick={downloadJson}>
            ⬇ Download JSON
          </button>
          <button className="btn-secondary" onClick={exportReport}>
            🖨 Export Report
          </button>
          <button
            className="btn-secondary"
            onClick={openOriginal}
            disabled={!patent || (!patent.url && !patent.lens_url)}
          >
            🌐 Open Original
          </button>
          <button className="btn-secondary" onClick={share}>
            🔗 Share
          </button>
          <button className="btn-secondary" onClick={onExplainAgain}>
            🔄 Explain Again
          </button>
          <button className="btn-secondary" onClick={onFindFunding}>
            💰 Find Funding
          </button>
          <button className="btn-secondary" onClick={onRelatedPapers}>
            📚 Related Papers
          </button>
        </div>
        <div className="flex items-center gap-2">
          <button className="btn-ghost text-xs" onClick={onRefresh} title="Refresh all sections">
            🔄 Refresh
          </button>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Compare drawer — opens when the user selects patents to compare.
// ---------------------------------------------------------------------------
function CompareDrawer({ patents, onClose, onRemove }) {
  if (!patents || patents.length === 0) return null;
  return (
    <div className="fixed bottom-0 inset-x-0 z-30 bg-white border-t border-slate-200 shadow-lg animate-slide-up p-4">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-slate-800">
            Compare {patents.length} patent{patents.length === 1 ? "" : "s"}
          </h3>
          <button className="btn-ghost text-xs" onClick={onClose}>
            ✕ Close
          </button>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {patents.map((p) => (
            <div
              key={p.patent_id || p.patent_number}
              className="border border-slate-200 rounded-lg p-3 text-sm"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <div className="font-semibold truncate">{p.title || "Patent"}</div>
                  <div className="text-xs text-slate-500">
                    {p.patent_number} · {p.source || "—"}
                  </div>
                </div>
                <button
                  className="text-red-600 text-xs"
                  onClick={() => onRemove(p)}
                  aria-label="Remove"
                >
                  ✕
                </button>
              </div>
              {p.url && (
                <a
                  href={p.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-primary-600 hover:underline mt-2 inline-block"
                >
                  Open ↗
                </a>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------
export default function PatentIntelligenceDashboard() {
  const { patentNumber } = useParams();
  const [compareList, setCompareList] = useState([]);
  const overviewRef = useRef(null);

  const overview = useSection(patentNumber, "overview", () =>
    patentDashboardAPI.overview(patentNumber)
  );
  const aiSummary = useSection(patentNumber, "aiSummary", () =>
    patentDashboardAPI.aiSummary(patentNumber)
  );
  const innovation = useSection(patentNumber, "innovationScores", () =>
    patentDashboardAPI.innovationScores(patentNumber, true)
  );
  const techGap = useSection(patentNumber, "techGap", () =>
    patentDashboardAPI.techGap(patentNumber)
  );
  const apps = useSection(patentNumber, "commercialApplications", () =>
    patentDashboardAPI.commercialApplications(patentNumber)
  );
  const recommendations = useSection(patentNumber, "recommendations", () =>
    patentDashboardAPI.recommendations(patentNumber)
  );
  const funding = useSection(patentNumber, "relatedFunding", () =>
    patentDashboardAPI.relatedFunding(patentNumber)
  );
  const publications = useSection(patentNumber, "relatedPublications", () =>
    patentDashboardAPI.relatedPublications(patentNumber)
  );
  const similar = useSection(patentNumber, "similarPatents", () =>
    patentDashboardAPI.similarPatents(patentNumber)
  );
  const trend = useSection(patentNumber, "techTrend", () =>
    patentDashboardAPI.techTrend(patentNumber)
  );

  function explainAgain() {
    invalidateSection(patentNumber, "aiSummary");
    aiSummary.refresh();
  }

  function refreshAll() {
    invalidatePatent(patentNumber);
    overview.refresh();
    aiSummary.refresh();
    innovation.refresh();
    techGap.refresh();
    apps.refresh();
    recommendations.refresh();
    funding.refresh();
    publications.refresh();
    similar.refresh();
    trend.refresh();
  }

  function scrollToFunding() {
    document
      .getElementById("section-funding")
      ?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function scrollToPapers() {
    document
      .getElementById("section-publications")
      ?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function addToCompare(patent) {
    setCompareList((prev) => {
      if (prev.find((p) => (p.patent_id || p.patent_number) === (patent.patent_id || patent.patent_number))) {
        return prev;
      }
      return [...prev, patent].slice(0, 4);
    });
  }

  function removeFromCompare(patent) {
    setCompareList((prev) =>
      prev.filter(
        (p) => (p.patent_id || p.patent_number) !== (patent.patent_id || patent.patent_number)
      )
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">
            🧠 Patent Intelligence Dashboard
          </h1>
          <p className="text-sm text-slate-500">
            Patent <span className="font-mono">{patentNumber}</span> · AI-assisted analysis
          </p>
        </div>
        <Link to="/patents" className="btn-secondary text-xs">
          ← Back to search
        </Link>
      </div>

      {/* Action bar */}
      {overview.data?.patent && (
        <ActionBar
          patent={overview.data?.patent}
          onExplainAgain={explainAgain}
          onRefresh={refreshAll}
          onFindFunding={scrollToFunding}
          onRelatedPapers={scrollToPapers}
          onCompare={() =>
            overview.data?.patent &&
            addToCompare({
              patent_id: overview.data.patent.id,
              patent_number: overview.data.patent.patent_number,
              title: overview.data.patent.title,
              source: overview.data.patent.source,
              url: overview.data.patent.url,
            })
          }
          compareCount={compareList.length}
        />
      )}

      {/* 1. Overview */}
      <PatentOverview
        data={overview.data}
        loading={overview.loading}
        error={overview.error}
      />

      {/* 2. AI Summary */}
      <AISummaryCard
        data={aiSummary.data}
        loading={aiSummary.loading}
        error={aiSummary.error}
        onExplainAgain={explainAgain}
      />

      {/* 3. Innovation Analysis */}
      <InnovationScores
        data={innovation.data}
        loading={innovation.loading}
        error={innovation.error}
      />

      {/* 4. Tech Gap */}
      <TechGap
        data={techGap.data}
        loading={techGap.loading}
        error={techGap.error}
      />

      {/* 5. Commercial Applications */}
      <CommercialApplications
        data={apps.data}
        loading={apps.loading}
        error={apps.error}
      />

      {/* 6. Related Funding */}
      <div id="section-funding">
        <RelatedFunding
          data={funding.data}
          loading={funding.loading}
          error={funding.error}
        />
      </div>

      {/* 7. Related Publications */}
      <div id="section-publications">
        <RelatedPublications
          data={publications.data}
          loading={publications.loading}
          error={publications.error}
        />
      </div>

      {/* 8. Similar Patents */}
      <SimilarPatents
        data={similar.data}
        loading={similar.loading}
        error={similar.error}
        onCompare={addToCompare}
      />

      {/* 9. Tech Trend */}
      <TechnologyTrend
        data={trend.data}
        loading={trend.loading}
        error={trend.error}
      />

      {/* 10. AI Recommendations */}
      <AIRecommendations
        data={recommendations.data}
        loading={recommendations.loading}
        error={recommendations.error}
      />

      <CompareDrawer
        patents={compareList}
        onClose={() => setCompareList([])}
        onRemove={removeFromCompare}
      />
    </div>
  );
}
