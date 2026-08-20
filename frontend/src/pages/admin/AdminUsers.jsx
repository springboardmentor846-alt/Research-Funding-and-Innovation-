import { useEffect, useState } from "react";
import {
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Search,
  ShieldCheck,
  UserCog,
  UserRoundX,
} from "lucide-react";
import {
  getAdminUsers,
  updateAdminUserRole,
  updateAdminUserStatus,
} from "../../api/admin";

const ROLE_OPTIONS = [
  { value: "all", label: "All roles" },
  { value: "researcher", label: "Researchers" },
  { value: "startup_founder", label: "Startup founders" },
  { value: "administrator", label: "Administrators" },
];

function roleLabel(role) {
  if (role === "startup_founder") return "Startup Founder";
  if (role === "administrator") return "Administrator";
  return "Researcher";
}

export default function AdminUsers() {
  const [users, setUsers] = useState([]);
  const [search, setSearch] = useState("");
  const [role, setRole] = useState("all");
  const [status, setStatus] = useState("all");
  const [page, setPage] = useState(1);
  const [meta, setMeta] = useState({
    total: 0,
    total_pages: 0,
    page_size: 10,
  });
  const [loading, setLoading] = useState(true);
  const [savingId, setSavingId] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const loadUsers = async (targetPage = page) => {
    try {
      setLoading(true);
      setError("");

      const data = await getAdminUsers({
        search: search.trim() || undefined,
        role: role === "all" ? undefined : role,
        status: status === "all" ? undefined : status,
        page: targetPage,
        page_size: 10,
      });

      setUsers(data.users);
      setMeta({
        total: data.total,
        total_pages: data.total_pages,
        page_size: data.page_size,
      });
      setPage(data.page);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to load users."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers(1);
    // Filters are intentionally applied only when the user submits.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [role, status]);

  const handleSearch = (event) => {
    event.preventDefault();
    loadUsers(1);
  };

  const handleStatus = async (user) => {
    const nextStatus = !user.is_active;
    const action = nextStatus ? "activate" : "deactivate";

    if (!window.confirm(`Are you sure you want to ${action} ${user.full_name}?`)) {
      return;
    }

    try {
      setSavingId(user.user_id);
      setMessage("");
      setError("");

      const response = await updateAdminUserStatus(
        user.user_id,
        nextStatus
      );

      setMessage(response.message);
      await loadUsers(page);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to update the user's status."
      );
    } finally {
      setSavingId(null);
    }
  };

  const handleRole = async (user, nextRole) => {
    if (nextRole === user.role) return;

    if (
      !window.confirm(
        `Change ${user.full_name}'s role from ${roleLabel(user.role)} to ${roleLabel(nextRole)}?`
      )
    ) {
      return;
    }

    try {
      setSavingId(user.user_id);
      setMessage("");
      setError("");

      const response = await updateAdminUserRole(
        user.user_id,
        nextRole
      );

      setMessage(response.message);
      await loadUsers(page);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to update the user's role."
      );
    } finally {
      setSavingId(null);
    }
  };

  return (
    <div className="admin-page">
      <div className="admin-page-header">
        <div>
          <span className="admin-eyebrow">ADMINISTRATION</span>
          <h1>User management</h1>
          <p>
            Review platform accounts and control role-based access.
          </p>
        </div>

        <div className="admin-secure-chip">
          <ShieldCheck size={15} />
          Administrator only
        </div>
      </div>

      {message && (
        <div className="admin-alert success">
          <CheckCircle2 size={16} />
          {message}
        </div>
      )}

      {error && <div className="admin-alert error">{error}</div>}

      <section className="admin-panel">
        <div className="admin-user-toolbar">
          <form className="admin-search-form" onSubmit={handleSearch}>
            <Search size={17} />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search by name or email..."
              aria-label="Search users"
            />
            <button type="submit">Search</button>
          </form>

          <div className="admin-filter-group">
            <select
              value={role}
              onChange={(event) => setRole(event.target.value)}
              aria-label="Filter by role"
            >
              {ROLE_OPTIONS.map((item) => (
                <option value={item.value} key={item.value}>
                  {item.label}
                </option>
              ))}
            </select>

            <select
              value={status}
              onChange={(event) => setStatus(event.target.value)}
              aria-label="Filter by account status"
            >
              <option value="all">All status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
        </div>

        <div className="admin-table-wrap">
          {loading ? (
            <div className="admin-loading table-loading">
              <div className="spinner-border text-primary" role="status" />
              <span>Loading users...</span>
            </div>
          ) : (
            <table className="admin-table admin-user-table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Registered</th>
                  <th>Access control</th>
                </tr>
              </thead>

              <tbody>
                {users.length ? (
                  users.map((user) => {
                    const isSaving = savingId === user.user_id;

                    return (
                      <tr key={user.user_id}>
                        <td>
                          <div className="admin-user-cell">
                            <span className="admin-table-avatar">
                              {user.full_name.charAt(0).toUpperCase()}
                            </span>
                            <div>
                              <strong>{user.full_name}</strong>
                              <small>{user.email}</small>
                            </div>
                          </div>
                        </td>

                        <td>
                          <select
                            className="admin-role-select"
                            value={user.role}
                            disabled={isSaving}
                            onChange={(event) =>
                              handleRole(user, event.target.value)
                            }
                          >
                            <option value="researcher">Researcher</option>
                            <option value="startup_founder">Startup Founder</option>
                            <option value="administrator">Administrator</option>
                          </select>
                        </td>

                        <td>
                          <span
                            className={`admin-status ${
                              user.is_active ? "active" : "inactive"
                            }`}
                          >
                            {user.is_active ? "Active" : "Inactive"}
                          </span>
                        </td>

                        <td>
                          <span className="admin-date">
                            {user.created_at
                              ? new Date(user.created_at).toLocaleDateString()
                              : "—"}
                          </span>
                        </td>

                        <td>
                          <button
                            type="button"
                            className={`admin-access-btn ${
                              user.is_active ? "disable" : "enable"
                            }`}
                            disabled={isSaving}
                            onClick={() => handleStatus(user)}
                          >
                            {user.is_active ? (
                              <>
                                <UserRoundX size={15} />
                                Deactivate
                              </>
                            ) : (
                              <>
                                <UserCog size={15} />
                                Activate
                              </>
                            )}
                          </button>
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan="5" className="admin-empty-cell">
                      No users match the selected filters.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </div>

        <div className="admin-pagination">
          <span>
            Showing {users.length} of {meta.total} users
          </span>

          <div>
            <button
              type="button"
              disabled={page <= 1 || loading}
              onClick={() => loadUsers(page - 1)}
              aria-label="Previous page"
            >
              <ChevronLeft size={16} />
            </button>

            <strong>
              {meta.total_pages ? page : 0} / {meta.total_pages || 0}
            </strong>

            <button
              type="button"
              disabled={page >= meta.total_pages || loading}
              onClick={() => loadUsers(page + 1)}
              aria-label="Next page"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </section>

      <section className="admin-control-note">
        <ShieldCheck size={18} />
        <div>
          <strong>Access controls are enforced by the backend.</strong>
          <p>
            Administrator routes use role-based authorization, so hiding this
            section in the interface is not the security boundary.
          </p>
        </div>
      </section>
    </div>
  );
}
