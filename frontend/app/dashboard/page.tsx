"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiRequest, logout } from "@/lib/api";
import Sidebar from "@/components/Sidebar";

export default function DashboardPage() {
  const router = useRouter();

  const [dashboardData, setDashboardData] =
    useState<any>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const token =
          localStorage.getItem("access_token");

        if (!token) {
          router.push("/login");
          return;
        }

        const data = await apiRequest(
          "/dashboard/"
        );

        console.log(
          "DASHBOARD RESPONSE:",
          data
        );

        setDashboardData(data);

      } catch (err: any) {
        console.error(
          "Dashboard error:",
          err
        );

        if (
          err.message === "Invalid Token" ||
          err.message === "Not authenticated"
        ) {
          logout();
          router.push("/login");
          return;
        }

        setError(
          err.message ||
            "Unable to load dashboard"
        );

      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, [router]);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  /* =========================================================
     LOADING
  ========================================================= */

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#06111f] text-white">
        <div className="text-xl text-cyan-400">
          Loading dashboard...
        </div>
      </main>
    );
  }

  /* =========================================================
     ERROR
  ========================================================= */

  if (error) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#06111f] px-6 text-white">

        <div className="rounded-2xl border border-red-500/40 bg-red-500/10 p-8 text-center">

          <h1 className="text-2xl font-bold text-red-400">
            Dashboard Error
          </h1>

          <p className="mt-3 text-slate-300">
            {error}
          </p>

          <button
            onClick={() =>
              router.push("/login")
            }
            className="mt-6 rounded-xl bg-cyan-500 px-6 py-3 font-semibold text-black"
          >
            Go to Login
          </button>

        </div>

      </main>
    );
  }

  if (!dashboardData) {
    return null;
  }

  const role =
    dashboardData.role || "";

  const dashboard =
    dashboardData.dashboard || {};

  /* =========================================================
     ROLE PERMISSIONS
  ========================================================= */

  const canAccessResearch =
    [
      "Researcher",
      "Investor",
      "Startup Founder",
      "University",
      "Funding Agency",
      "Industry Partner",
      "Admin",
    ].includes(role);

  const canAccessPatent =
    [
      "Researcher",
      "Investor",
      "Startup Founder",
      "University",
      "Industry Partner",
      "Admin",
    ].includes(role);

  const canAccessFunding =
    [
      "Researcher",
      "Investor",
      "Startup Founder",
      "University",
      "Funding Agency",
      "Admin",
    ].includes(role);

  const isAdmin =
    role === "Admin";

  return (
    <div className="min-h-screen bg-[#06111f] text-white">

      {/* =====================================================
          SIDEBAR
      ===================================================== */}

      <Sidebar />

      {/* =====================================================
          MAIN CONTENT
      ===================================================== */}

      <main className="ml-72 min-h-screen">

        {/* ===================================================
            NAVBAR
        =================================================== */}

        <header className="border-b border-slate-800 bg-[#071321]">

          <div className="mx-auto flex max-w-7xl items-center justify-between px-8 py-5">

            <button
              onClick={() =>
                router.push("/")
              }
              className="text-3xl font-bold"
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

            <button
              onClick={handleLogout}
              className="rounded-lg border border-slate-600 px-5 py-2 text-sm font-semibold transition hover:border-red-400 hover:text-red-400"
            >
              Logout
            </button>

          </div>

        </header>

        {/* ===================================================
            MAIN SECTION
        =================================================== */}

        <section className="mx-auto max-w-7xl px-8 py-12">

          {/* =================================================
              HEADING
          ================================================= */}

          <div className="mb-10">

            <p className="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-400">
              InnoBridge-AI
            </p>

            <h1 className="mt-3 text-5xl font-bold tracking-tight">
              Dashboard
            </h1>

            <p className="mt-3 text-lg text-slate-400">
              Welcome to your innovation intelligence workspace.
            </p>

          </div>

          {/* =================================================
              LOGGED IN USER
          ================================================= */}

          <div className="mb-8 rounded-2xl border border-slate-700 bg-[#0c1929] p-6">

            <p className="text-sm text-slate-500">
              Logged in as
            </p>

            <div className="mt-2 flex items-center gap-3">

              <h2 className="text-2xl font-bold text-cyan-400">
                {role}
              </h2>

              <span className="rounded-full border border-green-500/40 bg-green-500/10 px-3 py-1 text-xs font-semibold text-green-400">
                Verified
              </span>

            </div>

          </div>

          {/* =================================================
              ROLE OVERVIEW
          ================================================= */}

          <RoleOverview
            role={role}
            dashboard={dashboard}
          />

          {/* =================================================
              INNOVATION INTELLIGENCE
          ================================================= */}

          <div className="mt-14">

            <h2 className="text-2xl font-bold">
              Innovation Intelligence
            </h2>

            <p className="mt-2 text-slate-400">
              Access the capabilities available for your role.
            </p>

            <div className="mt-6 grid gap-6 md:grid-cols-3">

              {/* =============================================
                  RESEARCH INTELLIGENCE
              ============================================= */}

              {canAccessResearch && (
                <button
                  onClick={() =>
                    router.push(
                      "/research-intelligence"
                    )
                  }
                  className="rounded-2xl border border-slate-700 bg-[#0c1929] p-7 text-left transition hover:border-cyan-400/60"
                >

                  <div className="text-3xl">
                    🔬
                  </div>

                  <h3 className="mt-4 text-xl font-bold">
                    Research Intelligence
                  </h3>

                  <p className="mt-3 text-sm text-slate-400">
                    Discover and analyze research,
                    authors and institutions.
                  </p>

                </button>
              )}

              {/* =============================================
                  PATENT INTELLIGENCE
              ============================================= */}

              {canAccessPatent && (
                <button
                  onClick={() =>
                    router.push(
                      "/patent-intelligence"
                    )
                  }
                  className="rounded-2xl border border-slate-700 bg-[#0c1929] p-7 text-left transition hover:border-indigo-400/60"
                >

                  <div className="text-3xl">
                    📜
                  </div>

                  <h3 className="mt-4 text-xl font-bold">
                    Patent Intelligence
                  </h3>

                  <p className="mt-3 text-sm text-slate-400">
                    Search, compare and analyze patents.
                  </p>

                </button>
              )}

              {/* =============================================
                  FUNDING INTELLIGENCE
              ============================================= */}

              {canAccessFunding && (
                <button
                  onClick={() =>
                    router.push(
                      "/funding-intelligence"
                    )
                  }
                  className="rounded-2xl border border-slate-700 bg-[#0c1929] p-7 text-left transition hover:border-purple-400/60"
                >

                  <div className="text-3xl">
                    💰
                  </div>

                  <h3 className="mt-4 text-xl font-bold">
                    Funding Intelligence
                  </h3>

                  <p className="mt-3 text-sm text-slate-400">
                    Discover funding opportunities
                    and grants.
                  </p>

                </button>
              )}

            </div>

          </div>

          {/* =================================================
              ADMIN MANAGEMENT
          ================================================= */}

          {isAdmin && (
            <div className="mt-14">

              <h2 className="text-2xl font-bold">
                Administration
              </h2>

              <p className="mt-2 text-slate-400">
                Manage users and platform operations.
              </p>

              <div className="mt-6 grid gap-6 md:grid-cols-2">

                {/* ===========================================
                    USER MANAGEMENT
                =========================================== */}

                <button
                  onClick={() =>
                    router.push(
                      "/admin/users"
                    )
                  }
                  className="rounded-2xl border border-red-500/30 bg-[#0c1929] p-7 text-left transition hover:border-red-400"
                >

                  <div className="text-3xl">
                    👥
                  </div>

                  <h3 className="mt-4 text-xl font-bold">
                    User Management
                  </h3>

                  <p className="mt-3 text-sm text-slate-400">
                    View, verify and manage platform users.
                  </p>

                  <p className="mt-4 text-xs font-semibold text-red-400">
                    Manage Users →
                  </p>

                </button>

                {/* ===========================================
                    PLATFORM ANALYTICS
                =========================================== */}

                <button
                  onClick={() =>
                    router.push(
                      "/admin/analytics"
                    )
                  }
                  className="rounded-2xl border border-slate-700 bg-[#0c1929] p-7 text-left transition hover:border-cyan-400/60"
                >

                  <div className="text-3xl">
                    📊
                  </div>

                  <h3 className="mt-4 text-xl font-bold">
                    Platform Analytics
                  </h3>

                  <p className="mt-3 text-sm text-slate-400">
                    Monitor users, projects and platform activity.
                  </p>

                  <p className="mt-4 text-xs font-semibold text-cyan-400">
                    View Analytics →
                  </p>

                </button>

              </div>

            </div>
          )}

        </section>

      </main>

    </div>
  );
}


/* ============================================================
   ROLE OVERVIEW COMPONENT
============================================================ */

function RoleOverview({
  role,
  dashboard,
}: {
  role: string;
  dashboard: any;
}) {

  /* ==========================================================
     RESEARCHER
  ========================================================== */

  if (role === "Researcher") {
    return (
      <div>

        <div className="mb-6">

          <h2 className="text-2xl font-bold">
            Researcher Overview
          </h2>

          <p className="mt-2 text-slate-400">
            Manage your research and discover new opportunities.
          </p>

        </div>

        <div className="grid gap-6 md:grid-cols-3">

          <StatCard
            title="My Projects"
            value={
              dashboard.my_projects ?? 0
            }
            description="Research projects created by you"
            color="cyan"
          />

          <StatCard
            title="Available Grants"
            value={
              dashboard.available_grants ??
              "Coming Soon"
            }
            description="Funding opportunities for researchers"
            color="indigo"
          />

          <StatCard
            title="Research Trends"
            value={
              dashboard.research_trends ??
              "Coming Soon"
            }
            description="Explore current research trends"
            color="purple"
          />

        </div>

      </div>
    );
  }


  /* ==========================================================
     INVESTOR
  ========================================================== */

  if (role === "Investor") {
    return (
      <div>

        <div className="mb-6">

          <h2 className="text-2xl font-bold">
            Investor Overview
          </h2>

          <p className="mt-2 text-slate-400">
            Discover promising innovations, startups and investment opportunities.
          </p>

        </div>

        <div className="grid gap-6 md:grid-cols-3">

          <StatCard
            title="Investment Opportunities"
            value={
              dashboard.investment_opportunities ??
              "Coming Soon"
            }
            description="Potential opportunities to explore"
            color="cyan"
          />

          <StatCard
            title="Startups"
            value={
              dashboard.startups ??
              "Coming Soon"
            }
            description="Innovative startups"
            color="indigo"
          />

          <StatCard
            title="Market Trends"
            value={
              dashboard.market_trends ??
              "Coming Soon"
            }
            description="Emerging innovation trends"
            color="purple"
          />

        </div>

      </div>
    );
  }


  /* ==========================================================
     STARTUP FOUNDER
  ========================================================== */

  if (role === "Startup Founder") {
    return (
      <div>

        <div className="mb-6">

          <h2 className="text-2xl font-bold">
            Startup Founder Overview
          </h2>

          <p className="mt-2 text-slate-400">
            Discover funding, patents and opportunities for your startup.
          </p>

        </div>

        <div className="grid gap-6 md:grid-cols-3">

          <StatCard
            title="My Projects"
            value={
              dashboard.my_projects ?? 0
            }
            description="Innovation projects"
            color="cyan"
          />

          <StatCard
            title="Funding Opportunities"
            value={
              dashboard.funding_opportunities ??
              "Coming Soon"
            }
            description="Funding programs for startups"
            color="indigo"
          />

          <StatCard
            title="Patent Opportunities"
            value={
              dashboard.patent_opportunities ??
              "Coming Soon"
            }
            description="Patent opportunities to explore"
            color="purple"
          />

        </div>

      </div>
    );
  }


  /* ==========================================================
     UNIVERSITY
  ========================================================== */

  if (role === "University") {
    return (
      <div>

        <div className="mb-6">

          <h2 className="text-2xl font-bold">
            University Overview
          </h2>

          <p className="mt-2 text-slate-400">
            Connect research, innovation, patents and funding opportunities.
          </p>

        </div>

        <div className="grid gap-6 md:grid-cols-3">

          <StatCard
            title="Research Projects"
            value={
              dashboard.research_projects ??
              "Coming Soon"
            }
            description="University research projects"
            color="cyan"
          />

          <StatCard
            title="Patents"
            value={
              dashboard.patents ??
              "Coming Soon"
            }
            description="University patent portfolio"
            color="indigo"
          />

          <StatCard
            title="Funding"
            value={
              dashboard.funding ??
              "Coming Soon"
            }
            description="Available funding opportunities"
            color="purple"
          />

        </div>

      </div>
    );
  }


  /* ==========================================================
     FUNDING AGENCY
  ========================================================== */

  if (role === "Funding Agency") {
    return (
      <div>

        <div className="mb-6">

          <h2 className="text-2xl font-bold">
            Funding Agency Overview
          </h2>

          <p className="mt-2 text-slate-400">
            Discover research projects and manage funding opportunities.
          </p>

        </div>

        <div className="grid gap-6 md:grid-cols-3">

          <StatCard
            title="Funding Programs"
            value={
              dashboard.funding_programs ??
              "Coming Soon"
            }
            description="Available funding programs"
            color="cyan"
          />

          <StatCard
            title="Research Projects"
            value={
              dashboard.research_projects ??
              "Coming Soon"
            }
            description="Projects seeking funding"
            color="indigo"
          />

          <StatCard
            title="Applications"
            value={
              dashboard.applications ??
              "Coming Soon"
            }
            description="Funding applications"
            color="purple"
          />

        </div>

      </div>
    );
  }


  /* ==========================================================
     INDUSTRY PARTNER
  ========================================================== */

  if (role === "Industry Partner") {
    return (
      <div>

        <div className="mb-6">

          <h2 className="text-2xl font-bold">
            Industry Partner Overview
          </h2>

          <p className="mt-2 text-slate-400">
            Discover technologies, research and patents for industry collaboration.
          </p>

        </div>

        <div className="grid gap-6 md:grid-cols-3">

          <StatCard
            title="Technologies"
            value={
              dashboard.technologies ??
              "Coming Soon"
            }
            description="Technologies available for collaboration"
            color="cyan"
          />

          <StatCard
            title="Patents"
            value={
              dashboard.patents ??
              "Coming Soon"
            }
            description="Relevant patent opportunities"
            color="indigo"
          />

          <StatCard
            title="Collaborations"
            value={
              dashboard.collaborations ??
              "Coming Soon"
            }
            description="Potential industry collaborations"
            color="purple"
          />

        </div>

      </div>
    );
  }


  /* ==========================================================
     ADMIN
  ========================================================== */

  if (role === "Admin") {
    return (
      <div>

        <div className="mb-6">

          <h2 className="text-2xl font-bold">
            Administration Overview
          </h2>

          <p className="mt-2 text-slate-400">
            Monitor users and platform activity.
          </p>

        </div>

        <div className="grid gap-6 md:grid-cols-2">

          <StatCard
            title="Total Users"
            value={
              dashboard.total_users ?? 0
            }
            description="Registered users on the platform"
            color="cyan"
          />

          <StatCard
            title="Total Projects"
            value={
              dashboard.total_projects ?? 0
            }
            description="Research and innovation projects"
            color="indigo"
          />

        </div>

      </div>
    );
  }


  /* ==========================================================
     FALLBACK
  ========================================================== */

  return (
    <div className="rounded-2xl border border-slate-700 bg-[#0c1929] p-7">

      <h2 className="text-2xl font-bold">
        Welcome to InnoBridge-AI
      </h2>

      <p className="mt-3 text-slate-400">
        Your role is {role}.
      </p>

    </div>
  );
}


/* ============================================================
   STAT CARD
============================================================ */

function StatCard({
  title,
  value,
  description,
  color,
}: {
  title: string;
  value: string | number;
  description: string;
  color: "cyan" | "indigo" | "purple";
}) {

  const colorClass = {
    cyan: "text-cyan-400",
    indigo: "text-indigo-400",
    purple: "text-purple-400",
  }[color];

  const borderClass = {
    cyan: "hover:border-cyan-400/50",
    indigo: "hover:border-indigo-400/50",
    purple: "hover:border-purple-400/50",
  }[color];

  return (
    <div
      className={`rounded-2xl border border-slate-700 bg-[#0c1929] p-7 transition ${borderClass}`}
    >

      <p className="text-sm text-slate-400">
        {title}
      </p>

      <p
        className={`mt-4 text-3xl font-bold ${colorClass}`}
      >
        {value}
      </p>

      <p className="mt-3 text-sm text-slate-500">
        {description}
      </p>

    </div>
  );
}