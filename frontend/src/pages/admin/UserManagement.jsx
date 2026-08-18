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
  Field,
  downloadFile,
} from "../../components/admin/ui.jsx";

const ROLE_OPTIONS = [
  { value: "", label: "All roles" },
  { value: "researcher", label: "Researchers" },
  { value: "startup_founder", label: "Startup Founders" },
  { value: "innovation_manager", label: "Innovation Managers" },
  { value: "admin", label: "Admins" },
];

const STATUS_OPTIONS = [
  { value: "", label: "All statuses" },
  { value: "true", label: "Active" },
  { value: "false", label: "Inactive" },
];

const ROLE_BADGE = {
  researcher: "primary",
  startup_founder: "purple",
  innovation_manager: "warning",
  admin: "danger",
};

const ROLE_LABEL = {
  researcher: "Researcher",
  startup_founder: "Startup Founder",
  innovation_manager: "Innovation Manager",
  admin: "Admin",
};

function EditUserModal({ user, onClose, onSaved }) {
  const [form, setForm] = useState({
    full_name: user.full_name || "",
    affiliation: user.affiliation || "",
    is_active: user.is_active,
    is_verified: user.is_verified,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function save(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      await adminAPI.updateUser(user.id, form);
      onSaved("User updated");
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update user");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 p-4" onClick={saving ? undefined : onClose}>
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-lg"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800">Edit User</h2>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-800">✕</button>
        </div>
        <form onSubmit={save}>
          <div className="px-6 py-5 space-y-4">
            {error && <div className="card bg-red-50 text-red-700 text-sm">{error}</div>}
            <div className="p-3 rounded-lg bg-slate-50 text-sm">
              <div><strong>{user.username}</strong> · {user.email}</div>
              <div className="text-slate-500 text-xs mt-1">
                Role: {ROLE_LABEL[user.role] || user.role} (cannot be changed by admin)
              </div>
            </div>
            <Field label="Full name" required>
              <input
                className="input"
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                required
              />
            </Field>
            <Field label="Affiliation">
              <input
                className="input"
                value={form.affiliation}
                onChange={(e) => setForm({ ...form, affiliation: e.target.value })}
              />
            </Field>
            <div className="flex items-center gap-6">
              <label className="inline-flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-slate-300 text-primary-600"
                  checked={form.is_active}
                  onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                />
                Account active
              </label>
              <label className="inline-flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-slate-300 text-primary-600"
                  checked={form.is_verified}
                  onChange={(e) => setForm({ ...form, is_verified: e.target.checked })}
                />
                Verified
              </label>
            </div>
          </div>
          <div className="px-6 py-4 border-t border-slate-200 flex justify-end gap-2">
            <button type="button" onClick={onClose} className="btn-secondary" disabled={saving}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function UserDetailModal({ userId, onClose }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    adminAPI
      .getUser(userId)
      .then((r) => setUser(r.data))
      .catch((err) => setError(err.response?.data?.detail || "Failed to load user"))
      .finally(() => setLoading(false));
  }, [userId]);

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 p-4" onClick={onClose}>
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800">User Details</h2>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-800">✕</button>
        </div>
        <div className="px-6 py-5">
          {loading ? (
            <p className="text-sm text-slate-500">Loading...</p>
          ) : error ? (
            <div className="card bg-red-50 text-red-700 text-sm">{error}</div>
          ) : user ? (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-lg font-bold">
                  {(user.full_name || user.username).charAt(0).toUpperCase()}
                </div>
                <div>
                  <div className="font-semibold text-slate-800">{user.full_name || user.username}</div>
                  <div className="text-sm text-slate-500">{user.email} · @{user.username}</div>
                  <div className="mt-1 flex flex-wrap gap-2">
                    <Badge tone={ROLE_BADGE[user.role]}>{ROLE_LABEL[user.role] || user.role}</Badge>
                    {user.is_active ? <Badge tone="success">Active</Badge> : <Badge tone="danger">Inactive</Badge>}
                    {user.is_verified && <Badge tone="blue">Verified</Badge>}
                  </div>
                </div>
              </div>
              <div className="grid sm:grid-cols-2 gap-3 text-sm">
                <div><span className="text-slate-500">Affiliation:</span> {user.affiliation || "—"}</div>
                <div><span className="text-slate-500">ORCID:</span> {user.orcid || "—"}</div>
                <div><span className="text-slate-500">H-Index:</span> {user.h_index ?? 0}</div>
                <div><span className="text-slate-500">i10-Index:</span> {user.i10_index ?? 0}</div>
                <div><span className="text-slate-500">Citations:</span> {user.citation_count ?? 0}</div>
                <div><span className="text-slate-500">Joined:</span> {user.created_at ? new Date(user.created_at).toLocaleDateString() : "—"}</div>
                <div><span className="text-slate-500">Last Login:</span> {user.last_login ? new Date(user.last_login).toLocaleString() : "Never"}</div>
              </div>
              {user.bio && (
                <div>
                  <div className="text-xs text-slate-500 mb-1">Bio</div>
                  <div className="text-sm text-slate-700">{user.bio}</div>
                </div>
              )}
              {user.research_interests && (
                <div>
                  <div className="text-xs text-slate-500 mb-1">Research Interests</div>
                  <div className="flex flex-wrap gap-1">
                    {user.research_interests.split(",").map((s, i) => (
                      <Badge key={i} tone="primary">{s.trim()}</Badge>
                    ))}
                  </div>
                </div>
              )}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded-lg bg-blue-50 text-center">
                  <div className="text-lg font-bold text-blue-700">{user.stats?.publications_count ?? 0}</div>
                  <div className="text-xs text-slate-600">Publications</div>
                </div>
                <div className="p-3 rounded-lg bg-purple-50 text-center">
                  <div className="text-lg font-bold text-purple-700">{user.stats?.recommendations_count ?? 0}</div>
                  <div className="text-xs text-slate-600">Recommendations</div>
                </div>
                <div className="p-3 rounded-lg bg-green-50 text-center">
                  <div className="text-lg font-bold text-green-700">{user.stats?.collaborations_count ?? 0}</div>
                  <div className="text-xs text-slate-600">Collaborations</div>
                </div>
                <div className="p-3 rounded-lg bg-amber-50 text-center">
                  <div className="text-lg font-bold text-amber-700">{user.stats?.funding_history_count ?? 0}</div>
                  <div className="text-xs text-slate-600">Funding History</div>
                </div>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

export default function UserManagement() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [search, setSearch] = useState("");
  const [role, setRole] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [editing, setEditing] = useState(null);
  const [viewing, setViewing] = useState(null);
  const [confirm, setConfirm] = useState(null);
  const [busy, setBusy] = useState(false);

  const { toasts, pushToast, dismissToast } = useToasts();

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, search, role, status]);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const params = {
        page,
        page_size: pageSize,
        ...(search ? { search } : {}),
        ...(role ? { role } : {}),
        ...(status ? { is_active: status } : {}),
      };
      const res = await adminAPI.listUsers(params);
      setItems(res.data.items);
      setTotal(res.data.total);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load users");
    } finally {
      setLoading(false);
    }
  }

  async function handleActivate(u) {
    setBusy(true);
    try {
      await adminAPI.activateUser(u.id);
      pushToast(`${u.username} reactivated`, "success");
      load();
    } catch (err) {
      pushToast(err.response?.data?.detail || "Failed to activate user", "error");
    } finally {
      setBusy(false);
    }
  }

  async function handleDeactivate(u) {
    setBusy(true);
    try {
      await adminAPI.deactivateUser(u.id);
      pushToast(`${u.username} deactivated`, "success");
      load();
    } catch (err) {
      pushToast(err.response?.data?.detail || "Failed to deactivate user", "error");
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete() {
    if (!confirm) return;
    setBusy(true);
    try {
      await adminAPI.deleteUser(confirm.id);
      pushToast(`${confirm.username} deleted`, "success");
      setConfirm(null);
      if (items.length === 1 && page > 1) setPage(page - 1);
      else load();
    } catch (err) {
      pushToast(err.response?.data?.detail || "Failed to delete user", "error");
    } finally {
      setBusy(false);
    }
  }

  async function handleExport() {
    try {
      const res = await adminAPI.exportUsers();
      await downloadFile(res, "users_report.csv");
      pushToast("User report exported", "success");
    } catch (err) {
      pushToast("Failed to export users", "error");
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="space-y-4">
      <ToastStack toasts={toasts} onDismiss={dismissToast} />

      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">User Management</h1>
          <p className="text-slate-500 text-sm">
            {total} user{total !== 1 ? "s" : ""} on the platform
          </p>
        </div>
        <button onClick={handleExport} className="btn-secondary text-sm">
          ⬇ Export CSV
        </button>
      </div>

      {error && <ErrorBanner message={error} onRetry={load} />}

      <div className="card flex flex-wrap gap-3">
        <input
          className="input flex-1 min-w-[200px]"
          placeholder="Search by name, email, username..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
        />
        <select
          className="input min-w-[160px]"
          value={role}
          onChange={(e) => {
            setRole(e.target.value);
            setPage(1);
          }}
        >
          {ROLE_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
        <select
          className="input min-w-[140px]"
          value={status}
          onChange={(e) => {
            setStatus(e.target.value);
            setPage(1);
          }}
        >
          {STATUS_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <PageLoader label="Loading users..." />
      ) : items.length === 0 ? (
        <EmptyState
          title="No users found"
          description="Try adjusting your filters or search term."
        />
      ) : (
        <div className="card overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-slate-600 uppercase text-xs">
              <tr>
                <th className="text-left px-4 py-3">User</th>
                <th className="text-left px-4 py-3">Role</th>
                <th className="text-left px-4 py-3">Status</th>
                <th className="text-left px-4 py-3">Affiliation</th>
                <th className="text-left px-4 py-3">Joined</th>
                <th className="text-right px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((u) => (
                <tr key={u.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-sm font-bold flex-shrink-0">
                        {(u.full_name || u.username).charAt(0).toUpperCase()}
                      </div>
                      <div className="min-w-0">
                        <div className="font-medium text-slate-800 truncate">
                          {u.full_name || u.username}
                        </div>
                        <div className="text-xs text-slate-500 truncate">
                          {u.email}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <Badge tone={ROLE_BADGE[u.role]}>{ROLE_LABEL[u.role] || u.role}</Badge>
                  </td>
                  <td className="px-4 py-3">
                    {u.is_active ? (
                      <Badge tone="success">Active</Badge>
                    ) : (
                      <Badge tone="danger">Inactive</Badge>
                    )}
                    {u.is_verified && <Badge tone="blue">Verified</Badge>}
                  </td>
                  <td className="px-4 py-3 text-slate-600 max-w-[200px] truncate">
                    {u.affiliation || "—"}
                  </td>
                  <td className="px-4 py-3 text-slate-500 text-xs">
                    {u.created_at ? new Date(u.created_at).toLocaleDateString() : "—"}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex justify-end gap-1 flex-wrap">
                      <button
                        className="btn-ghost text-xs"
                        onClick={() => setViewing(u.id)}
                      >
                        View
                      </button>
                      <button
                        className="btn-ghost text-xs"
                        onClick={() => setEditing(u)}
                      >
                        Edit
                      </button>
                      {u.is_active ? (
                        <button
                          className="btn-ghost text-xs text-amber-600"
                          disabled={busy}
                          onClick={() => handleDeactivate(u)}
                        >
                          Deactivate
                        </button>
                      ) : (
                        <button
                          className="btn-ghost text-xs text-green-600"
                          disabled={busy}
                          onClick={() => handleActivate(u)}
                        >
                          Activate
                        </button>
                      )}
                      <button
                        className="btn-ghost text-xs text-red-600"
                        disabled={busy}
                        onClick={() => setConfirm(u)}
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

      {editing && (
        <EditUserModal
          user={editing}
          onClose={() => setEditing(null)}
          onSaved={(msg) => {
            pushToast(msg, "success");
            load();
          }}
        />
      )}

      {viewing && (
        <UserDetailModal userId={viewing} onClose={() => setViewing(null)} />
      )}

      <ConfirmDialog
        open={!!confirm}
        title="Delete user permanently"
        description={
          confirm
            ? `This will permanently delete ${confirm.username} (${confirm.email}) and all of their owned data. This action cannot be undone.`
            : ""
        }
        confirmText="Delete"
        busy={busy}
        onConfirm={handleDelete}
        onCancel={() => !busy && setConfirm(null)}
      />
    </div>
  );
}
