import React, { useEffect, useState } from "react";
import { adminAPI } from "../../services/api.js";
import {
  PageLoader,
  ErrorBanner,
  EmptyState,
  Badge,
  ConfirmDialog,
  Pagination,
  useToasts,
  ToastStack,
  downloadFile,
} from "../../components/admin/ui.jsx";

function PublicationDetailModal({ pub, onClose }) {
  if (!pub) return null;
  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 p-4" onClick={onClose}>
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800">Publication Details</h2>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-800">✕</button>
        </div>
        <div className="px-6 py-5 space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            {pub.research_domain && <Badge tone="primary">{pub.research_domain}</Badge>}
            {pub.publisher && <Badge tone="purple">{pub.publisher}</Badge>}
            {pub.citation_count > 0 && <Badge tone="success">📚 {pub.citation_count} citations</Badge>}
            {pub.doi && <Badge>DOI: {pub.doi}</Badge>}
          </div>
          <h3 className="text-xl font-semibold text-slate-800">{pub.title}</h3>
          <div className="text-sm text-slate-600">By {pub.authors}</div>
          {pub.venue && <div className="text-sm text-slate-500">Venue: {pub.venue}</div>}
          {pub.publication_date && (
            <div className="text-sm text-slate-500">
              Published: {new Date(pub.publication_date).toLocaleDateString()}
            </div>
          )}
          {pub.abstract && (
            <div>
              <div className="text-xs text-slate-500 mb-1">Abstract</div>
              <div className="text-sm text-slate-700 whitespace-pre-wrap">{pub.abstract}</div>
            </div>
          )}
          {pub.keywords && (
            <div className="flex flex-wrap gap-1">
              {pub.keywords.split(",").map((k, i) => (
                <span key={i} className="text-xs text-slate-500">#{k.trim()}</span>
              ))}
            </div>
          )}
          {pub.url && (
            <a href={pub.url} target="_blank" rel="noreferrer" className="text-sm text-primary-600 hover:underline">
              View original
            </a>
          )}
        </div>
        <div className="px-6 py-4 border-t border-slate-200 flex justify-end">
          <button onClick={onClose} className="btn-secondary">Close</button>
        </div>
      </div>
    </div>
  );
}

export default function PublicationMonitor() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [search, setSearch] = useState("");
  const [domain, setDomain] = useState("");
  const [ownerId, setOwnerId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [stats, setStats] = useState(null);

  const [viewing, setViewing] = useState(null);
  const [confirm, setConfirm] = useState(null);
  const [busy, setBusy] = useState(false);

  const { toasts, pushToast, dismissToast } = useToasts();

  useEffect(() => {
    load();
    loadStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, search, domain, ownerId]);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const params = {
        page,
        page_size: pageSize,
        ...(search ? { search } : {}),
        ...(domain ? { domain } : {}),
        ...(ownerId ? { owner_id: Number(ownerId) } : {}),
      };
      const res = await adminAPI.listPublications(params);
      setItems(res.data.items);
      setTotal(res.data.total);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load publications");
    } finally {
      setLoading(false);
    }
  }

  async function loadStats() {
    try {
      const res = await adminAPI.publicationStats();
      setStats(res.data);
    } catch (err) {
      // non-blocking
    }
  }

  async function handleDelete() {
    if (!confirm) return;
    setBusy(true);
    try {
      await adminAPI.deletePublication(confirm.id);
      pushToast("Publication removed", "success");
      setConfirm(null);
      if (items.length === 1 && page > 1) setPage(page - 1);
      else load();
    } catch (err) {
      pushToast(err.response?.data?.detail || "Failed to remove", "error");
    } finally {
      setBusy(false);
    }
  }

  async function handleExport() {
    try {
      const res = await adminAPI.exportPublications();
      await downloadFile(res, "publications_report.csv");
      pushToast("Publications report exported", "success");
    } catch (err) {
      pushToast("Failed to export", "error");
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="space-y-4">
      <ToastStack toasts={toasts} onDismiss={dismissToast} />

      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Publication Monitoring</h1>
          <p className="text-slate-500 text-sm">
            {total} publication{total !== 1 ? "s" : ""} across all researchers
          </p>
        </div>
        <button onClick={handleExport} className="btn-secondary text-sm">⬇ Export CSV</button>
      </div>

      <div className="card bg-amber-50 border-amber-200 text-amber-800 text-sm">
        ⚠ Admin can only <strong>remove</strong> duplicate, spam, or invalid records. Admin cannot add, edit, or delete legitimate publications on behalf of researchers.
      </div>

      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="card text-center py-4">
            <div className="text-2xl font-bold text-slate-800">{stats.total_publications}</div>
            <div className="text-xs text-slate-500">Total</div>
          </div>
          <div className="card text-center py-4">
            <div className="text-2xl font-bold text-green-700">{stats.total_citations}</div>
            <div className="text-xs text-slate-500">Citations</div>
          </div>
          <div className="card text-center py-4">
            <div className="text-2xl font-bold text-blue-700">{stats.recent_additions_30d}</div>
            <div className="text-xs text-slate-500">Added (30d)</div>
          </div>
          <div className="card text-center py-4">
            <div className="text-2xl font-bold text-purple-700">{stats.by_domain?.length || 0}</div>
            <div className="text-xs text-slate-500">Domains</div>
          </div>
        </div>
      )}

      {error && <ErrorBanner message={error} onRetry={load} />}

      <div className="card flex flex-wrap gap-3">
        <input
          className="input flex-1 min-w-[200px]"
          placeholder="Search title, abstract, authors, DOI..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
        />
        <input
          className="input min-w-[160px]"
          placeholder="Domain"
          value={domain}
          onChange={(e) => { setDomain(e.target.value); setPage(1); }}
        />
        <input
          className="input min-w-[140px]"
          placeholder="Owner ID"
          value={ownerId}
          onChange={(e) => { setOwnerId(e.target.value.replace(/[^\d]/g, "")); setPage(1); }}
        />
      </div>

      {loading ? (
        <PageLoader label="Loading publications..." />
      ) : items.length === 0 ? (
        <EmptyState title="No publications found" description="Try adjusting filters." />
      ) : (
        <div className="card overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600 uppercase text-xs">
              <tr>
                <th className="text-left px-4 py-3">Title</th>
                <th className="text-left px-4 py-3">Authors</th>
                <th className="text-left px-4 py-3">Domain</th>
                <th className="text-left px-4 py-3">Owner</th>
                <th className="text-left px-4 py-3">Citations</th>
                <th className="text-left px-4 py-3">Added</th>
                <th className="text-right px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 max-w-[320px]">
                    <div className="font-medium text-slate-800 truncate">{p.title}</div>
                    {p.doi && <div className="text-xs text-slate-500">DOI: {p.doi}</div>}
                  </td>
                  <td className="px-4 py-3 text-slate-600 max-w-[220px] truncate">{p.authors}</td>
                  <td className="px-4 py-3">
                    {p.research_domain ? <Badge tone="purple">{p.research_domain}</Badge> : "—"}
                  </td>
                  <td className="px-4 py-3 text-slate-500 text-xs">#{p.owner_id}</td>
                  <td className="px-4 py-3 text-slate-600">{p.citation_count ?? 0}</td>
                  <td className="px-4 py-3 text-xs text-slate-500">
                    {p.created_at ? new Date(p.created_at).toLocaleDateString() : "—"}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex justify-end gap-1">
                      <button className="btn-ghost text-xs" onClick={() => setViewing(p)}>View</button>
                      <button
                        className="btn-ghost text-xs text-red-600"
                        disabled={busy}
                        onClick={() => setConfirm(p)}
                      >
                        Remove
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Pagination page={page} totalPages={totalPages} onChange={setPage} />

      {viewing && <PublicationDetailModal pub={viewing} onClose={() => setViewing(null)} />}

      <ConfirmDialog
        open={!!confirm}
        title="Remove publication"
        description={
          confirm
            ? `Remove "${confirm.title}" from the platform? Use this for duplicates, spam, or invalid records.`
            : ""
        }
        confirmText="Remove"
        busy={busy}
        onConfirm={handleDelete}
        onCancel={() => !busy && setConfirm(null)}
      />
    </div>
  );
}
