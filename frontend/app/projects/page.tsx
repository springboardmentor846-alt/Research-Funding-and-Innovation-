"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { apiRequest } from "@/lib/api";

type Portfolio = {
  id: number;
  user_id?: number;
  title: string;
  category: string;
  description?: string | null;
  status?: string;
  visibility?: string;
};

type ProjectDetail = {
  id: number;
  portfolio_id: number;
  github_url: string | null;
  demo_url: string | null;
  technology_stack: string | null;
  team_size: number | null;
  project_duration: string | null;
};

export default function ProjectDetailsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  /*
   * =====================================================
   * PORTFOLIO ID
   * =====================================================
   *
   * When coming from Innovation Details:
   *
   * /projects?portfolioId=5
   *
   * portfolioId will automatically be 5.
   */

  const urlPortfolioId =
    searchParams.get("portfolioId");

  const [selectedPortfolioId, setSelectedPortfolioId] =
    useState<string>(urlPortfolioId || "");

  /*
   * =====================================================
   * STATE
   * =====================================================
   */

  const [portfolios, setPortfolios] =
    useState<Portfolio[]>([]);

  const [project, setProject] =
    useState<ProjectDetail | null>(null);

  const [githubUrl, setGithubUrl] =
    useState("");

  const [demoUrl, setDemoUrl] =
    useState("");

  const [technologyStack, setTechnologyStack] =
    useState("");

  const [teamSize, setTeamSize] =
    useState("");

  const [projectDuration, setProjectDuration] =
    useState("");

  const [message, setMessage] =
    useState("");

  const [error, setError] =
    useState("");

  const [loadingPortfolios, setLoadingPortfolios] =
    useState(true);

  const [loadingProject, setLoadingProject] =
    useState(false);

  const [creating, setCreating] =
    useState(false);

  const [updating, setUpdating] =
    useState(false);

  const [deleting, setDeleting] =
    useState(false);

  /*
   * =====================================================
   * LOAD PORTFOLIOS
   * =====================================================
   *
   * This is required when the user opens
   * Project Details directly from the sidebar.
   */

  useEffect(() => {
    async function loadPortfolios() {
      try {
        setLoadingPortfolios(true);
        setError("");

        /*
         * Get the user's portfolios.
         *
         * If your backend uses a different endpoint for
         * listing portfolios, only this URL needs to change.
         */

        const data = await apiRequest(
          "/portfolio/my"
        );

        const list = Array.isArray(data)
          ? data
          : data?.portfolios || [];

        setPortfolios(list);

      } catch (err: any) {
        console.error(
          "Failed to load portfolios:",
          err
        );

        setError(
          err?.message ||
            "Failed to load portfolios."
        );
      } finally {
        setLoadingPortfolios(false);
      }
    }

    loadPortfolios();
  }, []);

  /*
   * =====================================================
   * KEEP URL PORTFOLIO ID IN SYNC
   * =====================================================
   */

  useEffect(() => {
    if (urlPortfolioId) {
      setSelectedPortfolioId(
        urlPortfolioId
      );
    }
  }, [urlPortfolioId]);

  /*
   * =====================================================
   * LOAD PROJECT DETAILS
   * =====================================================
   */

  useEffect(() => {
    if (!selectedPortfolioId) {
      setProject(null);

      setGithubUrl("");
      setDemoUrl("");
      setTechnologyStack("");
      setTeamSize("");
      setProjectDuration("");

      return;
    }

    loadProject(
      selectedPortfolioId
    );
  }, [selectedPortfolioId]);

  async function loadProject(
    portfolioId: string
  ) {
    try {
      setLoadingProject(true);
      setError("");
      setMessage("");

      const data = await apiRequest(
        `/project-details/${portfolioId}`
      );

      /*
       * Project already exists.
       */

      setProject(data);

      setGithubUrl(
        data.github_url || ""
      );

      setDemoUrl(
        data.demo_url || ""
      );

      setTechnologyStack(
        data.technology_stack || ""
      );

      setTeamSize(
        data.team_size !== null &&
        data.team_size !== undefined
          ? String(data.team_size)
          : ""
      );

      setProjectDuration(
        data.project_duration || ""
      );

      setMessage(
        "Project details loaded successfully."
      );

    } catch (err: any) {

      /*
       * 404 means:
       *
       * Portfolio exists,
       * but Project Details have not
       * been created yet.
       */

      if (
        err?.message ===
        "Project details not found."
      ) {
        setProject(null);

        setGithubUrl("");
        setDemoUrl("");
        setTechnologyStack("");
        setTeamSize("");
        setProjectDuration("");

        setMessage(
          "No project details found. You can create them below."
        );

      } else {

        setError(
          err?.message ||
            "Failed to load project details."
        );
      }

    } finally {
      setLoadingProject(false);
    }
  }

  /*
   * =====================================================
   * SELECT PORTFOLIO
   * =====================================================
   */

  function handlePortfolioChange(
    value: string
  ) {
    setSelectedPortfolioId(value);

    setError("");
    setMessage("");

    /*
     * Put portfolio ID in URL.
     *
     * Example:
     *
     * /projects?portfolioId=5
     */

    if (value) {
      router.push(
        `/projects?portfolioId=${value}`
      );
    } else {
      router.push("/projects");
    }
  }

  /*
   * =====================================================
   * CREATE PROJECT DETAILS
   * =====================================================
   */

  async function createProject() {

    if (!selectedPortfolioId) {
      setError(
        "Please select a portfolio first."
      );

      return;
    }

    setCreating(true);
    setError("");
    setMessage("");

    const requestBody = {
      github_url:
        githubUrl.trim() || null,

      demo_url:
        demoUrl.trim() || null,

      technology_stack:
        technologyStack.trim() || null,

      team_size:
        teamSize.trim() !== ""
          ? Number(teamSize)
          : null,

      project_duration:
        projectDuration.trim() || null,
    };

    try {

      const data = await apiRequest(
        `/project-details/${selectedPortfolioId}`,
        {
          method: "POST",
          body: JSON.stringify(
            requestBody
          ),
        }
      );

      setProject(data);

      setGithubUrl(
        data.github_url || ""
      );

      setDemoUrl(
        data.demo_url || ""
      );

      setTechnologyStack(
        data.technology_stack || ""
      );

      setTeamSize(
        data.team_size !== null &&
        data.team_size !== undefined
          ? String(data.team_size)
          : ""
      );

      setProjectDuration(
        data.project_duration || ""
      );

      setMessage(
        "Project details created successfully."
      );

    } catch (err: any) {

      setError(
        err?.message ||
          "Failed to create project details."
      );

    } finally {
      setCreating(false);
    }
  }

  /*
   * =====================================================
   * UPDATE PROJECT DETAILS
   * =====================================================
   */

  async function updateProject() {

    if (!selectedPortfolioId) {
      setError(
        "Please select a portfolio first."
      );

      return;
    }

    if (!project) {
      setError(
        "Project details do not exist yet."
      );

      return;
    }

    setUpdating(true);
    setError("");
    setMessage("");

    const requestBody = {
      github_url:
        githubUrl.trim() || null,

      demo_url:
        demoUrl.trim() || null,

      technology_stack:
        technologyStack.trim() || null,

      team_size:
        teamSize.trim() !== ""
          ? Number(teamSize)
          : null,

      project_duration:
        projectDuration.trim() || null,
    };

    try {

      const data = await apiRequest(
        `/project-details/${selectedPortfolioId}`,
        {
          method: "PUT",
          body: JSON.stringify(
            requestBody
          ),
        }
      );

      setProject(data);

      setMessage(
        "Project details updated successfully."
      );

    } catch (err: any) {

      setError(
        err?.message ||
          "Failed to update project details."
      );

    } finally {
      setUpdating(false);
    }
  }

  /*
   * =====================================================
   * DELETE PROJECT DETAILS
   * =====================================================
   */

  async function deleteProject() {

    if (!selectedPortfolioId) {
      setError(
        "Please select a portfolio first."
      );

      return;
    }

    if (!project) {
      setError(
        "No project details exist."
      );

      return;
    }

    const confirmed =
      window.confirm(
        "Are you sure you want to delete these project details?"
      );

    if (!confirmed) {
      return;
    }

    setDeleting(true);
    setError("");
    setMessage("");

    try {

      await apiRequest(
        `/project-details/${selectedPortfolioId}`,
        {
          method: "DELETE",
        }
      );

      setProject(null);

      setGithubUrl("");
      setDemoUrl("");
      setTechnologyStack("");
      setTeamSize("");
      setProjectDuration("");

      setMessage(
        "Project details deleted successfully. You can create them again."
      );

    } catch (err: any) {

      setError(
        err?.message ||
          "Failed to delete project details."
      );

    } finally {
      setDeleting(false);
    }
  }

  /*
   * =====================================================
   * LOADING SCREEN
   * =====================================================
   */

  if (loadingPortfolios) {
    return (
      <div className="min-h-screen bg-[#06111f] text-white">

        <main className="mx-auto max-w-5xl px-8 py-20">

          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-400">
            InnoBridge-AI
          </p>

          <h1 className="mt-3 text-5xl font-bold">
            Project Details
          </h1>

          <p className="mt-5 text-lg text-slate-400">
            Loading portfolios...
          </p>

        </main>

      </div>
    );
  }

  /*
   * =====================================================
   * MAIN PAGE
   * =====================================================
   */

  return (
    <div className="min-h-screen bg-[#06111f] text-white">

      <main className="mx-auto max-w-5xl px-8 py-12">

        {/* HEADER */}

        <div className="mb-10">

          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-400">
            InnoBridge-AI
          </p>

          <h1 className="mt-3 text-5xl font-bold">
            Project Details
          </h1>

          <p className="mt-3 text-lg text-slate-400">
            Manage the technical details of your project.
          </p>

        </div>

        {/* =================================================
            PORTFOLIO SELECTOR
        ================================================= */}

        <div className="mb-6 rounded-2xl border border-cyan-400/30 bg-[#0b1a2b] p-6">

          <p className="text-sm text-slate-500">
            Innovation Portfolio
          </p>

          <h2 className="mt-2 text-xl font-semibold text-cyan-400">
            Select Portfolio
          </h2>

          <p className="mt-2 text-sm text-slate-400">
            Choose a portfolio to manage its
            project details.
          </p>

          <select
            value={selectedPortfolioId}
            onChange={(e) =>
              handlePortfolioChange(
                e.target.value
              )
            }
            className="mt-5 w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
          >

            <option value="">
              -- Select a Portfolio --
            </option>

            {portfolios.map(
              (portfolio) => (
                <option
                  key={portfolio.id}
                  value={portfolio.id}
                >
                  #{portfolio.id} -{" "}
                  {portfolio.title}
                </option>
              )
            )}

          </select>

          {selectedPortfolioId && (
            <p className="mt-3 text-sm text-slate-400">

              Portfolio ID:

              <span className="ml-2 font-semibold text-cyan-400">
                {selectedPortfolioId}
              </span>

            </p>
          )}

        </div>

        {/* SUCCESS MESSAGE */}

        {message && (
          <div className="mb-6 rounded-lg border border-green-500/40 bg-green-500/10 p-4 text-green-400">
            {message}
          </div>
        )}

        {/* ERROR MESSAGE */}

        {error && (
          <div className="mb-6 rounded-lg border border-red-500/40 bg-red-500/10 p-4 text-red-400">
            {error}
          </div>
        )}

        {/* =================================================
            NO PORTFOLIO SELECTED
        ================================================= */}

        {!selectedPortfolioId && (

          <div className="rounded-2xl border border-slate-700 bg-[#0b1a2b] p-10 text-center">

            <div className="text-5xl">
              📋
            </div>

            <h2 className="mt-5 text-2xl font-bold">
              Select a Portfolio
            </h2>

            <p className="mt-3 text-slate-400">
              Select a portfolio above to create,
              view, update, or delete its
              project details.
            </p>

          </div>

        )}

        {/* =================================================
            LOADING PROJECT
        ================================================= */}

        {selectedPortfolioId &&
          loadingProject && (

            <div className="rounded-2xl border border-slate-700 bg-[#0b1a2b] p-10 text-center">

              <p className="text-lg text-slate-400">
                Loading project details...
              </p>

            </div>

          )}

        {/* =================================================
            PROJECT FORM
        ================================================= */}

        {selectedPortfolioId &&
          !loadingProject && (

            <div className="rounded-2xl border border-slate-700 bg-[#0b1a2b] p-8">

              <h2 className="mb-8 text-2xl font-bold">
                Project Information
              </h2>

              {/* GITHUB */}

              <div className="mb-6">

                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  GitHub URL
                </label>

                <input
                  type="url"
                  value={githubUrl}
                  onChange={(e) =>
                    setGithubUrl(
                      e.target.value
                    )
                  }
                  placeholder="https://github.com/username/project"
                  className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

              </div>

              {/* DEMO */}

              <div className="mb-6">

                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Demo URL
                </label>

                <input
                  type="url"
                  value={demoUrl}
                  onChange={(e) =>
                    setDemoUrl(
                      e.target.value
                    )
                  }
                  placeholder="https://your-demo.com"
                  className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

              </div>

              {/* TECHNOLOGY STACK */}

              <div className="mb-6">

                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Technology Stack
                </label>

                <textarea
                  value={technologyStack}
                  onChange={(e) =>
                    setTechnologyStack(
                      e.target.value
                    )
                  }
                  placeholder="React, Next.js, FastAPI, Python, PostgreSQL..."
                  rows={4}
                  className="w-full resize-none rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

              </div>

              {/* TEAM SIZE */}

              <div className="mb-6">

                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Team Size
                </label>

                <input
                  type="number"
                  min="1"
                  value={teamSize}
                  onChange={(e) =>
                    setTeamSize(
                      e.target.value
                    )
                  }
                  placeholder="Example: 4"
                  className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

              </div>

              {/* PROJECT DURATION */}

              <div className="mb-8">

                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Project Duration
                </label>

                <input
                  type="text"
                  value={projectDuration}
                  onChange={(e) =>
                    setProjectDuration(
                      e.target.value
                    )
                  }
                  placeholder="Example: 6 months"
                  className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

              </div>

              {/* =================================================
                  BUTTONS
              ================================================= */}

              <div className="flex flex-wrap gap-4">

                {/* CREATE */}

                {!project && (

                  <button
                    type="button"
                    onClick={createProject}
                    disabled={
                      creating ||
                      updating ||
                      deleting
                    }
                    className="rounded-lg bg-cyan-500 px-6 py-3 font-semibold text-black hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {creating
                      ? "Creating..."
                      : "+ Create"}
                  </button>

                )}

                {/* UPDATE */}

                {project && (

                  <button
                    type="button"
                    onClick={updateProject}
                    disabled={
                      creating ||
                      updating ||
                      deleting
                    }
                    className="rounded-lg border border-indigo-400 px-6 py-3 font-semibold text-indigo-400 hover:bg-indigo-400 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {updating
                      ? "Updating..."
                      : "Update"}
                  </button>

                )}

                {/* DELETE */}

                {project && (

                  <button
                    type="button"
                    onClick={deleteProject}
                    disabled={
                      creating ||
                      updating ||
                      deleting
                    }
                    className="rounded-lg border border-red-400 px-6 py-3 font-semibold text-red-400 hover:bg-red-400 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {deleting
                      ? "Deleting..."
                      : "Delete"}
                  </button>

                )}

              </div>

            </div>

          )}

        {/* =================================================
            CURRENT PROJECT DETAILS
        ================================================= */}

        {project && (

          <div className="mt-8 rounded-2xl border border-slate-700 bg-[#0b1a2b] p-8">

            <h2 className="mb-6 text-2xl font-bold">
              Current Project Details
            </h2>

            <div className="space-y-5">

              <Detail
                label="Project ID"
                value={String(project.id)}
              />

              <Detail
                label="Portfolio ID"
                value={String(
                  project.portfolio_id
                )}
              />

              <Detail
                label="GitHub URL"
                value={
                  project.github_url
                }
              />

              <Detail
                label="Demo URL"
                value={
                  project.demo_url
                }
              />

              <Detail
                label="Technology Stack"
                value={
                  project.technology_stack
                }
              />

              <Detail
                label="Team Size"
                value={
                  project.team_size !== null &&
                  project.team_size !== undefined
                    ? String(
                        project.team_size
                      )
                    : null
                }
              />

              <Detail
                label="Project Duration"
                value={
                  project.project_duration
                }
              />

            </div>

          </div>

        )}

      </main>

    </div>
  );
}


/*
 * =====================================================
 * DETAIL COMPONENT
 * =====================================================
 */

function Detail({
  label,
  value,
}: {
  label: string;
  value: string | null;
}) {

  return (

    <div className="border-b border-slate-700 pb-4">

      <p className="text-sm text-slate-500">
        {label}
      </p>

      <p className="mt-1 break-all text-white">
        {value || "Not provided"}
      </p>

    </div>

  );
}