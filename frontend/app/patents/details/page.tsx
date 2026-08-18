"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { apiRequest } from "@/lib/api";

type Portfolio = {
  id: number;
  title: string;
  category: string;
};

type PatentDetail = {
  id: number;
  portfolio_id: number;
  patent_title: string;
  patent_number: string | null;
  patent_status: string | null;
  filing_date: string | null;
  publication_date: string | null;
  inventors: string | null;
  patent_url: string | null;
  description: string | null;
};

export default function PatentDetailsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  /*
   * ---------------------------------------------------------
   * PORTFOLIO ID
   *
   * Example:
   * /patents/details?portfolioId=5
   * ---------------------------------------------------------
   */

  const urlPortfolioId = searchParams.get("portfolioId");

  /*
   * ---------------------------------------------------------
   * STATES
   * ---------------------------------------------------------
   */

  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);

  const [selectedPortfolioId, setSelectedPortfolioId] =
    useState<string>(urlPortfolioId || "");

  const [patent, setPatent] = useState<PatentDetail | null>(null);

  /*
   * Form fields
   */

  const [patentTitle, setPatentTitle] = useState("");
  const [patentNumber, setPatentNumber] = useState("");
  const [patentStatus, setPatentStatus] = useState("");

  /*
   * IMPORTANT:
   *
   * Date input uses:
   * YYYY-MM-DD
   *
   * This is exactly what FastAPI/Pydantic expects.
   */

  const [filingDate, setFilingDate] = useState("");
  const [publicationDate, setPublicationDate] = useState("");

  const [inventors, setInventors] = useState("");
  const [patentUrl, setPatentUrl] = useState("");
  const [description, setDescription] = useState("");

  /*
   * UI states
   */

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [loadingPortfolios, setLoadingPortfolios] =
    useState(true);

  const [loadingPatent, setLoadingPatent] =
    useState(false);

  const [creating, setCreating] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [deleting, setDeleting] = useState(false);

  /*
   * ---------------------------------------------------------
   * CLEAR FORM
   * ---------------------------------------------------------
   */

  function clearPatentForm() {
    setPatentTitle("");
    setPatentNumber("");
    setPatentStatus("");
    setFilingDate("");
    setPublicationDate("");
    setInventors("");
    setPatentUrl("");
    setDescription("");
  }

  /*
   * ---------------------------------------------------------
   * LOAD PORTFOLIOS
   * ---------------------------------------------------------
   */

  useEffect(() => {
    async function loadPortfolios() {
      try {
        setLoadingPortfolios(true);
        setError("");

        const data = await apiRequest("/portfolio/my");

        const list = Array.isArray(data)
          ? data
          : data?.portfolios || [];

        setPortfolios(list);
      } catch (err: any) {
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
   * ---------------------------------------------------------
   * UPDATE PORTFOLIO ID FROM URL
   * ---------------------------------------------------------
   */

  useEffect(() => {
    if (urlPortfolioId) {
      setSelectedPortfolioId(urlPortfolioId);
    }
  }, [urlPortfolioId]);

  /*
   * ---------------------------------------------------------
   * LOAD PATENT WHEN PORTFOLIO CHANGES
   * ---------------------------------------------------------
   */

  useEffect(() => {
    if (!selectedPortfolioId) {
      setPatent(null);
      clearPatentForm();
      return;
    }

    loadPatent(selectedPortfolioId);
  }, [selectedPortfolioId]);

  /*
   * ---------------------------------------------------------
   * LOAD PATENT
   * ---------------------------------------------------------
   */

  async function loadPatent(portfolioId: string) {
    try {
      setLoadingPatent(true);
      setError("");
      setMessage("");

      const data = await apiRequest(
        `/patent-details/${portfolioId}`
      );

      setPatent(data);

      setPatentTitle(data.patent_title || "");
      setPatentNumber(data.patent_number || "");
      setPatentStatus(data.patent_status || "");

      /*
       * Backend already returns:
       *
       * YYYY-MM-DD
       *
       * which is exactly what:
       *
       * <input type="date">
       *
       * needs.
       */

      setFilingDate(data.filing_date || "");
      setPublicationDate(
        data.publication_date || ""
      );

      setInventors(data.inventors || "");
      setPatentUrl(data.patent_url || "");
      setDescription(data.description || "");

      setMessage(
        "Patent details loaded successfully."
      );
    } catch (err: any) {
      /*
       * IMPORTANT:
       *
       * 404 is NORMAL when the selected portfolio
       * does not have patent details yet.
       *
       * Do NOT console.error here because Next.js
       * development mode can show an error overlay.
       */

      const errorMessage =
        err?.message || "";

      if (
        errorMessage.includes(
          "Patent details not found"
        )
      ) {
        setPatent(null);
        clearPatentForm();
        setError("");

        setMessage(
          "No patent details found for this portfolio. You can create them below."
        );

        return;
      }

      setError(
        errorMessage ||
          "Failed to load patent details."
      );
    } finally {
      setLoadingPatent(false);
    }
  }

  /*
   * ---------------------------------------------------------
   * SELECT PORTFOLIO
   * ---------------------------------------------------------
   */

  function handlePortfolioChange(
    value: string
  ) {
    setSelectedPortfolioId(value);

    setError("");
    setMessage("");

    if (value) {
      router.push(
        `/patents/details?portfolioId=${value}`
      );
    } else {
      router.push("/patents/details");
    }
  }

  /*
   * ---------------------------------------------------------
   * CREATE PATENT
   * ---------------------------------------------------------
   */

  async function createPatent() {
    if (!selectedPortfolioId) {
      setError(
        "Please select a portfolio first."
      );
      return;
    }

    if (!patentTitle.trim()) {
      setError(
        "Patent Title is required."
      );
      return;
    }

    setCreating(true);
    setError("");
    setMessage("");

    const requestBody = {
      patent_title:
        patentTitle.trim(),

      patent_number:
        patentNumber.trim() || null,

      patent_status:
        patentStatus.trim() || null,

      /*
       * HTML date input already returns:
       * YYYY-MM-DD
       */

      filing_date:
        filingDate || null,

      publication_date:
        publicationDate || null,

      inventors:
        inventors.trim() || null,

      patent_url:
        patentUrl.trim() || null,

      description:
        description.trim() || null,
    };

    try {
      const data = await apiRequest(
        `/patent-details/${selectedPortfolioId}`,
        {
          method: "POST",
          body: JSON.stringify(requestBody),
        }
      );

      setPatent(data);

      setPatentTitle(
        data.patent_title || ""
      );

      setPatentNumber(
        data.patent_number || ""
      );

      setPatentStatus(
        data.patent_status || ""
      );

      setFilingDate(
        data.filing_date || ""
      );

      setPublicationDate(
        data.publication_date || ""
      );

      setInventors(
        data.inventors || ""
      );

      setPatentUrl(
        data.patent_url || ""
      );

      setDescription(
        data.description || ""
      );

      setMessage(
        "Patent details created successfully."
      );
    } catch (err: any) {
      setError(
        err?.message ||
          "Failed to create patent details."
      );
    } finally {
      setCreating(false);
    }
  }

  /*
   * ---------------------------------------------------------
   * UPDATE PATENT
   * ---------------------------------------------------------
   */

  async function updatePatent() {
    if (!selectedPortfolioId) {
      setError(
        "Portfolio ID is missing."
      );
      return;
    }

    if (!patent) {
      setError(
        "Patent details do not exist yet."
      );
      return;
    }

    if (!patentTitle.trim()) {
      setError(
        "Patent Title is required."
      );
      return;
    }

    setUpdating(true);
    setError("");
    setMessage("");

    const requestBody = {
      patent_title:
        patentTitle.trim(),

      patent_number:
        patentNumber.trim() || null,

      patent_status:
        patentStatus.trim() || null,

      filing_date:
        filingDate || null,

      publication_date:
        publicationDate || null,

      inventors:
        inventors.trim() || null,

      patent_url:
        patentUrl.trim() || null,

      description:
        description.trim() || null,
    };

    try {
      const data = await apiRequest(
        `/patent-details/${selectedPortfolioId}`,
        {
          method: "PUT",
          body: JSON.stringify(requestBody),
        }
      );

      setPatent(data);

      setPatentTitle(
        data.patent_title || ""
      );

      setPatentNumber(
        data.patent_number || ""
      );

      setPatentStatus(
        data.patent_status || ""
      );

      setFilingDate(
        data.filing_date || ""
      );

      setPublicationDate(
        data.publication_date || ""
      );

      setInventors(
        data.inventors || ""
      );

      setPatentUrl(
        data.patent_url || ""
      );

      setDescription(
        data.description || ""
      );

      setMessage(
        "Patent details updated successfully."
      );
    } catch (err: any) {
      setError(
        err?.message ||
          "Failed to update patent details."
      );
    } finally {
      setUpdating(false);
    }
  }

  /*
   * ---------------------------------------------------------
   * DELETE PATENT
   * ---------------------------------------------------------
   */

  async function deletePatent() {
    if (!selectedPortfolioId) {
      setError(
        "Portfolio ID is missing."
      );
      return;
    }

    if (!patent) {
      setError(
        "No patent details exist."
      );
      return;
    }

    const confirmed =
      window.confirm(
        "Are you sure you want to delete these patent details?"
      );

    if (!confirmed) {
      return;
    }

    setDeleting(true);
    setError("");
    setMessage("");

    try {
      await apiRequest(
        `/patent-details/${selectedPortfolioId}`,
        {
          method: "DELETE",
        }
      );

      setPatent(null);

      clearPatentForm();

      setMessage(
        "Patent details deleted successfully. You can create them again."
      );
    } catch (err: any) {
      setError(
        err?.message ||
          "Failed to delete patent details."
      );
    } finally {
      setDeleting(false);
    }
  }

  /*
   * ---------------------------------------------------------
   * LOADING PORTFOLIOS
   * ---------------------------------------------------------
   */

  if (loadingPortfolios) {
    return (
      <div className="min-h-screen bg-[#06111f] text-white">
        <main className="mx-auto max-w-5xl px-8 py-20">
          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-400">
            InnoBridge-AI
          </p>

          <h1 className="mt-3 text-5xl font-bold">
            Patent Details
          </h1>

          <p className="mt-5 text-lg text-slate-400">
            Loading portfolios...
          </p>
        </main>
      </div>
    );
  }

  /*
   * ---------------------------------------------------------
   * MAIN PAGE
   * ---------------------------------------------------------
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
            Patent Details
          </h1>

          <p className="mt-3 text-lg text-slate-400">
            Manage detailed information about your patent.
          </p>
        </div>

        {/* PORTFOLIO SELECTOR */}

        <div className="mb-6 rounded-2xl border border-cyan-400/30 bg-[#0b1a2b] p-6">

          <p className="text-sm text-slate-500">
            Innovation Portfolio
          </p>

          <h2 className="mt-2 text-xl font-semibold text-cyan-400">
            Select Portfolio
          </h2>

          <p className="mt-2 text-sm text-slate-400">
            Choose the portfolio whose patent details you want to manage.
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

        {/* NO PORTFOLIO */}

        {!selectedPortfolioId && (
          <div className="rounded-2xl border border-slate-700 bg-[#0b1a2b] p-10 text-center">

            <div className="text-5xl">
              📜
            </div>

            <h2 className="mt-5 text-2xl font-bold">
              Select a Portfolio
            </h2>

            <p className="mt-3 text-slate-400">
              Select a portfolio above to
              create, view, update, or delete
              its patent details.
            </p>

          </div>
        )}

        {/* LOADING PATENT */}

        {selectedPortfolioId &&
          loadingPatent && (
            <div className="rounded-2xl border border-slate-700 bg-[#0b1a2b] p-10 text-center">

              <p className="text-lg text-slate-400">
                Loading patent details...
              </p>

            </div>
          )}

        {/* PATENT FORM */}

        {selectedPortfolioId &&
          !loadingPatent && (
            <div className="rounded-2xl border border-slate-700 bg-[#0b1a2b] p-8">

              <h2 className="mb-8 text-2xl font-bold">
                Patent Information
              </h2>

              {/* PATENT TITLE */}

              <div className="mb-6">
                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Patent Title *
                </label>

                <input
                  type="text"
                  value={patentTitle}
                  onChange={(e) =>
                    setPatentTitle(
                      e.target.value
                    )
                  }
                  placeholder="Enter patent title"
                  className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />
              </div>

              {/* PATENT NUMBER */}

              <div className="mb-6">
                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Patent Number
                </label>

                <input
                  type="text"
                  value={patentNumber}
                  onChange={(e) =>
                    setPatentNumber(
                      e.target.value
                    )
                  }
                  placeholder="Example: IN123456"
                  className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />
              </div>

              {/* PATENT STATUS */}

              <div className="mb-6">
                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Patent Status
                </label>

                <select
                  value={patentStatus}
                  onChange={(e) =>
                    setPatentStatus(
                      e.target.value
                    )
                  }
                  className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                >
                  <option value="">
                    -- Select Status --
                  </option>

                  <option value="Filed">
                    Filed
                  </option>

                  <option value="Published">
                    Published
                  </option>

                  <option value="Granted">
                    Granted
                  </option>

                  <option value="Pending">
                    Pending
                  </option>

                  <option value="Rejected">
                    Rejected
                  </option>
                </select>
              </div>

              {/* FILING DATE */}

              <div className="mb-6">
                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Filing Date
                </label>

                <input
                  type="date"
                  value={filingDate}
                  onChange={(e) =>
                    setFilingDate(
                      e.target.value
                    )
                  }
                  className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

                <p className="mt-2 text-xs text-slate-500">
                  Select the filing date using the calendar.
                </p>
              </div>

              {/* PUBLICATION DATE */}

              <div className="mb-6">
                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Publication Date
                </label>

                <input
                  type="date"
                  value={publicationDate}
                  onChange={(e) =>
                    setPublicationDate(
                      e.target.value
                    )
                  }
                  className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

                <p className="mt-2 text-xs text-slate-500">
                  Select the publication date using the calendar.
                </p>
              </div>

              {/* INVENTORS */}

              <div className="mb-6">
                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Inventors
                </label>

                <input
                  type="text"
                  value={inventors}
                  onChange={(e) =>
                    setInventors(
                      e.target.value
                    )
                  }
                  placeholder="Example: Harshitha, Rahul, Priya"
                  className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />
              </div>

              {/* PATENT URL */}

              <div className="mb-6">
                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Patent URL
                </label>

                <input
                  type="url"
                  value={patentUrl}
                  onChange={(e) =>
                    setPatentUrl(
                      e.target.value
                    )
                  }
                  placeholder="https://example.com/patent"
                  className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />
              </div>

              {/* DESCRIPTION */}

              <div className="mb-8">
                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Description
                </label>

                <textarea
                  value={description}
                  onChange={(e) =>
                    setDescription(
                      e.target.value
                    )
                  }
                  placeholder="Describe the patent..."
                  rows={7}
                  className="w-full resize-none rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />
              </div>

              {/* BUTTONS */}

              <div className="flex flex-wrap gap-4">

                {/* CREATE */}

                {!patent && (
                  <button
                    type="button"
                    onClick={createPatent}
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

                {patent && (
                  <button
                    type="button"
                    onClick={updatePatent}
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

                {patent && (
                  <button
                    type="button"
                    onClick={deletePatent}
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

        {/* CURRENT PATENT */}

        {patent && (
          <div className="mt-8 rounded-2xl border border-slate-700 bg-[#0b1a2b] p-8">

            <h2 className="mb-6 text-2xl font-bold">
              Current Patent Details
            </h2>

            <div className="space-y-5">

              <Detail
                label="Patent ID"
                value={String(patent.id)}
              />

              <Detail
                label="Portfolio ID"
                value={String(
                  patent.portfolio_id
                )}
              />

              <Detail
                label="Patent Title"
                value={patent.patent_title}
              />

              <Detail
                label="Patent Number"
                value={patent.patent_number}
              />

              <Detail
                label="Patent Status"
                value={patent.patent_status}
              />

              <Detail
                label="Filing Date"
                value={patent.filing_date}
              />

              <Detail
                label="Publication Date"
                value={
                  patent.publication_date
                }
              />

              <Detail
                label="Inventors"
                value={patent.inventors}
              />

              <Detail
                label="Patent URL"
                value={patent.patent_url}
              />

              <Detail
                label="Description"
                value={patent.description}
              />

            </div>
          </div>
        )}

      </main>
    </div>
  );
}

/*
 * ---------------------------------------------------------
 * DETAIL COMPONENT
 * ---------------------------------------------------------
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