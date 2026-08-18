import React, { useEffect, useMemo, useState } from "react";
import { adminAPI } from "../../services/api.js";
import {
  PageLoader,
  ErrorBanner,
  EmptyState,
  Badge,
  useToasts,
  ToastStack,
  downloadFile,
} from "../../components/admin/ui.jsx";

function PatentDetailModal({ patent, onClose }) {
  if (!patent) return null;
  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 p-4" onClick={onClose}>
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800">Patent Details</h2>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-800">✕</button>
        </div>
        <div className="px-6 py-5 space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone="primary">{patent.source}</Badge>
            <Badge tone="purple">{patent.technology}</Badge>
            <Badge tone="success">📚 {patent.citations} citations</Badge>
            <Badge>Year {patent.year}</Badge>
          </div>
          <h3 className="text-xl font-semibold text-slate-800">{patent.title}</h3>
          <div className="text-sm text-slate-500">ID: {patent.id}</div>
          <p className="text-sm text-slate-700 whitespace-pre-wrap">{patent.abstract}</p>
        </div>
        <div className="px-6 py-4 border-t border-slate-200 flex justify-end">
          <button onClick={onClose} className="btn-secondary">Close</button>
        </div>
      </div>
    </div>
  );
}

export default function PatentMonitor() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [source, setSource] = useState("all");
  const [viewing, setViewing] = useState(null);

  const { toasts, pushToast, dismissToast } = useToasts();

  useEffect(() => {
    load();
  }, []);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const res = await adminAPI.patentOverview();
      setData(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load patent overview");
    } finally {
      setLoading(false);
    }
  }

  async function handleExport() {
    try {
      const res = await adminAPI.exportPatents();
      await downloadFile(res, "patents_report.csv");
      pushToast("Patents report exported", "success");
    } catch (err) {
      pushToast("Failed to export", "error");
    }
  }

  const filteredItems = useMemo(() => {
    if (!data) return [];
    let items = data.items || [];
    if (source && source !== "all") {
      const normalized = source.toLowerCase().replace("_", " ");
      items = items.filter((p) => p.source.toLowerCase() === normalized);
    }
    if (search.trim()) {
      const q = search.toLowerCase();
      items = items.filter(
        (p) =>
          p.title.toLowerCase().includes(q) ||
          p.abstract.toLowerCase().includes(q) ||
          p.technology.toLowerCase().includes(q)
      );
    }
    return items;
  }, [data, search, source]);

  if (loading) return <PageLoader label="Loading patent overview..." />;
  if (error) return <ErrorBanner message={error} onRetry={load} />;
  if (!data) return null;

  return (
    <div className="space-y-4">
      <ToastStack toasts={toasts} onDismiss={dismissToast} />

      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Patent Monitoring</h1>
          <p className="text-slate-500 text-sm">
            Read-only overview of platform-wide patent data
          </p>
        </div>
        <button onClick={handleExport} className="btn-secondary text-sm">⬇ Export CSV</button>
      </div>

      <div className="card bg-blue-50 border-blue-200 text-blue-800 text-sm">
        ℹ Admin can only <strong>monitor</strong> patents. Patents are sourced from integrated patent registries and cannot be added, edited, or deleted by admin.
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="card text-center py-4">
          <div className="text-2xl font-bold text-slate-800">{data.total_patents}</div>
          <div className="text-xs text-slate-500">Total Patents</div>
        </div>
        <div className="card text-center py-4">
          <div className="text-2xl font-bold text-green-700">{data.total_citations}</div>
          <div className="text-xs text-slate-500">Citations</div>
        </div>
        <div className="card text-center py-4">
          <div className="text-2xl font-bold text-purple-700">{data.by_technology?.length || 0}</div>
          <div className="text-xs text-slate-500">Technology Areas</div>
        </div>
        <div className="card text-center py-4">
          <div className="text-2xl font-bold text-blue-700">{data.by_source?.length || 0}</div>
          <div className="text-xs text-slate-500">Sources</div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-3">By Source</h3>
          <div className="space-y-2">
            {data.by_source?.map((b) => (
              <div key={b.source} className="flex items-center justify-between text-sm">
                <span className="text-slate-700">{b.source}</span>
                <Badge tone="primary">{b.count}</Badge>
              </div>
            ))}
          </div>
        </div>
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-3">By Technology</h3>
          <div className="space-y-2">
            {data.by_technology?.map((b) => (
              <div key={b.technology} className="flex items-center justify-between text-sm">
                <span className="text-slate-700">{b.technology}</span>
                <Badge tone="purple">{b.count}</Badge>
              </div>
            ))}
          </div>
        </div>
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-3">By Year</h3>
          <div className="space-y-2">
            {data.by_year?.map((b) => (
              <div key={b.year} className="flex items-center justify-between text-sm">
                <span className="text-slate-700">{b.year}</span>
                <Badge tone="success">{b.count}</Badge>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="card flex flex-wrap gap-3">
        <input
          className="input flex-1 min-w-[200px]"
          placeholder="Search title, abstract, technology..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="input min-w-[160px]"
          value={source}
          onChange={(e) => setSource(e.target.value)}
        >
          <option value="all">All sources</option>
          {data.by_source?.map((b) => (
            <option key={b.source} value={b.source.toLowerCase().replace(" ", "_")}>
              {b.source}
            </option>
          ))}
        </select>
      </div>

      {filteredItems.length === 0 ? (
        <EmptyState title="No patents match" description="Try adjusting filters." />
      ) : (
        <div className="card overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600 uppercase text-xs">
              <tr>
                <th className="text-left px-4 py-3">ID</th>
                <th className="text-left px-4 py-3">Title</th>
                <th className="text-left px-4 py-3">Source</th>
                <th className="text-left px-4 py-3">Year</th>
                <th className="text-left px-4 py-3">Technology</th>
                <th className="text-left px-4 py-3">Citations</th>
                <th className="text-right px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredItems.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 text-slate-500 text-xs font-mono">{p.id}</td>
                  <td className="px-4 py-3 font-medium text-slate-800 max-w-[320px] truncate">{p.title}</td>
                  <td className="px-4 py-3"><Badge tone="primary">{p.source}</Badge></td>
                  <td className="px-4 py-3 text-slate-600">{p.year}</td>
                  <td className="px-4 py-3"><Badge tone="purple">{p.technology}</Badge></td>
                  <td className="px-4 py-3 text-slate-600">{p.citations}</td>
                  <td className="px-4 py-3 text-right">
                    <button className="btn-ghost text-xs" onClick={() => setViewing(p)}>View</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {viewing && <PatentDetailModal patent={viewing} onClose={() => setViewing(null)} />}
    </div>
  );
}
