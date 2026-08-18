"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiRequest } from "@/lib/api";

type User = {
  id: number;
  full_name: string;
  email: string;
  role: string;
  is_verified: boolean;
};

const ROLES = [
  "Researcher",
  "Investor",
  "Startup Founder",
  "University",
  "Funding Agency",
  "Industry Partner",
  "Admin",
];

export default function UserManagementPage() {
  const router = useRouter();

  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");

  const [processingId, setProcessingId] =
    useState<number | null>(null);

  const [message, setMessage] = useState("");

  useEffect(() => {
    loadUsers();
  }, []);

  /* =========================================================
     LOAD USERS
  ========================================================= */

  const loadUsers = async () => {
    try {
      setLoading(true);
      setError("");
      setMessage("");

      const response = await apiRequest(
        "/users/admin/users"
      );

      console.log(
        "ADMIN USERS:",
        response
      );

      setUsers(response.users || []);

    } catch (err: any) {
      console.error(
        "Load users error:",
        err
      );

      setError(
        err?.message ||
          "Failed to load users"
      );

    } finally {
      setLoading(false);
    }
  };

  /* =========================================================
     VERIFY USER
  ========================================================= */

  const handleVerify = async (
    userId: number
  ) => {
    try {
      setProcessingId(userId);
      setError("");
      setMessage("");

      await apiRequest(
        `/users/verify-user/${userId}`,
        {
          method: "PUT",
        }
      );

      setMessage(
        "User verified successfully."
      );

      // Update only the affected user
      setUsers((previousUsers) =>
        previousUsers.map((user) =>
          user.id === userId
            ? {
                ...user,
                is_verified: true,
              }
            : user
        )
      );

    } catch (err: any) {
      console.error(
        "Verify user error:",
        err
      );

      setError(
        err?.message ||
          "Failed to verify user"
      );

    } finally {
      setProcessingId(null);
    }
  };

  /* =========================================================
     CHANGE ROLE
  ========================================================= */

  const handleRoleChange = async (
    userId: number,
    newRole: string
  ) => {
    try {
      setProcessingId(userId);
      setError("");
      setMessage("");

      await apiRequest(
        `/users/admin/users/${userId}/role?new_role=${encodeURIComponent(
          newRole
        )}`,
        {
          method: "PUT",
        }
      );

      setMessage(
        "User role updated successfully."
      );

      setUsers((previousUsers) =>
        previousUsers.map((user) =>
          user.id === userId
            ? {
                ...user,
                role: newRole,
              }
            : user
        )
      );

    } catch (err: any) {
      console.error(
        "Change role error:",
        err
      );

      setError(
        err?.message ||
          "Failed to change user role"
      );

    } finally {
      setProcessingId(null);
    }
  };

  /* =========================================================
     FILTER USERS
  ========================================================= */

  const filteredUsers = users.filter(
    (user) => {
      const searchValue =
        search.toLowerCase();

      return (
        user.full_name
          .toLowerCase()
          .includes(searchValue) ||
        user.email
          .toLowerCase()
          .includes(searchValue) ||
        user.role
          .toLowerCase()
          .includes(searchValue)
      );
    }
  );

  /* =========================================================
     STATISTICS
  ========================================================= */

  const totalUsers =
    users.length;

  const verifiedUsers =
    users.filter(
      (user) => user.is_verified
    ).length;

  const pendingUsers =
    users.filter(
      (user) => !user.is_verified
    ).length;

  /* =========================================================
     LOADING
  ========================================================= */

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#06111f] text-white">

        <div className="text-center">

          <div className="text-2xl font-bold text-cyan-400">
            Loading Users...
          </div>

          <p className="mt-3 text-slate-400">
            Fetching platform users
          </p>

        </div>

      </main>
    );
  }

  /* =========================================================
     PAGE
  ========================================================= */

  return (
    <main className="min-h-screen bg-[#06111f] text-white">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <header className="border-b border-slate-800 bg-[#071321]">

        <div className="mx-auto flex max-w-7xl items-center justify-between px-8 py-5">

          <div>

            <button
              onClick={() =>
                router.push("/dashboard")
              }
              className="text-2xl font-bold"
            >

              <span className="text-cyan-400">
                Inno
              </span>

              <span className="text-white">
                Bridge
              </span>

              <span className="text-indigo-400">
                -AI
              </span>

            </button>

            <p className="mt-1 text-sm text-slate-500">
              Administration
            </p>

          </div>

          <button
            onClick={() =>
              router.push("/dashboard")
            }
            className="rounded-xl border border-slate-700 px-5 py-2.5 text-sm font-semibold text-slate-300 transition hover:border-cyan-400 hover:text-cyan-400"
          >
            ← Dashboard
          </button>

        </div>

      </header>

      {/* =====================================================
          CONTENT
      ===================================================== */}

      <section className="mx-auto max-w-7xl px-8 py-10">

        {/* ===================================================
            TITLE
        =================================================== */}

        <div className="mb-10">

          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-red-400">
            Administration
          </p>

          <h1 className="mt-3 text-4xl font-bold">
            User Management
          </h1>

          <p className="mt-3 text-slate-400">
            View, verify and manage InnoBridge-AI users.
          </p>

        </div>

        {/* ===================================================
            SUCCESS MESSAGE
        =================================================== */}

        {message && (
          <div className="mb-6 rounded-xl border border-green-500/30 bg-green-500/10 px-5 py-4 text-green-400">
            ✅ {message}
          </div>
        )}

        {/* ===================================================
            ERROR MESSAGE
        =================================================== */}

        {error && (
          <div className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-red-400">
            ⚠️ {error}
          </div>
        )}

        {/* ===================================================
            SUMMARY CARDS
        =================================================== */}

        <div className="grid gap-6 md:grid-cols-3">

          <SummaryCard
            title="Total Users"
            value={totalUsers}
            icon="👥"
          />

          <SummaryCard
            title="Verified Users"
            value={verifiedUsers}
            icon="✅"
          />

          <SummaryCard
            title="Pending Verification"
            value={pendingUsers}
            icon="⏳"
          />

        </div>

        {/* ===================================================
            SEARCH + REFRESH
        =================================================== */}

        <div className="mt-8 rounded-2xl border border-slate-800 bg-[#0c1929] p-6">

          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

            <div className="flex-1">

              <label className="mb-2 block text-sm text-slate-400">
                Search Users
              </label>

              <input
                type="text"
                value={search}
                onChange={(e) =>
                  setSearch(e.target.value)
                }
                placeholder="Search by name, email or role..."
                className="w-full rounded-xl border border-slate-700 bg-[#071321] px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-400"
              />

            </div>

            <button
              onClick={loadUsers}
              className="rounded-xl border border-slate-700 px-5 py-3 font-semibold text-slate-300 transition hover:border-cyan-400 hover:text-cyan-400"
            >
              ↻ Refresh
            </button>

          </div>

        </div>

        {/* ===================================================
            USERS TABLE
        =================================================== */}

        <div className="mt-8 overflow-hidden rounded-2xl border border-slate-800 bg-[#0c1929]">

          <div className="border-b border-slate-800 px-6 py-5">

            <h2 className="text-xl font-bold">
              Registered Users
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Showing {filteredUsers.length} of{" "}
              {users.length} users
            </p>

          </div>

          <div className="overflow-x-auto">

            <table className="w-full min-w-[950px]">

              <thead>

                <tr className="border-b border-slate-800 text-left text-sm text-slate-500">

                  <th className="px-6 py-4">
                    ID
                  </th>

                  <th className="px-6 py-4">
                    User
                  </th>

                  <th className="px-6 py-4">
                    Email
                  </th>

                  <th className="px-6 py-4">
                    Role
                  </th>

                  <th className="px-6 py-4">
                    Status
                  </th>

                  <th className="px-6 py-4">
                    Actions
                  </th>

                </tr>

              </thead>

              <tbody>

                {filteredUsers.length === 0 ? (

                  <tr>

                    <td
                      colSpan={6}
                      className="px-6 py-12 text-center text-slate-500"
                    >
                      {search
                        ? "No users match your search."
                        : "No users found."}
                    </td>

                  </tr>

                ) : (

                  filteredUsers.map(
                    (user) => (

                      <tr
                        key={user.id}
                        className="border-b border-slate-800/60 transition hover:bg-slate-800/20"
                      >

                        {/* ID */}

                        <td className="px-6 py-5 text-slate-500">
                          #{user.id}
                        </td>

                        {/* NAME */}

                        <td className="px-6 py-5">

                          <div className="flex items-center gap-3">

                            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-cyan-500/10 font-bold text-cyan-400">
                              {user.full_name
                                .charAt(0)
                                .toUpperCase()}
                            </div>

                            <div>

                              <p className="font-semibold">
                                {user.full_name}
                              </p>

                            </div>

                          </div>

                        </td>

                        {/* EMAIL */}

                        <td className="px-6 py-5 text-sm text-slate-400">
                          {user.email}
                        </td>

                        {/* ROLE */}

                        <td className="px-6 py-5">

                          <select
                            value={user.role}
                            disabled={
                              processingId ===
                              user.id
                            }
                            onChange={(e) =>
                              handleRoleChange(
                                user.id,
                                e.target.value
                              )
                            }
                            className="rounded-lg border border-slate-700 bg-[#071321] px-3 py-2 text-sm text-slate-300 outline-none focus:border-cyan-400 disabled:opacity-50"
                          >

                            {ROLES.map(
                              (role) => (
                                <option
                                  key={role}
                                  value={role}
                                >
                                  {role}
                                </option>
                              )
                            )}

                          </select>

                        </td>

                        {/* STATUS */}

                        <td className="px-6 py-5">

                          {user.is_verified ? (

                            <span className="inline-flex items-center rounded-full border border-green-500/30 bg-green-500/10 px-3 py-1 text-xs font-semibold text-green-400">
                              ✓ Verified
                            </span>

                          ) : (

                            <span className="inline-flex items-center rounded-full border border-yellow-500/30 bg-yellow-500/10 px-3 py-1 text-xs font-semibold text-yellow-400">
                              ⏳ Pending
                            </span>

                          )}

                        </td>

                        {/* ACTIONS */}

                        <td className="px-6 py-5">

                          {!user.is_verified ? (

                            <button
                              onClick={() =>
                                handleVerify(
                                  user.id
                                )
                              }
                              disabled={
                                processingId ===
                                user.id
                              }
                              className="rounded-lg bg-green-500 px-4 py-2 text-sm font-semibold text-black transition hover:bg-green-400 disabled:cursor-not-allowed disabled:opacity-50"
                            >
                              {processingId ===
                              user.id
                                ? "Processing..."
                                : "Verify"}
                            </button>

                          ) : (

                            <span className="text-sm text-slate-600">
                              Verified
                            </span>

                          )}

                        </td>

                      </tr>

                    )
                  )

                )}

              </tbody>

            </table>

          </div>

        </div>

      </section>

    </main>
  );
}


/* ============================================================
   SUMMARY CARD
============================================================ */

function SummaryCard({
  title,
  value,
  icon,
}: {
  title: string;
  value: number;
  icon: string;
}) {

  return (
    <div className="rounded-2xl border border-slate-800 bg-[#0c1929] p-7 transition hover:border-cyan-400/40">

      <div className="flex items-center justify-between">

        <div>

          <p className="text-sm text-slate-500">
            {title}
          </p>

          <p className="mt-3 text-4xl font-bold text-cyan-400">
            {value}
          </p>

        </div>

        <div className="text-3xl">
          {icon}
        </div>

      </div>

    </div>
  );
}