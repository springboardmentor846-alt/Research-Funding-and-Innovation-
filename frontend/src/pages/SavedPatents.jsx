import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { savedPatentsAPI } from "../services/api.js";
import { useSavedPatents } from "../context/SavedPatentsContext.jsx";
import {
  Pagination,
  ConfirmDialog,
  EmptyState,
  PageLoader,
  ToastStack,
  useToasts,
  Badge,
} from "../components/admin/ui.jsx";

const SORT_OPTIONS = [
  { value: "saved_at_desc", label: "Recently saved", sort_by: "saved_at", sort_order: "desc" },
  { value: "saved_at_asc", label: "Oldest first", sort_by: "saved_at", sort_order: "asc" },
  { value: "publication_date_desc", label: "Newest publication", sort_by: "publication_date", sort_order: "desc" },
  { value: "publication_year_desc", label: "Latest year", sort_by: "publication_year", sort_order: "desc" },
  { value: "title_asc", label: "Title A→Z", sort_by: "title", sort_order: "asc" },
  { value: "citation_count_desc", label: "Most cited", sort_by: "citation_count", sort_order: "desc" },
];

function PatentCard({ patent, onRemove, navigate }) {
  return (
    <div className="card hover:shadow-md transition flex flex-col">
      <div className="flex items-start justify-between gap-2">
        <Badge tone="primary">{patent.source || "unknown"}</Badge>
        <button
          className="btn-ghost text-xs text-red-600"
          onClick={onRemove}
          title="Remove from saved"
        >
          Remove
        </button>
      </div>
      <h3 className="font-semibold text-slate-800 mt-2 line-clamp-2">
        {patent.title}
      </h3>
      <div className="text-xs text-slate-500 mt-1 font-mono">
        {patent.patent_number}
      </div>
      <div className="text-sm text-slate-600 mt-2 space-y-1">
        {patent.inventors && (
          <div>
            <span className="text-slate-400">Inventors:</span> {patent.inventors}
          </div>
        )}
        {patent.assignee && (
          <div>
            <span className="text-slate-400">Assignee:</span> {patent.assignee}
          </div>
        )}
        {patent.technology_area && (
          <div>
            <span className="text-slate-400">Tech area:</span>{" "}
            {patent.technology_area}
          </div>
        )}
      </div>
      <div className="flex flex-wrap gap-2 mt-3">
        {patent.publication_year && (
          <Badge tone="purple">{patent.publication_year}</Badge>
        )}
        <Badge tone="success">📚 {patent.citation_count ?? 0} cites</Badge>
        <span className="text-xs text-slate-400 self-center">
          Saved {new Date(patent.saved_at).toLocaleDateString()}
        </span>
      </div>
      <div className="mt-4 flex gap-2">
        <button
          className="btn-primary text-xs"
          onClick={() =>
            navigate(`/patents/dashboard/${encodeURIComponent(patent.patent_number)}`)
          }
        >
          View Patent
        </button>
        {(patent.url || patent.lens_url) && (
          <a
            className="btn-secondary text-xs"
            href={patent.url || patent.lens_url}
            target="_blank"
            rel="noopener noreferrer"
          >
            Open Original
          </a>
        )}
      </div>
    </div>
  );
}

export default function SavedPatents() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(12);
  const [search, setSearch] = useState("");
  const [source, setSource] = useState("");
  const [sortKey, setSortKey] = useState("saved_at_desc");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [confirmRemove, setConfirmRemove] = useState(null);
  const { refresh } = useSavedPatents();
  const { toasts, pushToast, dismissToast } = useToasts();
  const navigate = useNavigate();

  const sort =
    SORT_OPTIONS.find((s) => s.value === sortKey) || SORT_OPTIONS[0];

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await savedPatentsAPI.list({
        page,
        page_size: pageSize,
        search: search || undefined,
        source: source || undefined,
        sort_by: sort.sort_by,
        sort_order: sort.sort_order,
      });
      setItems(res.data.items || []);
      setTotal(res.data.total || 0);
      setSources(res.data.sources || []);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load saved patents");
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, search, source, sort]);

  useEffect(() => {
    load();
  }, [load]);

  // Reset to page 1 whenever filters/sort change.
  useEffect(() => {
    setPage(1);
  }, [search, source, sortKey]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  async function doRemove(row) {
    try {
      await savedPatentsAPI.remove(row.id);
      pushToast("Saved patent removed", "success");
      setConfirmRemove(null);
      refresh();
      // If we just removed the last item on the page, step back so the
      // user does not land on an empty list.
      if (items.length === 1 && page > 1) {
        setPage(page - 1);
      } else {
        load();
      }
    } catch (err) {
      pushToast(err.response?.data?.detail || "Failed to remove", "error");
    }
  }

  return (
    <div className="space-y-4">
      <ToastStack toasts={toasts} onDismiss={dismissToast} />

      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">⭐ Saved Patents</h1>
          <p className="text-slate-500 text-sm">
            {total} patent{total === 1 ? "" : "s"} in your library
          </p>
        </div>
        <Link to="/patents" className="btn-secondary text-sm">
          Browse patents →
        </Link>
      </div>

      <div className="card flex flex-wrap gap-3">
        <input
          className="input flex-1 min-w-[200px]"
          placeholder="Search title, inventor, assignee, technology…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="input min-w-[160px]"
          value={source}
          onChange={(e) => setSource(e.target.value)}
        >
          <option value="">All sources</option>
          {sources.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <select
          className="input min-w-[180px]"
          value={sortKey}
          onChange={(e) => setSortKey(e.target.value)}
        >
          {SORT_OPTIONS.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <div className="card bg-red-50 text-red-700">{error}</div>
      )}

      {loading ? (
        <PageLoader label="Loading saved patents…" />
      ) : items.length === 0 ? (
        <EmptyState
          title="No saved patents yet"
          description="Open a patent and click '☆ Save Patent' to bookmark it for later."
          action={
            <Link to="/patents" className="btn-primary">
              Browse patents
            </Link>
          }
        />
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((p) => (
            <PatentCard
              key={p.id}
              patent={p}
              onRemove={() => setConfirmRemove(p)}
              navigate={navigate}
            />
          ))}
        </div>
      )}

      <Pagination page={page} totalPages={totalPages} onChange={setPage} />

      <ConfirmDialog
        open={!!confirmRemove}
        title="Remove this saved patent?"
        description={
          confirmRemove
            ? `"${confirmRemove.title}" will be removed from your library.`
            : ""
        }
        confirmText="Remove"
        onConfirm={() => confirmRemove && doRemove(confirmRemove)}
        onCancel={() => setConfirmRemove(null)}
      />
    </div>
  );
}