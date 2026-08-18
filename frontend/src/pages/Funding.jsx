import React, { useEffect, useMemo, useState } from "react";
import { fundingAPI, adminAPI } from "../services/api.js";
import { useAuth } from "../context/AuthContext.jsx";

const EMPTY_FORM = {
  title: "",
  description: "",
  organization: "",
  research_domain: "",
  funding_type: "grant",
  application_deadline: "",
  amount_min: "",
  amount_max: "",
  currency: "USD",
  country: "",
  url: "",
  eligibility: "",
  keywords: "",
  is_active: true,
};

const FUNDING_TYPES = ["grant", "fellowship", "accelerator"];

function toDateTimeLocal(value) {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "";
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function fromDateTimeLocal(value) {
  if (!value) return null;
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return null;
  return d.toISOString();
}

function buildPayload(form) {
  const payload = {
    title: form.title.trim(),
    description: form.description.trim(),
    organization: form.organization.trim() || null,
    research_domain: form.research_domain.trim() || null,
    funding_type: form.funding_type || null,
    country: form.country.trim() || null,
    url: form.url.trim() || null,
    eligibility: form.eligibility.trim() || null,
    keywords: form.keywords.trim() || null,
    currency: form.currency.trim() || "USD",
    application_deadline: fromDateTimeLocal(form.application_deadline),
    amount_min:
      form.amount_min === "" || form.amount_min === null
        ? null
        : Number(form.amount_min),
    amount_max:
      form.amount_max === "" || form.amount_max === null
        ? null
        : Number(form.amount_max),
    is_active: Boolean(form.is_active),
  };
  return payload;
}

function validate(form) {
  const errors = {};
  if (!form.title.trim()) errors.title = "Title is required";
  else if (form.title.trim().length > 500) errors.title = "Title is too long";

  if (!form.description.trim()) errors.description = "Description is required";

  if (form.url && form.url.trim()) {
    try {
      // Accept any URL the browser can parse; only flag obvious shape issues.
      // eslint-disable-next-line no-new
      new URL(form.url.trim());
    } catch {
      errors.url = "URL must be a valid link (include https://)";
    }
  }

  if (form.amount_min !== "" && Number.isNaN(Number(form.amount_min))) {
    errors.amount_min = "Amount must be a number";
  }
  if (form.amount_max !== "" && Number.isNaN(Number(form.amount_max))) {
    errors.amount_max = "Amount must be a number";
  }
  if (
    form.amount_min !== "" &&
    form.amount_max !== "" &&
    Number(form.amount_min) > Number(form.amount_max)
  ) {
    errors.amount_max = "Max amount must be greater than or equal to min amount";
  }

  return errors;
}

export default function Funding() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";

  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [domain, setDomain] = useState("");
  const [type, setType] = useState("");
  const [loading, setLoading] = useState(false);

  // Modal + form state
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [formErrors, setFormErrors] = useState({});
  const [formSubmitting, setFormSubmitting] = useState(false);

  // Inline feedback banner
  const [banner, setBanner] = useState(null); // {type: 'success'|'error', message: string}

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, search, domain, type]);

  // Auto-dismiss inline banner
  useEffect(() => {
    if (!banner) return undefined;
    const t = setTimeout(() => setBanner(null), 3500);
    return () => clearTimeout(t);
  }, [banner]);

  async function load() {
    setLoading(true);
    try {
      const res = await fundingAPI.list({
        page,
        page_size: 20,
        search,
        domain,
        funding_type: type,
      });
      setItems(res.data.items);
      setTotal(res.data.total);
      if (res.data.total > 0 && page === 1) {
        setBanner((prev) => prev?.type === "success" ? prev : null);
      }
    } catch (err) {
      console.error(err);
      setBanner({
        type: "error",
        message:
          err.response?.data?.detail || "Failed to load funding opportunities.",
      });
    } finally {
      setLoading(false);
    }
  }

  const totalPages = useMemo(
    () => Math.max(1, Math.ceil(total / 20)),
    [total]
  );

  function openCreateModal() {
    setEditingId(null);
    setForm(EMPTY_FORM);
    setFormErrors({});
    setModalOpen(true);
  }

  function openEditModal(item) {
    setEditingId(item.id);
    setForm({
      title: item.title || "",
      description: item.description || "",
      organization: item.organization || "",
      research_domain: item.research_domain || "",
      funding_type: item.funding_type || "grant",
      application_deadline: toDateTimeLocal(item.application_deadline),
      amount_min: item.amount_min ?? "",
      amount_max: item.amount_max ?? "",
      currency: item.currency || "USD",
      country: item.country || "",
      url: item.url || "",
      eligibility: item.eligibility || "",
      keywords: item.keywords || "",
      is_active: item.is_active !== false,
    });
    setFormErrors({});
    setModalOpen(true);
  }

  function closeModal() {
    if (formSubmitting) return;
    setModalOpen(false);
    setFormErrors({});
  }

  function updateField(name, value) {
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function submitForm(e) {
    e.preventDefault();
    const errors = validate(form);
    setFormErrors(errors);
    if (Object.keys(errors).length > 0) return;

    const payload = buildPayload(form);
    setFormSubmitting(true);
    try {
      if (editingId) {
        await adminAPI.updateFunding(editingId, payload);
        setBanner({ type: "success", message: "Funding opportunity updated." });
      } else {
        await adminAPI.createFunding(payload);
        setBanner({ type: "success", message: "Funding opportunity created." });
      }
      setModalOpen(false);
      // Refresh the list from the first page so the new/edited item is visible.
      if (page !== 1) setPage(1);
      else await load();
    } catch (err) {
      const detail = err.response?.data?.detail;
      setBanner({
        type: "error",
        message:
          (typeof detail === "string" && detail) ||
          (editingId ? "Failed to update funding." : "Failed to create funding."),
      });
    } finally {
      setFormSubmitting(false);
    }
  }

  async function handleDelete(item) {
    const ok = window.confirm(
      "Are you sure you want to delete this funding opportunity?"
    );
    if (!ok) return;
    try {
      await adminAPI.deleteFunding(item.id);
      setBanner({ type: "success", message: "Funding opportunity deleted." });
      // If the page becomes empty after deletion, step back one page.
      if (items.length === 1 && page > 1) {
        setPage(page - 1);
      } else {
        await load();
      }
    } catch (err) {
      const detail = err.response?.data?.detail;
      setBanner({
        type: "error",
        message: (typeof detail === "string" && detail) || "Failed to delete funding.",
      });
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Funding Opportunities</h1>
          <p className="text-slate-500 text-sm">
            Browse {total} active funding opportunities
          </p>
        </div>
        {isAdmin && (
          <button onClick={openCreateModal} className="btn-primary">
            + Add Funding Opportunity
          </button>
        )}
      </div>

      {banner && (
        <div
          role="alert"
          className={
            banner.type === "success"
              ? "card bg-green-50 border-green-200 text-green-800"
              : "card bg-red-50 border-red-200 text-red-800"
          }
        >
          {banner.message}
        </div>
      )}

      <div className="card flex flex-wrap gap-3">
        <input
          className="input flex-1 min-w-[200px]"
          placeholder="Search by title, keyword, description..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
        />
        <input
          className="input min-w-[180px]"
          placeholder="Domain"
          value={domain}
          onChange={(e) => {
            setDomain(e.target.value);
            setPage(1);
          }}
        />
        <select
          className="input min-w-[150px]"
          value={type}
          onChange={(e) => {
            setType(e.target.value);
            setPage(1);
          }}
        >
          <option value="">All Types</option>
          {FUNDING_TYPES.map((t) => (
            <option key={t} value={t}>
              {t.charAt(0).toUpperCase() + t.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="card text-center text-slate-500">Loading...</div>
      ) : items.length === 0 ? (
        <div className="card text-center text-slate-500">
          No funding opportunities match your filters.
        </div>
      ) : (
        <div className="grid gap-4">
          {items.map((f) => (
            <div key={f.id} className="card hover:shadow-md transition">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-slate-800 text-lg">{f.title}</h3>
                  <div className="text-sm text-slate-500 mt-1">
                    {f.organization} · {f.country || "International"}
                  </div>
                  <p className="text-sm text-slate-600 mt-2 line-clamp-3">
                    {f.description}
                  </p>
                  <div className="flex flex-wrap gap-2 mt-3">
                    {f.funding_type && (
                      <span className="badge-primary uppercase">
                        {f.funding_type}
                      </span>
                    )}
                    {f.research_domain && (
                      <span className="badge-purple">{f.research_domain}</span>
                    )}
                    {f.amount_min && f.amount_max && (
                      <span className="badge-success">
                        💰 {f.currency} {f.amount_min.toLocaleString()} -{" "}
                        {f.amount_max.toLocaleString()}
                      </span>
                    )}
                    {f.application_deadline && (
                      <span className="badge-warning">
                        ⏰ Deadline:{" "}
                        {new Date(f.application_deadline).toLocaleDateString()}
                      </span>
                    )}
                    {!f.is_active && (
                      <span className="badge bg-slate-200 text-slate-700">Inactive</span>
                    )}
                  </div>
                  {f.keywords && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {f.keywords
                        .split(",")
                        .slice(0, 8)
                        .map((k, i) => (
                          <span key={i} className="text-xs text-slate-500">
                            #{k.trim()}
                          </span>
                        ))}
                    </div>
                  )}
                </div>
                <div className="flex flex-col items-end gap-2 flex-shrink-0">
                  {f.url && (
                    <a
                      href={f.url}
                      target="_blank"
                      rel="noreferrer"
                      className="btn-primary text-sm"
                    >
                      Apply →
                    </a>
                  )}
                  {isAdmin && (
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => openEditModal(f)}
                        className="btn-secondary text-xs"
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDelete(f)}
                        className="btn bg-red-600 text-white hover:bg-red-700 text-xs"
                      >
                        Delete
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            disabled={page === 1}
            onClick={() => setPage(page - 1)}
            className="btn-secondary"
          >
            Prev
          </button>
          <span className="text-sm text-slate-600">
            Page {page} of {totalPages}
          </span>
          <button
            disabled={page === totalPages}
            onClick={() => setPage(page + 1)}
            className="btn-secondary"
          >
            Next
          </button>
        </div>
      )}

      {modalOpen && (
        <div
          className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 p-4"
          onClick={closeModal}
        >
          <div
            className="bg-white rounded-xl shadow-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <form onSubmit={submitForm} noValidate>
              <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-slate-800">
                  {editingId ? "Edit Funding Opportunity" : "Add Funding Opportunity"}
                </h2>
                <button
                  type="button"
                  onClick={closeModal}
                  className="text-slate-500 hover:text-slate-800"
                  aria-label="Close"
                >
                  ✕
                </button>
              </div>

              <div className="px-6 py-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="sm:col-span-2">
                  <label className="label">
                    Title <span className="text-red-500">*</span>
                  </label>
                  <input
                    className="input"
                    value={form.title}
                    onChange={(e) => updateField("title", e.target.value)}
                    maxLength={500}
                  />
                  {formErrors.title && (
                    <p className="text-xs text-red-600 mt-1">{formErrors.title}</p>
                  )}
                </div>

                <div className="sm:col-span-2">
                  <label className="label">
                    Description <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    className="input min-h-[100px]"
                    value={form.description}
                    onChange={(e) => updateField("description", e.target.value)}
                  />
                  {formErrors.description && (
                    <p className="text-xs text-red-600 mt-1">
                      {formErrors.description}
                    </p>
                  )}
                </div>

                <div>
                  <label className="label">Organization</label>
                  <input
                    className="input"
                    value={form.organization}
                    onChange={(e) => updateField("organization", e.target.value)}
                  />
                </div>

                <div>
                  <label className="label">Research Domain</label>
                  <input
                    className="input"
                    value={form.research_domain}
                    onChange={(e) => updateField("research_domain", e.target.value)}
                    placeholder="e.g. AI, Climate, Biotech"
                  />
                </div>

                <div>
                  <label className="label">Funding Type</label>
                  <select
                    className="input"
                    value={form.funding_type}
                    onChange={(e) => updateField("funding_type", e.target.value)}
                  >
                    {FUNDING_TYPES.map((t) => (
                      <option key={t} value={t}>
                        {t.charAt(0).toUpperCase() + t.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="label">Country</label>
                  <input
                    className="input"
                    value={form.country}
                    onChange={(e) => updateField("country", e.target.value)}
                  />
                </div>

                <div>
                  <label className="label">Application Deadline</label>
                  <input
                    type="datetime-local"
                    className="input"
                    value={form.application_deadline}
                    onChange={(e) => updateField("application_deadline", e.target.value)}
                  />
                </div>

                <div>
                  <label className="label">Currency</label>
                  <input
                    className="input"
                    value={form.currency}
                    onChange={(e) => updateField("currency", e.target.value)}
                    maxLength={10}
                  />
                </div>

                <div>
                  <label className="label">Amount (min)</label>
                  <input
                    type="number"
                    className="input"
                    value={form.amount_min}
                    onChange={(e) => updateField("amount_min", e.target.value)}
                    min="0"
                    step="0.01"
                  />
                  {formErrors.amount_min && (
                    <p className="text-xs text-red-600 mt-1">
                      {formErrors.amount_min}
                    </p>
                  )}
                </div>

                <div>
                  <label className="label">Amount (max)</label>
                  <input
                    type="number"
                    className="input"
                    value={form.amount_max}
                    onChange={(e) => updateField("amount_max", e.target.value)}
                    min="0"
                    step="0.01"
                  />
                  {formErrors.amount_max && (
                    <p className="text-xs text-red-600 mt-1">
                      {formErrors.amount_max}
                    </p>
                  )}
                </div>

                <div className="sm:col-span-2">
                  <label className="label">URL</label>
                  <input
                    className="input"
                    value={form.url}
                    onChange={(e) => updateField("url", e.target.value)}
                    placeholder="https://..."
                  />
                  {formErrors.url && (
                    <p className="text-xs text-red-600 mt-1">{formErrors.url}</p>
                  )}
                </div>

                <div className="sm:col-span-2">
                  <label className="label">Eligibility</label>
                  <textarea
                    className="input min-h-[80px]"
                    value={form.eligibility}
                    onChange={(e) => updateField("eligibility", e.target.value)}
                  />
                </div>

                <div className="sm:col-span-2">
                  <label className="label">Keywords</label>
                  <input
                    className="input"
                    value={form.keywords}
                    onChange={(e) => updateField("keywords", e.target.value)}
                    placeholder="comma, separated, list"
                  />
                </div>

                <div className="sm:col-span-2 flex items-center gap-2">
                  <input
                    id="is_active"
                    type="checkbox"
                    className="h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                    checked={Boolean(form.is_active)}
                    onChange={(e) => updateField("is_active", e.target.checked)}
                  />
                  <label htmlFor="is_active" className="text-sm text-slate-700">
                    Active (visible to researchers)
                  </label>
                </div>
              </div>

              <div className="px-6 py-4 border-t border-slate-200 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={closeModal}
                  className="btn-secondary"
                  disabled={formSubmitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={formSubmitting}
                >
                  {formSubmitting
                    ? editingId
                      ? "Saving..."
                      : "Creating..."
                    : editingId
                    ? "Save Changes"
                    : "Create"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
