"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

import { apiRequest } from "@/lib/api";

type AnalyticsData = {
  total_users: number;
  verified_users: number;
  pending_users: number;
  roles: {
    Admin: number;
    Researcher: number;
    Investor: number;
    "Startup Founder": number;
    University: number;
    "Funding Agency": number;
    "Industry Partner": number;
  };
};

export default function PlatformAnalyticsPage() {
  const router = useRouter();

  const [data, setData] =
    useState<AnalyticsData | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await apiRequest(
        "/users/admin/analytics"
      );

      console.log(
        "PLATFORM ANALYTICS:",
        response
      );

      setData(response);

    } catch (err: any) {
      console.error(
        "Analytics error:",
        err
      );

      setError(
        err?.message ||
          "Failed to load platform analytics"
      );

    } finally {
      setLoading(false);
    }
  };

  /* =========================================================
     LOADING
  ========================================================= */

  if (loading) {
    return (
      <main className="min-h-screen bg-[#06111f] flex items-center justify-center text-white">

        <div className="text-center">

          <div className="text-2xl font-bold text-cyan-400">
            Loading Platform Analytics...
          </div>

          <p className="mt-3 text-slate-400">
            Fetching real platform data
          </p>

        </div>

      </main>
    );
  }

  /* =========================================================
     ERROR
  ========================================================= */

  if (error) {
    return (
      <main className="min-h-screen bg-[#06111f] flex items-center justify-center px-6">

        <div className="max-w-md rounded-2xl border border-red-500/30 bg-red-500/10 p-8 text-center">

          <div className="text-4xl">
            ⚠️
          </div>

          <h1 className="mt-4 text-2xl font-bold text-red-400">
            Unable to Load Analytics
          </h1>

          <p className="mt-3 text-slate-300">
            {error}
          </p>

          <div className="mt-6 flex justify-center gap-3">

            <button
              onClick={loadAnalytics}
              className="rounded-xl bg-cyan-500 px-5 py-3 font-semibold text-black hover:bg-cyan-400"
            >
              Retry
            </button>

            <button
              onClick={() =>
                router.push("/dashboard")
              }
              className="rounded-xl border border-slate-600 px-5 py-3 font-semibold text-white hover:border-slate-400"
            >
              Dashboard
            </button>

          </div>

        </div>

      </main>
    );
  }

  if (!data) {
    return null;
  }

  /* =========================================================
     ROLE CHART DATA
  ========================================================= */

  const roleData = [
    {
      name: "Admin",
      users: data.roles.Admin,
    },
    {
      name: "Researcher",
      users: data.roles.Researcher,
    },
    {
      name: "Investor",
      users: data.roles.Investor,
    },
    {
      name: "Startup",
      users: data.roles["Startup Founder"],
    },
    {
      name: "University",
      users: data.roles.University,
    },
    {
      name: "Funding Agency",
      users: data.roles["Funding Agency"],
    },
    {
      name: "Industry",
      users: data.roles["Industry Partner"],
    },
  ];

  /* =========================================================
     VERIFICATION CHART DATA
  ========================================================= */

  const verificationData = [
    {
      name: "Verified",
      value: data.verified_users,
    },
    {
      name: "Pending",
      value: data.pending_users,
    },
  ];

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
              Platform Analytics
            </p>

          </div>

          <button
            onClick={() =>
              router.push("/dashboard")
            }
            className="rounded-xl border border-slate-700 px-5 py-2.5 text-sm font-semibold text-slate-300 hover:border-cyan-400 hover:text-cyan-400"
          >
            ← Dashboard
          </button>

        </div>

      </header>

      {/* =====================================================
          CONTENT
      ===================================================== */}

      <section className="mx-auto max-w-7xl px-8 py-10">

        <div className="mb-10">

          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-400">
            Administration
          </p>

          <h1 className="mt-3 text-4xl font-bold">
            Platform Analysis
          </h1>

          <p className="mt-3 text-slate-400">
            Real-time overview of users and platform
            participation.
          </p>

        </div>

        {/* ===================================================
            SUMMARY CARDS
        =================================================== */}

        <div className="grid gap-6 md:grid-cols-3">

          <SummaryCard
            title="Total Users"
            value={data.total_users}
            icon="👥"
            description="All registered users"
          />

          <SummaryCard
            title="Verified Users"
            value={data.verified_users}
            icon="✅"
            description="Approved accounts"
          />

          <SummaryCard
            title="Pending Users"
            value={data.pending_users}
            icon="⏳"
            description="Waiting for verification"
          />

        </div>

        {/* ===================================================
            CHARTS
        =================================================== */}

        <div className="mt-8 grid gap-8 lg:grid-cols-2">

          {/* ===============================================
              ROLE DISTRIBUTION
          =============================================== */}

          <div className="rounded-2xl border border-slate-800 bg-[#0c1929] p-7">

            <h2 className="text-xl font-bold">
              User Distribution by Role
            </h2>

            <p className="mt-2 text-sm text-slate-500">
              Number of users in each stakeholder category.
            </p>

            <div className="mt-8 h-[380px]">

              <ResponsiveContainer
                width="100%"
                height="100%"
              >

                <BarChart
                  data={roleData}
                  margin={{
                    top: 10,
                    right: 10,
                    left: 0,
                    bottom: 60,
                  }}
                >

                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#1e293b"
                  />

                  <XAxis
                    dataKey="name"
                    angle={-35}
                    textAnchor="end"
                    interval={0}
                    height={80}
                    stroke="#94a3b8"
                    tick={{
                      fontSize: 11,
                    }}
                  />

                  <YAxis
                    allowDecimals={false}
                    stroke="#94a3b8"
                  />

                  <Tooltip
                    contentStyle={{
                      backgroundColor:
                        "#0f172a",
                      border:
                        "1px solid #334155",
                      borderRadius:
                        "10px",
                      color: "#fff",
                    }}
                  />

                  <Bar
                    dataKey="users"
                    fill="#22d3ee"
                    radius={[
                      6,
                      6,
                      0,
                      0,
                    ]}
                  />

                </BarChart>

              </ResponsiveContainer>

            </div>

          </div>

          {/* ===============================================
              VERIFICATION STATUS
          =============================================== */}

          <div className="rounded-2xl border border-slate-800 bg-[#0c1929] p-7">

            <h2 className="text-xl font-bold">
              Account Verification
            </h2>

            <p className="mt-2 text-sm text-slate-500">
              Verified versus pending user accounts.
            </p>

            <div className="mt-8 h-[380px]">

              <ResponsiveContainer
                width="100%"
                height="100%"
              >

                <PieChart>

                  <Pie
                    data={verificationData}
                    cx="50%"
                    cy="50%"
                    innerRadius={85}
                    outerRadius={135}
                    paddingAngle={4}
                    dataKey="value"
                  >

                    <Cell fill="#22c55e" />
                    <Cell fill="#f59e0b" />

                  </Pie>

                  <Tooltip
                    contentStyle={{
                      backgroundColor:
                        "#0f172a",
                      border:
                        "1px solid #334155",
                      borderRadius:
                        "10px",
                      color: "#fff",
                    }}
                  />

                  <Legend />

                </PieChart>

              </ResponsiveContainer>

            </div>

          </div>

        </div>

        {/* ===================================================
            ROLE SUMMARY TABLE
        =================================================== */}

        <div className="mt-8 rounded-2xl border border-slate-800 bg-[#0c1929] p-7">

          <div className="flex items-center justify-between">

            <div>

              <h2 className="text-xl font-bold">
                Role Summary
              </h2>

              <p className="mt-2 text-sm text-slate-500">
                Current distribution across all stakeholder roles.
              </p>

            </div>

            <button
              onClick={loadAnalytics}
              className="rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:border-cyan-400 hover:text-cyan-400"
            >
              ↻ Refresh
            </button>

          </div>

          <div className="mt-6 overflow-x-auto">

            <table className="w-full text-left">

              <thead>

                <tr className="border-b border-slate-800 text-sm text-slate-500">

                  <th className="px-4 py-4">
                    Role
                  </th>

                  <th className="px-4 py-4">
                    Users
                  </th>

                  <th className="px-4 py-4">
                    Percentage
                  </th>

                </tr>

              </thead>

              <tbody>

                {roleData.map((role) => {

                  const percentage =
                    data.total_users > 0
                      ? (
                          (role.users /
                            data.total_users) *
                          100
                        ).toFixed(1)
                      : "0.0";

                  return (
                    <tr
                      key={role.name}
                      className="border-b border-slate-800/60"
                    >

                      <td className="px-4 py-4 font-medium">
                        {role.name}
                      </td>

                      <td className="px-4 py-4 text-cyan-400 font-semibold">
                        {role.users}
                      </td>

                      <td className="px-4 py-4 text-slate-400">
                        {percentage}%
                      </td>

                    </tr>
                  );

                })}

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
  description,
}: {
  title: string;
  value: number;
  icon: string;
  description: string;
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

      <p className="mt-4 text-sm text-slate-500">
        {description}
      </p>

    </div>
  );
}