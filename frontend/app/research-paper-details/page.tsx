"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { apiRequest } from "@/lib/api";

type Portfolio = {
  id: number;
  title: string;
  category: string;
};

type ResearchPaperDetail = {
  id: number;
  portfolio_id: number;
  paper_title: string;
  journal_name: string | null;
  publication_year: number | null;
  doi: string | null;
  paper_url: string | null;
  authors: string | null;
  abstract: string | null;
};

export default function ResearchPaperDetailsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  /*
   * If opened from Innovation Portfolio:
   *
   * /research-paper-details?portfolioId=5
   *
   * the portfolio ID is automatically received.
   */
  const urlPortfolioId =
    searchParams.get("portfolioId");

  const [portfolios, setPortfolios] =
    useState<Portfolio[]>([]);

  const [selectedPortfolioId, setSelectedPortfolioId] =
    useState<string>(urlPortfolioId || "");

  const [researchPaper, setResearchPaper] =
    useState<ResearchPaperDetail | null>(null);

  const [paperTitle, setPaperTitle] =
    useState("");

  const [journalName, setJournalName] =
    useState("");

  const [publicationYear, setPublicationYear] =
    useState("");

  const [doi, setDoi] =
    useState("");

  const [paperUrl, setPaperUrl] =
    useState("");

  const [authors, setAuthors] =
    useState("");

  const [abstractText, setAbstractText] =
    useState("");

  const [message, setMessage] =
    useState("");

  const [error, setError] =
    useState("");

  const [loadingPortfolios, setLoadingPortfolios] =
    useState(true);

  const [loadingPaper, setLoadingPaper] =
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
   */

  useEffect(() => {
    async function loadPortfolios() {
      try {
        setLoadingPortfolios(true);
        setError("");

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
   * AUTOMATIC PORTFOLIO ID
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
   * LOAD RESEARCH PAPER
   * =====================================================
   */

  useEffect(() => {
    if (!selectedPortfolioId) {
      clearPaperForm();
      setResearchPaper(null);
      return;
    }

    loadResearchPaper(
      selectedPortfolioId
    );
  }, [selectedPortfolioId]);

  async function loadResearchPaper(
    portfolioId: string
  ) {
    try {
      setLoadingPaper(true);
      setError("");
      setMessage("");

      const data = await apiRequest(
        `/research-paper-details/${portfolioId}`
      );

      setResearchPaper(data);

      setPaperTitle(
        data.paper_title || ""
      );

      setJournalName(
        data.journal_name || ""
      );

      setPublicationYear(
        data.publication_year !== null &&
        data.publication_year !== undefined
          ? String(data.publication_year)
          : ""
      );

      setDoi(
        data.doi || ""
      );

      setPaperUrl(
        data.paper_url || ""
      );

      setAuthors(
        data.authors || ""
      );

      setAbstractText(
        data.abstract || ""
      );

      setMessage(
        "Research paper details loaded successfully."
      );

    } catch (err: any) {

      /*
       * 404 means the portfolio does not
       * have research paper details yet.
       */

      if (
        err?.message ===
        "Research paper details not found."
      ) {

        setResearchPaper(null);

        clearPaperForm();

        setMessage(
          "No research paper details found. You can create them below."
        );

      } else {

        setError(
          err?.message ||
            "Failed to load research paper details."
        );
      }

    } finally {
      setLoadingPaper(false);
    }
  }

  /*
   * =====================================================
   * CLEAR FORM
   * =====================================================
   */

  function clearPaperForm() {
    setPaperTitle("");
    setJournalName("");
    setPublicationYear("");
    setDoi("");
    setPaperUrl("");
    setAuthors("");
    setAbstractText("");
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

    if (value) {
      router.push(
        `/research-paper-details?portfolioId=${value}`
      );
    } else {
      router.push(
        "/research-paper-details"
      );
    }
  }

  /*
   * =====================================================
   * CREATE
   * =====================================================
   */

  async function createResearchPaper() {
    if (!selectedPortfolioId) {
      setError(
        "Please select a portfolio first."
      );

      return;
    }

    if (!paperTitle.trim()) {
      setError(
        "Paper Title is required."
      );

      return;
    }

    setCreating(true);
    setError("");
    setMessage("");

    const requestBody = {
      paper_title:
        paperTitle.trim(),

      journal_name:
        journalName.trim() || null,

      publication_year:
        publicationYear.trim() !== ""
          ? Number(publicationYear)
          : null,

      doi:
        doi.trim() || null,

      paper_url:
        paperUrl.trim() || null,

      authors:
        authors.trim() || null,

      abstract:
        abstractText.trim() || null,
    };

    try {
      const data = await apiRequest(
        `/research-paper-details/${selectedPortfolioId}`,
        {
          method: "POST",
          body: JSON.stringify(
            requestBody
          ),
        }
      );

      setResearchPaper(data);

      setPaperTitle(
        data.paper_title || ""
      );

      setJournalName(
        data.journal_name || ""
      );

      setPublicationYear(
        data.publication_year !== null &&
        data.publication_year !== undefined
          ? String(data.publication_year)
          : ""
      );

      setDoi(
        data.doi || ""
      );

      setPaperUrl(
        data.paper_url || ""
      );

      setAuthors(
        data.authors || ""
      );

      setAbstractText(
        data.abstract || ""
      );

      setMessage(
        "Research paper details created successfully."
      );

    } catch (err: any) {

      setError(
        err?.message ||
          "Failed to create research paper details."
      );

    } finally {
      setCreating(false);
    }
  }

  /*
   * =====================================================
   * UPDATE
   * =====================================================
   */

  async function updateResearchPaper() {
    if (!selectedPortfolioId) {
      setError(
        "Please select a portfolio first."
      );

      return;
    }

    if (!researchPaper) {
      setError(
        "Research paper details do not exist yet."
      );

      return;
    }

    if (!paperTitle.trim()) {
      setError(
        "Paper Title is required."
      );

      return;
    }

    setUpdating(true);
    setError("");
    setMessage("");

    const requestBody = {
      paper_title:
        paperTitle.trim(),

      journal_name:
        journalName.trim() || null,

      publication_year:
        publicationYear.trim() !== ""
          ? Number(publicationYear)
          : null,

      doi:
        doi.trim() || null,

      paper_url:
        paperUrl.trim() || null,

      authors:
        authors.trim() || null,

      abstract:
        abstractText.trim() || null,
    };

    try {
      const data = await apiRequest(
        `/research-paper-details/${selectedPortfolioId}`,
        {
          method: "PUT",
          body: JSON.stringify(
            requestBody
          ),
        }
      );

      setResearchPaper(data);

      setMessage(
        "Research paper details updated successfully."
      );

    } catch (err: any) {

      setError(
        err?.message ||
          "Failed to update research paper details."
      );

    } finally {
      setUpdating(false);
    }
  }

  /*
   * =====================================================
   * DELETE
   * =====================================================
   */

  async function deleteResearchPaper() {
    if (!selectedPortfolioId) {
      setError(
        "Please select a portfolio first."
      );

      return;
    }

    if (!researchPaper) {
      setError(
        "No research paper details exist."
      );

      return;
    }

    const confirmed =
      window.confirm(
        "Are you sure you want to delete these research paper details?"
      );

    if (!confirmed) {
      return;
    }

    setDeleting(true);
    setError("");
    setMessage("");

    try {
      await apiRequest(
        `/research-paper-details/${selectedPortfolioId}`,
        {
          method: "DELETE",
        }
      );

      setResearchPaper(null);

      clearPaperForm();

      setMessage(
        "Research paper details deleted successfully. You can create them again."
      );

    } catch (err: any) {

      setError(
        err?.message ||
          "Failed to delete research paper details."
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
            Research Paper Details
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
            Research Paper Details
          </h1>

          <p className="mt-3 text-lg text-slate-400">
            Manage detailed information about your research paper.
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
            Choose the portfolio whose research paper
            details you want to manage.
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
            NO PORTFOLIO
        ================================================= */}

        {!selectedPortfolioId && (

          <div className="rounded-2xl border border-slate-700 bg-[#0b1a2b] p-10 text-center">

            <div className="text-5xl">
              📄
            </div>

            <h2 className="mt-5 text-2xl font-bold">
              Select a Portfolio
            </h2>

            <p className="mt-3 text-slate-400">
              Select a portfolio above to create,
              view, update, or delete its research
              paper details.
            </p>

          </div>

        )}

        {/* =================================================
            LOADING PAPER
        ================================================= */}

        {selectedPortfolioId &&
          loadingPaper && (

            <div className="rounded-2xl border border-slate-700 bg-[#0b1a2b] p-10 text-center">

              <p className="text-lg text-slate-400">
                Loading research paper details...
              </p>

            </div>

          )}

        {/* =================================================
            FORM
        ================================================= */}

        {selectedPortfolioId &&
          !loadingPaper && (

            <div className="rounded-2xl border border-slate-700 bg-[#0b1a2b] p-8">

              <h2 className="mb-8 text-2xl font-bold">
                Research Paper Information
              </h2>

              {/* PAPER TITLE */}

              <div className="mb-6">

                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Paper Title *
                </label>

                <input
                  type="text"
                  value={paperTitle}
                  onChange={(e) =>
                    setPaperTitle(
                      e.target.value
                    )
                  }
                  placeholder="Enter research paper title"
                  className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

              </div>

              {/* JOURNAL NAME */}

              <div className="mb-6">

                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Journal Name
                </label>

                <input
                  type="text"
                  value={journalName}
                  onChange={(e) =>
                    setJournalName(
                      e.target.value
                    )
                  }
                  placeholder="Enter journal name"
                  className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

              </div>

              {/* PUBLICATION YEAR */}

              <div className="mb-6">

                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Publication Year
                </label>

                <input
                  type="number"
                  value={publicationYear}
                  onChange={(e) =>
                    setPublicationYear(
                      e.target.value
                    )
                  }
                  placeholder="Example: 2026"
                  className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

              </div>

              {/* DOI */}

              <div className="mb-6">

                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  DOI
                </label>

                <input
                  type="text"
                  value={doi}
                  onChange={(e) =>
                    setDoi(
                      e.target.value
                    )
                  }
                  placeholder="Example: 10.1000/xyz123"
                  className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

              </div>

              {/* PAPER URL */}

              <div className="mb-6">

                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Paper URL
                </label>

                <input
                  type="url"
                  value={paperUrl}
                  onChange={(e) =>
                    setPaperUrl(
                      e.target.value
                    )
                  }
                  placeholder="https://example.com/research-paper"
                  className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

              </div>

              {/* AUTHORS */}

              <div className="mb-6">

                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Authors
                </label>

                <input
                  type="text"
                  value={authors}
                  onChange={(e) =>
                    setAuthors(
                      e.target.value
                    )
                  }
                  placeholder="Example: Harshitha, Rahul, Priya"
                  className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

              </div>

              {/* ABSTRACT */}

              <div className="mb-8">

                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Abstract
                </label>

                <textarea
                  value={abstractText}
                  onChange={(e) =>
                    setAbstractText(
                      e.target.value
                    )
                  }
                  placeholder="Enter the research paper abstract"
                  rows={7}
                  className="w-full resize-none rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

              </div>

              {/* BUTTONS */}

              <div className="flex flex-wrap gap-4">

                {/* CREATE */}

                {!researchPaper && (

                  <button
                    type="button"
                    onClick={
                      createResearchPaper
                    }
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

                {researchPaper && (

                  <button
                    type="button"
                    onClick={
                      updateResearchPaper
                    }
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

                {researchPaper && (

                  <button
                    type="button"
                    onClick={
                      deleteResearchPaper
                    }
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
            CURRENT RESEARCH PAPER
        ================================================= */}

        {researchPaper && (

          <div className="mt-8 rounded-2xl border border-slate-700 bg-[#0b1a2b] p-8">

            <h2 className="mb-6 text-2xl font-bold">
              Current Research Paper Details
            </h2>

            <div className="space-y-5">

              <Detail
                label="Research Paper ID"
                value={String(
                  researchPaper.id
                )}
              />

              <Detail
                label="Portfolio ID"
                value={String(
                  researchPaper.portfolio_id
                )}
              />

              <Detail
                label="Paper Title"
                value={
                  researchPaper.paper_title
                }
              />

              <Detail
                label="Journal Name"
                value={
                  researchPaper.journal_name
                }
              />

              <Detail
                label="Publication Year"
                value={
                  researchPaper.publication_year !==
                    null &&
                  researchPaper.publication_year !==
                    undefined
                    ? String(
                        researchPaper.publication_year
                      )
                    : null
                }
              />

              <Detail
                label="DOI"
                value={
                  researchPaper.doi
                }
              />

              <Detail
                label="Paper URL"
                value={
                  researchPaper.paper_url
                }
              />

              <Detail
                label="Authors"
                value={
                  researchPaper.authors
                }
              />

              <Detail
                label="Abstract"
                value={
                  researchPaper.abstract
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

      <p className="mt-1 break-words whitespace-pre-wrap text-white">
        {value || "Not provided"}
      </p>

    </div>
  );
}