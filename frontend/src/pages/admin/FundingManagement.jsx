import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { adminAPI } from "../../services/api.js";
import {
  PageLoader,
  ErrorBanner,
  EmptyState,
  Badge,
  Pagination,
  useToasts,
  ToastStack,
} from "../../components/admin/ui.jsx";

const PROVIDER_LABELS = {
  nih: "NIH RePORTER",
  grants_gov: "Grants.gov",
  nsf: "NSF Awards",
  cordis: "CORDIS (EU)",
};

function fmtDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? "—" : d.toLocaleDateString();
}

// Edit/Create modal. All funding fields are editable, including is_active.
function FundingFormModal({ item, onClose, onSaved }) {
  const isEdit = !!item;
  const [form, setForm] = useState({
    title: item?.title || "",
    description: item?.description || "",
    keywords: item?.keywords || "",
    research_domain: item?.research_domain || "",
    organization: item?.organization || "",
    country: item?.country || "",
    funding_type: item?.funding_type || "grant",
    amount_min: item?.amount_min ?? "",
    amount_max: item?.amount_max ?? "",
    currency: item?.currency || "USD",
    application_deadline: item?.application_deadline
      ? new Date(item.application_deadline).toISOString().slice(0, 10)
      : "",
    eligibility: item?.eligibility || "",
    url: item?.url || "",
    is_active: item?.is_active ?? true,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  function setField(k, v) {
    setForm((prev) => ({ ...prev, [k]: v }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.title.trim() || !form.description.trim()) {
      setError("Title and description are required.");
      return;
    }
    setSaving(true);
    setError("");
    // Convert empty strings into nulls so the backend accepts them.
    const payload = {
      ...form,
      amount_min: form.amount_min === "" ? null : Number(form.amount_min),
      amount_max: form.amount_max === "" ? null : Number(form.amount_max),
      application_deadline: form.application_deadline
        ? new Date(form.application_deadline).toISOString()
        : null,
    };
    try {
      if (isEdit) {
        await adminAPI.updateFunding(item.id, payload);
      } else {
        await adminAPI.createFunding(payload);
      }
      onSaved();
      onClose();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          `Failed to ${isEdit ? "update" : "create"} funding`
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800">
            {isEdit ? "Edit Funding" : "Create Funding"}
          </h2>
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-slate-800"
          >
            ✕
          </button>
        </div>
        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-3">
          {error && <ErrorBanner message={error} />}
          <div>
            <label className="text-xs text-slate-500">Title *</label>
            <input
              className="input w-full"
              value={form.title}
              onChange={(e) => setField("title", e.target.value)}
              required
            />
          </div>
          <div>
            <label className="text-xs text-slate-500">Description *</label>
            <textarea
              className="input w-full"
              rows={4}
              value={form.description}
              onChange={(e) => setField("description", e.target.value)}
              required
            />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-slate-500">Keywords (comma-separated)</label>
              <input
                className="input w-full"
                value={form.keywords}
                onChange={(e) => setField("keywords", e.target.value)}
              />
            </div>
            <div>
              <label className="text-xs text-slate-500">Research Domain</label>
              <input
                className="input w-full"
                value={form.research_domain}
                onChange={(e) => setField("research_domain", e.target.value)}
              />
            </div>
            <div>
              <label className="text-xs text-slate-500">Organization</label>
              <input
                className="input w-full"
                value={form.organization}
                onChange={(e) => setField("organization", e.target.value)}
              />
            </div>
            <div>
              <label className="text-xs text-slate-500">Country</label>
              <input
                className="input w-full"
                value={form.country}
                onChange={(e) => setField("country", e.target.value)}
              />
            </div>
            <div>
              <label className="text-xs text-slate-500">Funding Type</label>
              <select
                className="input w-full"
                value={form.funding_type}
                onChange={(e) => setField("funding_type", e.target.value)}
              >
                <option value="grant">grant</option>
                <option value="fellowship">fellowship</option>
                <option value="accelerator">accelerator</option>
                <option value="prize">prize</option>
                <option value="scholarship">scholarship</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-500">URL</label>
              <input
                className="input w-full"
                value={form.url}
                onChange={(e) => setField("url", e.target.value)}
              />
            </div>
            <div>
              <label className="text-xs text-slate-500">Amount Min</label>
              <input
                type="number"
                className="input w-full"
                value={form.amount_min}
                onChange={(e) => setField("amount_min", e.target.value)}
              />
            </div>
            <div>
              <label className="text-xs text-slate-500">Amount Max</label>
              <input
                type="number"
                className="input w-full"
                value={form.amount_max}
                onChange={(e) => setField("amount_max", e.target.value)}
              />
            </div>
            <div>
              <label className="text-xs text-slate-500">Currency</label>
              <input
                className="input w-full"
                value={form.currency}
                onChange={(e) => setField("currency", e.target.value)}
              />
            </div>
            <div>
              <label className="text-xs text-slate-500">Application Deadline</label>
              <input
                type="date"
                className="input w-full"
                value={form.application_deadline}
                onChange={(e) => setField("application_deadline", e.target.value)}
              />
            </div>
            <div>
              <label className="text-xs text-slate-500">Status</label>
              <select
                className="input w-full"
                value={String(form.is_active)}
                onChange={(e) => setField("is_active", e.target.value === "true")}
              >
                <option value="true">Active</option>
                <option value="false">Inactive</option>
              </select>
            </div>
          </div>
          <div>
            <label className="text-xs text-slate-500">Eligibility</label>
            <textarea
              className="input w-full"
              rows={2}
              value={form.eligibility}
              onChange={(e) => setField("eligibility", e.target.value)}
            />
          </div>
          <div className="flex justify-end gap-2 pt-3 border-t border-slate-200">
            <button
              type="button"
              className="btn-secondary"
              onClick={onClose}
              disabled={saving}
            >
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? "Saving..." : isEdit ? "Update" : "Create"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function ConfirmDeleteModal({ item, onClose, onConfirm, deleting }) {
  if (!item) return null;
  return (
    <div
      className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-md"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-6 py-4 border-b border-slate-200">
          <h2 className="text-lg font-semibold text-slate-800">Delete Funding</h2>
        </div>
        <div className="px-6 py-5 text-sm text-slate-700 space-y-2">
          <p>
            This will permanently remove the funding opportunity
            <span className="font-semibold"> {item.title}</span> and any cached
            recommendations that referenced it. This action cannot be undone.
          </p>
        </div>
        <div className="px-6 py-4 border-t border-slate-200 flex justify-end gap-2">
          <button className="btn-secondary" onClick={onClose} disabled={deleting}>
            Cancel
          </button>
          <button
            className="btn-primary bg-red-600 hover:bg-red-700"
            onClick={onConfirm}
            disabled={deleting}
          >
            {deleting ? "Deleting..." : "Delete"}
          </button>
        </div>
      </div>
    </div>
  );
}

function FundingDetailModal({ item, onClose }) {
  if (!item) return null;
  return (
    <div
      className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800">Funding Details</h2>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-800">✕</button>
        </div>
        <div className="px-6 py-5 space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            {item.is_active ? <Badge tone="success">Active</Badge> : <Badge tone="danger">Inactive</Badge>}
            {item.funding_type && <Badge tone="primary">{item.funding_type}</Badge>}
            {item.research_domain && <Badge tone="purple">{item.research_domain}</Badge>}
            {(item.sources || []).map((s) => (
              <Badge key={s.source} tone="blue">
                {PROVIDER_LABELS[s.source] || s.source}
              </Badge>
            ))}
          </div>
          <h3 className="text-xl font-semibold text-slate-800">{item.title}</h3>
          <div className="text-sm text-slate-500">
            {item.organization || "—"} · {item.country || "International"}
          </div>
          <p className="text-sm text-slate-700 whitespace-pre-wrap">
            {item.description}
          </p>
          {item.eligibility && (
            <div>
              <div className="text-xs text-slate-500 mb-1">Eligibility</div>
              <div className="text-sm text-slate-700 whitespace-pre-wrap">{item.eligibility}</div>
            </div>
          )}
          {item.amount_min || item.amount_max ? (
            <div className="text-sm text-slate-700">
              <strong>Amount:</strong> {item.currency} {item.amount_min?.toLocaleString() || "—"} -{" "}
              {item.amount_max?.toLocaleString() || "—"}
            </div>
          ) : null}
          {item.application_deadline && (
            <div className="text-sm text-slate-700">
              <strong>Deadline:</strong> {new Date(item.application_deadline).toLocaleString()}
            </div>
          )}
          {item.keywords && (
            <div className="flex flex-wrap gap-1">
              {item.keywords.split(",").map((k, i) => (
                <span key={i} className="text-xs text-slate-500">#{k.trim()}</span>
              ))}
            </div>
          )}
          {(item.sources || []).length > 0 && (
            <div>
              <div className="text-xs text-slate-500 mb-1">Source Providers</div>
              <div className="space-y-1">
                {item.sources.map((s) => (
                  <div key={s.source} className="text-xs text-slate-600">
                    {PROVIDER_LABELS[s.source] || s.source} · {s.source_id}
                    {s.last_synced_at && (
                      <span className="text-slate-400 ml-2">
                        synced {new Date(s.last_synced_at).toLocaleString()}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
          {item.url && (
            <div className="text-sm">
              <a
                href={item.url}
                target="_blank"
                rel="noreferrer noopener"
                className="text-primary-600 hover:underline"
              >
                Open at source ↗
              </a>
            </div>
          )}
        </div>
        <div className="px-6 py-4 border-t border-slate-200 flex justify-end">
          <button className="btn-secondary" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}

export default function FundingManagement() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [search, setSearch] = useState("");
  const [domain, setDomain] = useState("");
  const [country, setCountry] = useState("");
  const [source, setSource] = useState("");
  const [isActive, setIsActive] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [stats, setStats] = useState(null);
  const [viewingItem, setViewingItem] = useState(null);
  const [editingItem, setEditingItem] = useState(null);
  const [creating, setCreating] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const { toasts, pushToast, dismissToast } = useToasts();

  useEffect(() => {
    load();
    loadStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, search, domain, country, source, isActive]);

  async function load() {
    setLoading(true);
    setError("");
    try {
      // Prefer the admin CRUD list — it returns the full row shape
      // (including is_active) and supports the same filters as the
      // funding-intel read view.
      const params = {
        page,
        page_size: pageSize,
        ...(search ? { search } : {}),
        ...(domain ? { domain } : {}),
        ...(country ? { country } : {}),
        ...(source ? { source } : {}),
        // isActive is a tri-state: "" (all) | "true" | "false". Convert to
        // an actual boolean for the backend query param so empty stays empty.
        ...(isActive === "true" ? { is_active: true } : {}),
        ...(isActive === "false" ? { is_active: false } : {}),
      };
      const res = await adminAPI.listFunding(params);
      setItems(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load funding");
    } finally {
      setLoading(false);
    }
  }

  async function loadStats() {
    try {
      const res = await adminAPI.fundingStats();
      setStats(res.data);
    } catch (err) {
      // non-blocking
    }
  }

  function handleSaved(message) {
    pushToast(message || "Funding saved", "success");
    load();
    loadStats();
  }

  async function handleConfirmDelete() {
    if (!confirmDelete) return;
    setDeleting(true);
    try {
      await adminAPI.deleteFunding(confirmDelete.id);
      pushToast("Funding deleted", "success");
      setConfirmDelete(null);
      load();
      loadStats();
    } catch (err) {
      pushToast(
        err.response?.data?.detail || "Failed to delete funding",
        "error"
      );
    } finally {
      setDeleting(false);
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="space-y-4">
      <ToastStack toasts={toasts} onDismiss={dismissToast} />

      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Imported Funding</h1>
          <p className="text-slate-500 text-sm">
            {total} opportunit{total !== 1 ? "ies" : "y"} ingested from the Funding Intelligence Service.
          </p>
        </div>
        <div className="flex gap-2">
          <button className="btn-primary text-sm" onClick={() => setCreating(true)}>
            + Add Funding
          </button>
          <Link to="/admin/funding-intel" className="btn-secondary text-sm">↻ Open Sync Dashboard</Link>
        </div>
      </div>

      <div className="card border-l-4 border-amber-400 bg-amber-50 text-amber-800 text-sm">
        Funding is read-only by default. Records are managed exclusively by the
        Funding Intelligence Service via scheduled and on-demand syncs from
        official providers. Use <span className="font-semibold">Add / Edit / Delete</span>{" "}
        below for manual overrides. Trigger or inspect syncs from the{" "}
        <Link to="/admin/funding-intel" className="font-semibold underline">Sync Dashboard</Link>.
      </div>

      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="card text-center py-4">
            <div className="text-2xl font-bold text-slate-800">{stats.total_funding}</div>
            <div className="text-xs text-slate-500">Total</div>
          </div>
          <div className="card text-center py-4">
            <div className="text-2xl font-bold text-green-700">{stats.active_funding}</div>
            <div className="text-xs text-slate-500">Active</div>
          </div>
          <div className="card text-center py-4">
            <div className="text-2xl font-bold text-red-700">{stats.inactive_funding ?? ""}</div>
            <div className="text-xs text-slate-500">Inactive</div>
          </div>
          <div className="card text-center py-4">
            <div className="text-2xl font-bold text-purple-700">{stats.recent_additions_30d ?? 0}</div>
            <div className="text-xs text-slate-500">Last 30 days</div>
          </div>
        </div>
      )}

      {error && <ErrorBanner message={error} onRetry={load} />}

      <div className="card flex flex-wrap gap-3">
        <input
          className="input flex-1 min-w-[200px]"
          placeholder="Search title, description, keywords..."
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
          className="input min-w-[160px]"
          placeholder="Country"
          value={country}
          onChange={(e) => { setCountry(e.target.value); setPage(1); }}
        />
        <select
          className="input min-w-[160px]"
          value={source}
          onChange={(e) => { setSource(e.target.value); setPage(1); }}
        >
          <option value="">All providers</option>
          <option value="nih">NIH RePORTER</option>
          <option value="grants_gov">Grants.gov</option>
          <option value="nsf">NSF Awards</option>
          <option value="cordis">CORDIS (EU)</option>
        </select>
        <select
          className="input min-w-[140px]"
          value={isActive}
          onChange={(e) => { setIsActive(e.target.value); setPage(1); }}
        >
          <option value="">All statuses</option>
          <option value="true">Active</option>
          <option value="false">Inactive/Expired</option>
        </select>
      </div>

      {loading ? (
        <PageLoader label="Loading funding..." />
      ) : items.length === 0 ? (
        <EmptyState
          title="No funding ingested yet"
          description="Trigger an initial sync from the Funding Intelligence page to populate the catalogue."
          action={
            <Link to="/admin/funding-intel" className="btn-primary text-sm">Open Sync Dashboard</Link>
          }
        />
      ) : (
        <div className="card overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600 uppercase text-xs">
              <tr>
                <th className="text-left px-4 py-3">Title</th>
                <th className="text-left px-4 py-3">Type</th>
                <th className="text-left px-4 py-3">Domain</th>
                <th className="text-left px-4 py-3">Country</th>
                <th className="text-left px-4 py-3">Status</th>
                <th className="text-left px-4 py-3">Deadline</th>
                <th className="text-right px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((f) => (
                <tr key={f.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 max-w-[280px]">
                    <div className="font-medium text-slate-800 truncate">{f.title}</div>
                    <div className="text-xs text-slate-500 truncate">{f.organization || "—"}</div>
                  </td>
                  <td className="px-4 py-3">
                    {f.funding_type ? <Badge tone="primary">{f.funding_type}</Badge> : "—"}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {f.research_domain ? <Badge tone="purple">{f.research_domain}</Badge> : "—"}
                  </td>
                  <td className="px-4 py-3 text-slate-600">{f.country || "International"}</td>
                  <td className="px-4 py-3">
                    {f.is_active ? <Badge tone="success">Active</Badge> : <Badge tone="danger">Inactive</Badge>}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500">{fmtDate(f.application_deadline)}</td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex justify-end gap-1">
                      <button
                        className="btn-ghost text-xs"
                        onClick={() => setViewingItem(f)}
                      >
                        View
                      </button>
                      <button
                        className="btn-ghost text-xs"
                        onClick={() => setEditingItem(f)}
                      >
                        Edit
                      </button>
                      <button
                        className="btn-ghost text-xs text-red-600 hover:text-red-800"
                        onClick={() => setConfirmDelete(f)}
                      >
                        Delete
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

      {viewingItem && (
        <FundingDetailModal item={viewingItem} onClose={() => setViewingItem(null)} />
      )}
      {editingItem && (
        <FundingFormModal
          item={editingItem}
          onClose={() => setEditingItem(null)}
          onSaved={() => handleSaved("Funding updated")}
        />
      )}
      {creating && (
        <FundingFormModal
          item={null}
          onClose={() => setCreating(false)}
          onSaved={() => handleSaved("Funding created")}
        />
      )}
      {confirmDelete && (
        <ConfirmDeleteModal
          item={confirmDelete}
          onClose={() => setConfirmDelete(null)}
          onConfirm={handleConfirmDelete}
          deleting={deleting}
        />
      )}
    </div>
  );
}
