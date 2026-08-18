"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import { apiRequest } from "@/lib/api";

type Portfolio = {
  id: number;
  user_id: number;
  title: string;
  category: string;
  description?: string | null;
  status: string;
  visibility: string;
  github_url?: string | null;
  paper_url?: string | null;
  prototype_link?: string | null;
};

export default function InnovationDetailsPage() {
  const params = useParams();
  const router = useRouter();

  const [portfolio, setPortfolio] =
    useState<Portfolio | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  useEffect(() => {
    async function loadPortfolio() {
      try {
        const id = params.id;

        if (!id) {
          throw new Error(
            "Portfolio ID not found"
          );
        }

        const data = await apiRequest(
          `/portfolio/${id}`
        );

        setPortfolio(data);
      } catch (err: any) {
        console.error(
          "Portfolio details error:",
          err
        );

        setError(
          err?.message ||
            "Failed to load portfolio"
        );
      } finally {
        setLoading(false);
      }
    }

    loadPortfolio();
  }, [params.id]);

  /*
   * =====================================================
   * LOADING
   * =====================================================
   */

  if (loading) {
    return (
      <div className="min-h-screen bg-[#06111f] text-white">
        <Sidebar />

        <main className="min-h-screen ml-72 p-10">
          <p className="text-slate-400">
            Loading innovation details...
          </p>
        </main>
      </div>
    );
  }

  /*
   * =====================================================
   * ERROR
   * =====================================================
   */

  if (error || !portfolio) {
    return (
      <div className="min-h-screen bg-[#06111f] text-white">
        <Sidebar />

        <main className="min-h-screen ml-72 p-10">

          <button
            onClick={() =>
              router.push(
                "/innovation-portfolio"
              )
            }
            className="mb-8 rounded-lg border border-slate-600 px-5 py-2 hover:border-cyan-400 hover:text-cyan-400"
          >
            ← Back to Portfolio
          </button>

          <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-6 text-red-400">
            {error ||
              "Portfolio not found"}
          </div>

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

      <Sidebar />

      <main className="min-h-screen ml-72">

        {/* =================================================
            NAVBAR
        ================================================= */}

        <header className="border-b border-slate-800 bg-[#071321]">

          <div className="flex items-center justify-between px-10 py-5">

            <button
              onClick={() =>
                router.push(
                  "/innovation-portfolio"
                )
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

            <button
              onClick={() =>
                router.push(
                  "/innovation-portfolio"
                )
              }
              className="rounded-lg border border-slate-600 px-5 py-2 text-sm hover:border-cyan-400 hover:text-cyan-400"
            >
              ← Back
            </button>

          </div>

        </header>

        {/* =================================================
            MAIN CONTENT
        ================================================= */}

        <section className="mx-auto max-w-6xl px-10 py-12">

          {/* =================================================
              HEADER
          ================================================= */}

          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-400">
            InnoBridge-AI
          </p>

          <h1 className="mt-3 text-5xl font-bold">
            Innovation Details
          </h1>

          <p className="mt-3 text-lg text-slate-400">
            View your complete innovation information.
          </p>

          {/* =================================================
              INNOVATION CARD
          ================================================= */}

          <div className="mt-10 rounded-2xl border border-slate-700 bg-[#0b1a2b] p-8">

            <div className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">

              <div>

                <span className="inline-block rounded-full border border-cyan-400/40 bg-cyan-400/10 px-4 py-1 text-sm text-cyan-400">
                  {portfolio.category}
                </span>

                <h2 className="mt-5 text-4xl font-bold">
                  {portfolio.title}
                </h2>

                <p className="mt-4 text-lg text-slate-400">
                  {portfolio.description ||
                    "No description provided."}
                </p>

              </div>

              <span className="rounded-full border border-slate-600 px-4 py-2 text-sm text-slate-300">
                {portfolio.visibility}
              </span>

            </div>

            <div className="my-8 border-t border-slate-700" />

            {/* =================================================
                BASIC INFORMATION
            ================================================= */}

            <h3 className="text-2xl font-bold">
              Basic Information
            </h3>

            <div className="mt-6 grid gap-5 md:grid-cols-2">

              <div className="rounded-xl border border-slate-700 bg-[#081625] p-5">

                <p className="text-sm text-slate-500">
                  Category
                </p>

                <p className="mt-2 text-lg font-semibold text-cyan-400">
                  {portfolio.category}
                </p>

              </div>

              <div className="rounded-xl border border-slate-700 bg-[#081625] p-5">

                <p className="text-sm text-slate-500">
                  Status
                </p>

                <p className="mt-2 text-lg font-semibold">
                  {portfolio.status}
                </p>

              </div>

              <div className="rounded-xl border border-slate-700 bg-[#081625] p-5">

                <p className="text-sm text-slate-500">
                  Visibility
                </p>

                <p className="mt-2 text-lg font-semibold">
                  {portfolio.visibility}
                </p>

              </div>

              <div className="rounded-xl border border-slate-700 bg-[#081625] p-5">

                <p className="text-sm text-slate-500">
                  Portfolio ID
                </p>

                <p className="mt-2 text-lg font-semibold">
                  #{portfolio.id}
                </p>

              </div>

            </div>

            {/* =================================================
                RELATED LINKS
            ================================================= */}

            <div className="my-8 border-t border-slate-700" />

            <h3 className="text-2xl font-bold">
              Related Links
            </h3>

            <div className="mt-6 grid gap-4 md:grid-cols-3">

              {/* GITHUB */}

              {portfolio.github_url ? (
                <a
                  href={portfolio.github_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="rounded-xl border border-slate-700 bg-[#081625] p-5 hover:border-cyan-400"
                >

                  <p className="font-semibold text-cyan-400">
                    GitHub
                  </p>

                  <p className="mt-2 text-sm text-slate-400">
                    Open GitHub repository →
                  </p>

                </a>
              ) : (
                <div className="rounded-xl border border-slate-700 bg-[#081625] p-5">

                  <p className="font-semibold">
                    GitHub
                  </p>

                  <p className="mt-2 text-sm text-slate-500">
                    No GitHub link added
                  </p>

                </div>
              )}

              {/* RESEARCH PAPER */}

              {portfolio.paper_url ? (
                <a
                  href={portfolio.paper_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="rounded-xl border border-slate-700 bg-[#081625] p-5 hover:border-cyan-400"
                >

                  <p className="font-semibold text-cyan-400">
                    Research Paper
                  </p>

                  <p className="mt-2 text-sm text-slate-400">
                    Open research paper →
                  </p>

                </a>
              ) : (
                <div className="rounded-xl border border-slate-700 bg-[#081625] p-5">

                  <p className="font-semibold">
                    Research Paper
                  </p>

                  <p className="mt-2 text-sm text-slate-500">
                    No paper link added
                  </p>

                </div>
              )}

              {/* PROTOTYPE */}

              {portfolio.prototype_link ? (
                <a
                  href={portfolio.prototype_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="rounded-xl border border-slate-700 bg-[#081625] p-5 hover:border-cyan-400"
                >

                  <p className="font-semibold text-cyan-400">
                    Prototype
                  </p>

                  <p className="mt-2 text-sm text-slate-400">
                    Open prototype →
                  </p>

                </a>
              ) : (
                <div className="rounded-xl border border-slate-700 bg-[#081625] p-5">

                  <p className="font-semibold">
                    Prototype
                  </p>

                  <p className="mt-2 text-sm text-slate-500">
                    No prototype link added
                  </p>

                </div>
              )}

            </div>

          </div>

          {/* =================================================
              RELATED MODULES
          ================================================= */}

          <div className="mt-10">

            <h2 className="text-2xl font-bold">
              Related Innovation Details
            </h2>

            <p className="mt-2 text-slate-400">
              Manage the detailed information
              associated with this innovation.
            </p>

            <div className="mt-6 grid gap-5 md:grid-cols-2">

              {/* =================================================
                  PROJECT DETAILS
              ================================================= */}

              <button
                type="button"
                onClick={() =>
                  router.push(
                    `/projects?portfolioId=${portfolio.id}`
                  )
                }
                className="rounded-xl border border-slate-700 bg-[#0b1a2b] p-6 text-left hover:border-cyan-400"
              >

                <h3 className="text-xl font-bold">
                  📋 Project Details
                </h3>

                <p className="mt-2 text-slate-400">
                  Manage detailed project information.
                </p>

              </button>

              {/* =================================================
                  RESEARCH PAPER DETAILS
              ================================================= */}

              <button
                type="button"
                onClick={() =>
                  router.push(
                    `/research-paper-details?portfolioId=${portfolio.id}`
                  )
                }
                className="rounded-xl border border-slate-700 bg-[#0b1a2b] p-6 text-left hover:border-cyan-400"
              >

                <h3 className="text-xl font-bold">
                  📄 Research Paper
                </h3>

                <p className="mt-2 text-slate-400">
                  Manage research paper information.
                </p>

              </button>

              {/* =================================================
                  PATENT DETAILS
              ================================================= */}

              <button
                type="button"
                onClick={() =>
                  router.push(
                    `/patents/details?portfolioId=${portfolio.id}`
                  )
                }
                className="rounded-xl border border-slate-700 bg-[#0b1a2b] p-6 text-left hover:border-cyan-400"
              >

                <h3 className="text-xl font-bold">
                  📜 Patent Details
                </h3>

                <p className="mt-2 text-slate-400">
                  Manage patent information.
                </p>

              </button>

              {/* =================================================
                  PROTOTYPE DETAILS
              ================================================= */}

              <button
                type="button"
                onClick={() =>
                  router.push(
                    `/prototypes/details?portfolioId=${portfolio.id}`
                  )
                }
                className="rounded-xl border border-slate-700 bg-[#0b1a2b] p-6 text-left hover:border-cyan-400"
              >

                <h3 className="text-xl font-bold">
                  🧪 Prototype Details
                </h3>

                <p className="mt-2 text-slate-400">
                  Manage prototype information.
                </p>

              </button>

            </div>

          </div>

        </section>

      </main>

    </div>
  );
}