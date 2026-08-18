import React, { useEffect, useState } from "react";
import { publicationsAPI } from "../services/api.js";

const emptyForm = {
  title: "",
  abstract: "",
  authors: "",
  keywords: "",
  doi: "",
  publisher: "",
  venue: "",
  research_domain: "",
  citation_count: 0,
  url: "",
};

export default function Publications() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [domain, setDomain] = useState("");
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");

  const pageSize = 20;

  useEffect(() => {
    load();
  }, [page, search, domain]);

  async function load() {
    setLoading(true);
    try {
      const res = await publicationsAPI.list({ page, page_size: pageSize, search, domain });
      setItems(res.data.items);
      setTotal(res.data.total);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load publications");
    } finally {
      setLoading(false);
    }
  }

  function openCreate() {
    setEditing(null);
    setForm(emptyForm);
    setShowForm(true);
  }

  function openEdit(p) {
    setEditing(p.id);
    setForm({
      title: p.title,
      abstract: p.abstract || "",
      authors: p.authors,
      keywords: p.keywords || "",
      doi: p.doi || "",
      publisher: p.publisher || "",
      venue: p.venue || "",
      research_domain: p.research_domain || "",
      citation_count: p.citation_count || 0,
      url: p.url || "",
    });
    setShowForm(true);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      if (editing) {
        await publicationsAPI.update(editing, form);
      } else {
        await publicationsAPI.create(form);
      }
      setShowForm(false);
      setForm(emptyForm);
      setEditing(null);
      load();
    } catch (err) {
      setError(err.response?.data?.detail || "Save failed");
    }
  }

  async function handleDelete(id) {
    if (!confirm("Delete this publication?")) return;
    await publicationsAPI.delete(id);
    load();
  }

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">My Publications</h1>
          <p className="text-slate-500 text-sm">Manage your research papers ({total} total)</p>
        </div>
        <button onClick={openCreate} className="btn-primary">+ Add Publication</button>
      </div>

      {error && <div className="card bg-red-50 text-red-700">{error}</div>}

      {/* Filters */}
      <div className="card flex flex-wrap gap-3">
        <input
          className="input flex-1 min-w-[200px]"
          placeholder="Search title, abstract, keywords..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
        />
        <input
          className="input min-w-[180px]"
          placeholder="Filter by domain"
          value={domain}
          onChange={(e) => { setDomain(e.target.value); setPage(1); }}
        />
      </div>

      {/* Form modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 z-40 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
            <h2 className="text-xl font-bold mb-4">{editing ? "Edit Publication" : "Add Publication"}</h2>
            <form onSubmit={handleSubmit} className="space-y-3">
              <Field label="Title *" value={form.title} onChange={(v) => setForm({ ...form, title: v })} required />
              <Field label="Authors *" value={form.authors} onChange={(v) => setForm({ ...form, authors: v })} required />
              <FieldTextarea label="Abstract" value={form.abstract} onChange={(v) => setForm({ ...form, abstract: v })} />
              <Field label="Keywords (comma-separated)" value={form.keywords} onChange={(v) => setForm({ ...form, keywords: v })} />
              <div className="grid sm:grid-cols-2 gap-3">
                <Field label="DOI" value={form.doi} onChange={(v) => setForm({ ...form, doi: v })} />
                <Field label="Publisher" value={form.publisher} onChange={(v) => setForm({ ...form, publisher: v })} />
              </div>
              <div className="grid sm:grid-cols-2 gap-3">
                <Field label="Venue" value={form.venue} onChange={(v) => setForm({ ...form, venue: v })} />
                <Field label="Research Domain" value={form.research_domain} onChange={(v) => setForm({ ...form, research_domain: v })} />
              </div>
              <div className="grid sm:grid-cols-2 gap-3">
                <Field label="Citation Count" type="number" value={form.citation_count} onChange={(v) => setForm({ ...form, citation_count: parseInt(v) || 0 })} />
                <Field label="URL" value={form.url} onChange={(v) => setForm({ ...form, url: v })} />
              </div>
              <div className="flex gap-2 pt-3">
                <button type="submit" className="btn-primary">{editing ? "Update" : "Create"}</button>
                <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* List */}
      {loading ? (
        <div className="card text-center text-slate-500">Loading...</div>
      ) : items.length === 0 ? (
        <div className="card text-center text-slate-500">No publications yet. Click "Add Publication" to get started.</div>
      ) : (
        <div className="grid gap-4">
          {items.map((p) => (
            <div key={p.id} className="card hover:shadow-md transition">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-slate-800">{p.title}</h3>
                  <div className="text-sm text-slate-500 mt-1">{p.authors}</div>
                  {p.abstract && <p className="text-sm text-slate-600 mt-2 line-clamp-2">{p.abstract}</p>}
                  <div className="flex flex-wrap gap-2 mt-3">
                    {p.research_domain && <span className="badge-primary">{p.research_domain}</span>}
                    {p.publisher && <span className="badge-purple">{p.publisher}</span>}
                    {p.citation_count > 0 && <span className="badge-success">📚 {p.citation_count} citations</span>}
                    {p.doi && <span className="badge">DOI: {p.doi}</span>}
                  </div>
                  {p.keywords && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {p.keywords.split(",").slice(0, 5).map((k, i) => (
                        <span key={i} className="text-xs text-slate-500">#{k.trim()}</span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="flex flex-col gap-1 flex-shrink-0">
                  <button onClick={() => openEdit(p)} className="btn-ghost text-xs">Edit</button>
                  <button onClick={() => handleDelete(p.id)} className="btn-ghost text-xs text-red-600">Delete</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button disabled={page === 1} onClick={() => setPage(page - 1)} className="btn-secondary">Prev</button>
          <span className="text-sm text-slate-600">Page {page} of {totalPages}</span>
          <button disabled={page === totalPages} onClick={() => setPage(page + 1)} className="btn-secondary">Next</button>
        </div>
      )}
    </div>
  );
}

function Field({ label, value, onChange, type = "text", required }) {
  return (
    <div>
      <label className="label">{label}</label>
      <input type={type} className="input" value={value} onChange={(e) => onChange(e.target.value)} required={required} />
    </div>
  );
}

function FieldTextarea({ label, value, onChange }) {
  return (
    <div>
      <label className="label">{label}</label>
      <textarea className="input min-h-[80px]" value={value} onChange={(e) => onChange(e.target.value)} />
    </div>
  );
}
