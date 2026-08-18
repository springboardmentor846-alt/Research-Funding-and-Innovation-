import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { authAPI, profileAPI, savedPatentsAPI } from "../services/api.js";
import { useAuth } from "../context/AuthContext.jsx";
import { useSavedPatents } from "../context/SavedPatentsContext.jsx";
import ResearchInterestsCard from "../components/ResearchInterestsCard.jsx";
import AlertPreferencesCard from "../components/AlertPreferencesCard.jsx";

export default function Profile() {
  const { user, refreshUser } = useAuth();
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({});
  const [stats, setStats] = useState(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  // password change
  const [pwForm, setPwForm] = useState({ old: "", new: "" });

  // collaborations
  const [collabs, setCollabs] = useState([]);
  const [showCollabForm, setShowCollabForm] = useState(false);
  const [editingCollab, setEditingCollab] = useState(null);
  const [collabForm, setCollabForm] = useState(emptyCollab);

  // funding history
  const [fundingHist, setFundingHist] = useState([]);
  const [fundingStats, setFundingStats] = useState({ total_amount: 0, total: 0 });
  const [showFundingForm, setShowFundingForm] = useState(false);
  const [editingFunding, setEditingFunding] = useState(null);
  const [fundingForm, setFundingForm] = useState(emptyFunding);

  // research interests
  const [interests, setInterests] = useState([]);
  const [predefinedDomains, setPredefinedDomains] = useState([]);

  // saved patents (most-recent 5 for the profile section)
  const { refresh: refreshSavedCount } = useSavedPatents();
  const [savedPatents, setSavedPatents] = useState([]);

  async function loadSavedPatents() {
    try {
      const res = await savedPatentsAPI.list({
        page: 1,
        page_size: 5,
        sort_by: "saved_at",
        sort_order: "desc",
      });
      setSavedPatents(res.data?.items || []);
    } catch {
      setSavedPatents([]);
    }
  }

  useEffect(() => {
    if (user) loadSavedPatents();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id]);

  useEffect(() => {
    if (user) {
      setForm({
        full_name: user.full_name || "",
        affiliation: user.affiliation || "",
        // research_interests text field is now managed by the structured card.
        // Keep it in form state for callers that still POST a CSV — but the
        // Profile UI no longer exposes it as an input.
        research_interests: user.research_interests || "",
        skills: user.skills || "",
        bio: user.bio || "",
        orcid: user.orcid || "",
        avatar_url: user.avatar_url || "",
      });
      // Hydrate the structured interest list (returned by /auth/me as
      // `interests` alongside the legacy CSV at `research_interests`).
      setInterests(Array.isArray(user.interests) ? user.interests : []);
    }
    loadAll();
  }, [user]);

  async function loadAll() {
    try {
      const [s, c, f, i, d] = await Promise.all([
        authAPI.myStats(),
        profileAPI.listCollaborations(),
        profileAPI.listFundingHistory(),
        profileAPI.listResearchInterests(),
        profileAPI.listResearchDomains(),
      ]);
      setStats(s.data);
      setCollabs(c.data.items);
      setFundingHist(f.data.items);
      setFundingStats({ total_amount: f.data.total_amount, total: f.data.total });
      setInterests(i.data.items || []);
      setPredefinedDomains(d.data.domains || []);
    } catch (err) {
      console.error("Failed to load profile data:", err);
    }
  }

  async function save() {
    setSaving(true);
    setMessage("");
    try {
      await authAPI.updateMe(form);
      await refreshUser();
      setMessage("Profile updated successfully");
      setEditing(false);
    } catch (err) {
      setMessage(err.response?.data?.detail || "Update failed");
    } finally {
      setSaving(false);
    }
  }

  async function changePassword() {
    if (pwForm.new.length < 8) {
      setMessage("Password must be at least 8 characters");
      return;
    }
    try {
      await authAPI.changePassword(pwForm.old, pwForm.new);
      setMessage("Password changed successfully");
      setPwForm({ old: "", new: "" });
    } catch (err) {
      setMessage(err.response?.data?.detail || "Failed to change password");
    }
  }

  // ---- Collaboration handlers ----
  function openCollabCreate() {
    setEditingCollab(null);
    setCollabForm(emptyCollab);
    setShowCollabForm(true);
  }
  function openCollabEdit(c) {
    setEditingCollab(c.id);
    setCollabForm({
      collaborator_name: c.collaborator_name || "",
      collaborator_email: c.collaborator_email || "",
      collaborator_affiliation: c.collaborator_affiliation || "",
      project_title: c.project_title || "",
      description: c.description || "",
      status: c.status || "active",
      start_date: c.start_date ? c.start_date.slice(0, 10) : "",
      end_date: c.end_date ? c.end_date.slice(0, 10) : "",
    });
    setShowCollabForm(true);
  }
  async function saveCollab() {
    try {
      const payload = {
        ...collabForm,
        start_date: collabForm.start_date || null,
        end_date: collabForm.end_date || null,
      };
      if (editingCollab) {
        await profileAPI.updateCollaboration(editingCollab, payload);
      } else {
        await profileAPI.createCollaboration(payload);
      }
      setShowCollabForm(false);
      loadAll();
    } catch (err) {
      setMessage(err.response?.data?.detail || "Failed to save collaboration");
    }
  }
  async function deleteCollab(id) {
    if (!confirm("Delete this collaboration?")) return;
    await profileAPI.deleteCollaboration(id);
    loadAll();
  }

  // ---- Funding history handlers ----
  function openFundingCreate() {
    setEditingFunding(null);
    setFundingForm(emptyFunding);
    setShowFundingForm(true);
  }
  function openFundingEdit(h) {
    setEditingFunding(h.id);
    setFundingForm({
      title: h.title || "",
      organization: h.organization || "",
      amount: h.amount || 0,
      currency: h.currency || "USD",
      status: h.status || "awarded",
      awarded_date: h.awarded_date ? h.awarded_date.slice(0, 10) : "",
      end_date: h.end_date ? h.end_date.slice(0, 10) : "",
      description: h.description || "",
    });
    setShowFundingForm(true);
  }
  async function saveFunding() {
    try {
      const payload = {
        ...fundingForm,
        amount: parseFloat(fundingForm.amount) || 0,
        awarded_date: fundingForm.awarded_date || null,
        end_date: fundingForm.end_date || null,
      };
      if (editingFunding) {
        await profileAPI.updateFundingHistory(editingFunding, payload);
      } else {
        await profileAPI.createFundingHistory(payload);
      }
      setShowFundingForm(false);
      loadAll();
    } catch (err) {
      setMessage(err.response?.data?.detail || "Failed to save funding record");
    }
  }
  async function deleteFunding(id) {
    if (!confirm("Delete this funding record?")) return;
    await profileAPI.deleteFundingHistory(id);
    loadAll();
  }

  if (!user) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h1 className="text-2xl font-bold text-slate-800">👤 My Profile</h1>
        {!editing ? (
          <button onClick={() => setEditing(true)} className="btn-primary">Edit Profile</button>
        ) : (
          <div className="flex gap-2">
            <button onClick={save} disabled={saving} className="btn-primary">{saving ? "Saving..." : "Save"}</button>
            <button onClick={() => setEditing(false)} className="btn-secondary">Cancel</button>
          </div>
        )}
      </div>

      {message && <div className="card bg-primary-50 text-primary-800">{message}</div>}

      {/* Identity card */}
      <div className="card">
        <div className="flex items-start gap-4">
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white text-2xl font-bold flex-shrink-0">
            {(user.full_name || user.username).charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            {editing ? (
              <div className="space-y-2">
                <Field label="Full Name" value={form.full_name} onChange={(v) => setForm({ ...form, full_name: v })} />
                <Field label="Affiliation" value={form.affiliation} onChange={(v) => setForm({ ...form, affiliation: v })} />
                <Field label="ORCID" value={form.orcid} onChange={(v) => setForm({ ...form, orcid: v })} />
                <Field label="Avatar URL" value={form.avatar_url} onChange={(v) => setForm({ ...form, avatar_url: v })} />
              </div>
            ) : (
              <>
                <h2 className="text-xl font-bold text-slate-800">{user.full_name || user.username}</h2>
                <div className="text-sm text-slate-500">{user.email} · @{user.username}</div>
                <div className="flex flex-wrap gap-2 mt-2">
                  <span className="badge-primary capitalize">{user.role.replace("_", " ")}</span>
                  {user.affiliation && <span className="badge-purple">{user.affiliation}</span>}
                  {user.is_verified && <span className="badge-success">✓ Verified</span>}
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <StatBox label="Publications" value={stats.total_publications} />
          <StatBox label="Citations" value={stats.total_citations} />
          <StatBox label="H-Index" value={stats.h_index} />
          <StatBox label="i10-Index" value={stats.i10_index} />
          <StatBox label="Recommendations" value={stats.recommendations_count} />
          <StatBox label="Funding Awarded" value={stats.funding_awarded} />
        </div>
      )}

      {/* Bio / Interests / Skills */}
      <div className="card">
        <h3 className="font-semibold text-slate-800 mb-3">Research Profile</h3>
        {editing ? (
          <div className="space-y-3">
            <FieldArea label="Bio" value={form.bio} onChange={(v) => setForm({ ...form, bio: v })} />
            {/* Research interests are managed by the structured card below. */}
            <Field label="Skills (comma-separated)" value={form.skills} onChange={(v) => setForm({ ...form, skills: v })} />
          </div>
        ) : (
          <div className="space-y-3">
            <div>
              <div className="text-sm text-slate-500">Bio</div>
              <div className="text-slate-700">{user.bio || <em className="text-slate-400">No bio yet</em>}</div>
            </div>
            {interests.length > 0 && (
              <div>
                <div className="text-sm text-slate-500">Research Interests</div>
                <div className="flex flex-wrap gap-1 mt-1">
                  {interests.map((i) => (
                    <span key={i.id} className={i.is_custom ? "badge-purple" : "badge-primary"}>
                      {i.name}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {user.skills && (
              <div>
                <div className="text-sm text-slate-500">Skills</div>
                <div className="flex flex-wrap gap-1 mt-1">
                  {user.skills.split(",").map((s, idx) => (
                    <span key={idx} className="badge-purple">{s.trim()}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Research Interests — structured tag editor */}
      <ResearchInterestsCard
        interests={interests}
        predefinedDomains={predefinedDomains}
        onChange={async () => {
          await refreshUser();
          loadAll();
        }}
      />

      {/* Collaborations */}
      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-slate-800">🤝 Collaborations ({collabs.length})</h3>
          <button onClick={openCollabCreate} className="btn-primary text-sm">+ Add Collaboration</button>
        </div>
        {collabs.length === 0 ? (
          <p className="text-sm text-slate-500">No collaborations yet. Add research collaborators to track your network.</p>
        ) : (
          <div className="space-y-3">
            {collabs.map((c) => (
              <div key={c.id} className="p-3 border border-slate-200 rounded-lg flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-slate-800">{c.collaborator_name}</div>
                  {c.collaborator_affiliation && <div className="text-sm text-slate-500">{c.collaborator_affiliation}</div>}
                  {c.project_title && <div className="text-sm text-slate-700 mt-1">{c.project_title}</div>}
                  <div className="flex flex-wrap gap-2 mt-2">
                    <span className={`badge ${
                      c.status === "active" ? "bg-green-100 text-green-800" :
                      c.status === "completed" ? "bg-slate-100 text-slate-700" :
                      "bg-amber-100 text-amber-800"
                    }`}>{c.status}</span>
                    {c.collaborator_email && <span className="text-xs text-slate-500">{c.collaborator_email}</span>}
                  </div>
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  <button onClick={() => openCollabEdit(c)} className="btn-ghost text-xs">Edit</button>
                  <button onClick={() => deleteCollab(c.id)} className="btn-ghost text-xs text-red-600">Delete</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Funding History */}
      <div className="card">
        <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
          <div>
            <h3 className="font-semibold text-slate-800">💰 Funding History ({fundingStats.total})</h3>
            {fundingStats.total > 0 && (
              <div className="text-sm text-slate-500">
                Total awarded: <span className="font-semibold text-green-700">${fundingStats.total_amount.toLocaleString()}</span>
              </div>
            )}
          </div>
          <button onClick={openFundingCreate} className="btn-primary text-sm">+ Add Funding Record</button>
        </div>
        {fundingHist.length === 0 ? (
          <p className="text-sm text-slate-500">No funding records yet. Track your awarded grants and fellowships here.</p>
        ) : (
          <div className="space-y-3">
            {fundingHist.map((h) => (
              <div key={h.id} className="p-3 border border-slate-200 rounded-lg flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-slate-800">{h.title}</div>
                  {h.organization && <div className="text-sm text-slate-500">{h.organization}</div>}
                  <div className="flex flex-wrap gap-2 mt-2">
                    {h.amount != null && (
                      <span className="badge-success">
                        {h.currency} {h.amount.toLocaleString()}
                      </span>
                    )}
                    <span className={`badge ${
                      h.status === "awarded" ? "bg-green-100 text-green-800" :
                      h.status === "completed" ? "bg-blue-100 text-blue-800" :
                      h.status === "pending" ? "bg-amber-100 text-amber-800" :
                      "bg-red-100 text-red-800"
                    }`}>{h.status}</span>
                    {h.awarded_date && <span className="text-xs text-slate-500">Awarded: {new Date(h.awarded_date).toLocaleDateString()}</span>}
                  </div>
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  <button onClick={() => openFundingEdit(h)} className="btn-ghost text-xs">Edit</button>
                  <button onClick={() => deleteFunding(h.id)} className="btn-ghost text-xs text-red-600">Delete</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Saved Patents */}
      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-slate-800">⭐ Saved Patents</h3>
          <Link
            to="/saved-patents"
            className="text-sm text-primary-600 hover:underline"
          >
            View all →
          </Link>
        </div>
        {savedPatents.length === 0 ? (
          <p className="text-sm text-slate-500">
            No saved patents yet. Bookmark patents from the Patent
            Intelligence Dashboard to track them here.
          </p>
        ) : (
          <div className="space-y-2">
            {savedPatents.map((p) => (
              <div
                key={p.id}
                className="p-3 border border-slate-200 rounded-lg flex items-start justify-between gap-3"
              >
                <div className="min-w-0">
                  <div className="font-medium text-slate-800 line-clamp-1">
                    {p.title}
                  </div>
                  <div className="text-xs text-slate-500 font-mono">
                    {p.patent_number} · {p.source}
                  </div>
                  {p.technology_area && (
                    <div className="text-xs text-slate-500">
                      {p.technology_area}
                    </div>
                  )}
                </div>
                <div className="flex gap-1 flex-shrink-0">
                  <Link
                    to={`/patents/dashboard/${encodeURIComponent(
                      p.patent_number
                    )}`}
                    className="btn-ghost text-xs"
                  >
                    View
                  </Link>
                  <button
                    className="btn-ghost text-xs text-red-600"
                    onClick={async () => {
                      if (
                        !window.confirm(
                          `Remove "${p.title}" from your saved patents?`
                        )
                      ) {
                        return;
                      }
                      try {
                        await savedPatentsAPI.remove(p.id);
                        setMessage("Saved patent removed");
                        setSavedPatents((items) =>
                          items.filter((x) => x.id !== p.id)
                        );
                        refreshSavedCount();
                      } catch (err) {
                        setMessage(
                          err.response?.data?.detail ||
                            "Failed to remove saved patent"
                        );
                      }
                    }}
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Change password */}
      <div className="card">
        <h3 className="font-semibold text-slate-800 mb-3">Change Password</h3>
        <div className="grid sm:grid-cols-3 gap-3 items-end">
          <div>
            <label className="label">Current Password</label>
            <input
              type="password"
              className="input"
              value={pwForm.old}
              onChange={(e) => setPwForm({ ...pwForm, old: e.target.value })}
            />
          </div>
          <div>
            <label className="label">New Password</label>
            <input
              type="password"
              className="input"
              value={pwForm.new}
              onChange={(e) => setPwForm({ ...pwForm, new: e.target.value })}
            />
          </div>
          <button onClick={changePassword} className="btn-primary">Update Password</button>
        </div>
      </div>

      {/* Alert preferences — wired to /api/v1/alert-preferences. */}
      <AlertPreferencesCard />

      {/* Collaboration modal */}
      {showCollabForm && (
        <Modal title={editingCollab ? "Edit Collaboration" : "Add Collaboration"} onClose={() => setShowCollabForm(false)}>
          <div className="space-y-3">
            <Field label="Collaborator Name *" value={collabForm.collaborator_name} onChange={(v) => setCollabForm({ ...collabForm, collaborator_name: v })} />
            <div className="grid sm:grid-cols-2 gap-3">
              <Field label="Email" value={collabForm.collaborator_email} onChange={(v) => setCollabForm({ ...collabForm, collaborator_email: v })} />
              <Field label="Affiliation" value={collabForm.collaborator_affiliation} onChange={(v) => setCollabForm({ ...collabForm, collaborator_affiliation: v })} />
            </div>
            <Field label="Project Title" value={collabForm.project_title} onChange={(v) => setCollabForm({ ...collabForm, project_title: v })} />
            <FieldArea label="Description" value={collabForm.description} onChange={(v) => setCollabForm({ ...collabForm, description: v })} />
            <div className="grid sm:grid-cols-3 gap-3">
              <Field label="Start Date" type="date" value={collabForm.start_date} onChange={(v) => setCollabForm({ ...collabForm, start_date: v })} />
              <Field label="End Date" type="date" value={collabForm.end_date} onChange={(v) => setCollabForm({ ...collabForm, end_date: v })} />
              <div>
                <label className="label">Status</label>
                <select className="input" value={collabForm.status} onChange={(e) => setCollabForm({ ...collabForm, status: e.target.value })}>
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                  <option value="paused">Paused</option>
                </select>
              </div>
            </div>
            <div className="flex gap-2 pt-2">
              <button onClick={saveCollab} className="btn-primary">{editingCollab ? "Update" : "Create"}</button>
              <button onClick={() => setShowCollabForm(false)} className="btn-secondary">Cancel</button>
            </div>
          </div>
        </Modal>
      )}

      {/* Funding history modal */}
      {showFundingForm && (
        <Modal title={editingFunding ? "Edit Funding Record" : "Add Funding Record"} onClose={() => setShowFundingForm(false)}>
          <div className="space-y-3">
            <Field label="Title *" value={fundingForm.title} onChange={(v) => setFundingForm({ ...fundingForm, title: v })} />
            <div className="grid sm:grid-cols-2 gap-3">
              <Field label="Organization" value={fundingForm.organization} onChange={(v) => setFundingForm({ ...fundingForm, organization: v })} />
              <Field label="Amount" type="number" value={fundingForm.amount} onChange={(v) => setFundingForm({ ...fundingForm, amount: v })} />
            </div>
            <div className="grid sm:grid-cols-2 gap-3">
              <div>
                <label className="label">Currency</label>
                <select className="input" value={fundingForm.currency} onChange={(e) => setFundingForm({ ...fundingForm, currency: e.target.value })}>
                  <option>USD</option>
                  <option>EUR</option>
                  <option>GBP</option>
                  <option>INR</option>
                  <option>JPY</option>
                </select>
              </div>
              <div>
                <label className="label">Status</label>
                <select className="input" value={fundingForm.status} onChange={(e) => setFundingForm({ ...fundingForm, status: e.target.value })}>
                  <option value="awarded">Awarded</option>
                  <option value="pending">Pending</option>
                  <option value="completed">Completed</option>
                  <option value="declined">Declined</option>
                </select>
              </div>
            </div>
            <div className="grid sm:grid-cols-2 gap-3">
              <Field label="Awarded Date" type="date" value={fundingForm.awarded_date} onChange={(v) => setFundingForm({ ...fundingForm, awarded_date: v })} />
              <Field label="End Date" type="date" value={fundingForm.end_date} onChange={(v) => setFundingForm({ ...fundingForm, end_date: v })} />
            </div>
            <FieldArea label="Description" value={fundingForm.description} onChange={(v) => setFundingForm({ ...fundingForm, description: v })} />
            <div className="flex gap-2 pt-2">
              <button onClick={saveFunding} className="btn-primary">{editingFunding ? "Update" : "Create"}</button>
              <button onClick={() => setShowFundingForm(false)} className="btn-secondary">Cancel</button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}

const emptyCollab = {
  collaborator_name: "",
  collaborator_email: "",
  collaborator_affiliation: "",
  project_title: "",
  description: "",
  status: "active",
  start_date: "",
  end_date: "",
};

const emptyFunding = {
  title: "",
  organization: "",
  amount: 0,
  currency: "USD",
  status: "awarded",
  awarded_date: "",
  end_date: "",
  description: "",
};

function Modal({ title, onClose, children }) {
  return (
    <div className="fixed inset-0 bg-black/50 z-40 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
        <h2 className="text-xl font-bold mb-4">{title}</h2>
        {children}
      </div>
    </div>
  );
}

function StatBox({ label, value }) {
  return (
    <div className="card text-center">
      <div className="text-2xl font-bold text-slate-800">{value}</div>
      <div className="text-xs text-slate-500">{label}</div>
    </div>
  );
}

function Field({ label, value, onChange, type = "text" }) {
  return (
    <div>
      <label className="label">{label}</label>
      <input type={type} className="input" value={value || ""} onChange={(e) => onChange(e.target.value)} />
    </div>
  );
}

function FieldArea({ label, value, onChange }) {
  return (
    <div>
      <label className="label">{label}</label>
      <textarea className="input min-h-[100px]" value={value || ""} onChange={(e) => onChange(e.target.value)} />
    </div>
  );
}
