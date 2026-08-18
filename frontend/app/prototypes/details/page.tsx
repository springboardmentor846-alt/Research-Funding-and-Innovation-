"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { apiRequest } from "@/lib/api";

interface PrototypeDetail {
  id: number;
  portfolio_id: number;
  prototype_name: string;
  prototype_type: string | null;
  development_stage: string | null;
  prototype_url: string | null;
  demo_video_url: string | null;
  description: string | null;
}

interface Portfolio {
  id: number;
  title: string;
  category: string;
}

export default function PrototypeDetailsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  /*
   * Portfolio ID comes from:
   *
   * /prototypes/details?portfolioId=5
   */

  const urlPortfolioId = searchParams.get("portfolioId");

  /*
   * --------------------------------------------------
   * STATES
   * --------------------------------------------------
   */

  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);

  const [selectedPortfolioId, setSelectedPortfolioId] =
    useState<string>(urlPortfolioId || "");

  const [prototype, setPrototype] =
    useState<PrototypeDetail | null>(null);

  const [prototypeName, setPrototypeName] =
    useState("");

  const [prototypeType, setPrototypeType] =
    useState("");

  const [developmentStage, setDevelopmentStage] =
    useState("");

  const [prototypeUrl, setPrototypeUrl] =
    useState("");

  const [demoVideoUrl, setDemoVideoUrl] =
    useState("");

  const [description, setDescription] =
    useState("");

  /*
   * UI states
   */

  const [loadingPortfolios, setLoadingPortfolios] =
    useState(true);

  const [loadingPrototype, setLoadingPrototype] =
    useState(false);

  const [creating, setCreating] =
    useState(false);

  const [updating, setUpdating] =
    useState(false);

  const [deleting, setDeleting] =
    useState(false);

  const [message, setMessage] =
    useState("");

  const [error, setError] =
    useState("");

  /*
   * --------------------------------------------------
   * CLEAR FORM
   * --------------------------------------------------
   */

  function clearForm() {
    setPrototypeName("");
    setPrototypeType("");
    setDevelopmentStage("");
    setPrototypeUrl("");
    setDemoVideoUrl("");
    setDescription("");
  }

  /*
   * --------------------------------------------------
   * LOAD PORTFOLIOS
   * --------------------------------------------------
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
   * --------------------------------------------------
   * UPDATE PORTFOLIO ID FROM URL
   * --------------------------------------------------
   */

  useEffect(() => {
    if (urlPortfolioId) {
      setSelectedPortfolioId(urlPortfolioId);
    }
  }, [urlPortfolioId]);

  /*
   * --------------------------------------------------
   * LOAD PROTOTYPE
   * --------------------------------------------------
   */

  useEffect(() => {
    if (!selectedPortfolioId) {
      setPrototype(null);
      clearForm();
      return;
    }

    loadPrototype(selectedPortfolioId);
  }, [selectedPortfolioId]);

  async function loadPrototype(
    portfolioId: string
  ) {
    try {
      setLoadingPrototype(true);
      setError("");
      setMessage("");

      const data = await apiRequest(
        `/prototype-details/${portfolioId}`
      );

      setPrototype(data);

      setPrototypeName(
        data.prototype_name || ""
      );

      setPrototypeType(
        data.prototype_type || ""
      );

      setDevelopmentStage(
        data.development_stage || ""
      );

      setPrototypeUrl(
        data.prototype_url || ""
      );

      setDemoVideoUrl(
        data.demo_video_url || ""
      );

      setDescription(
        data.description || ""
      );
    } catch (err: any) {
      /*
       * 404 is NORMAL if a prototype has not
       * been created for this portfolio yet.
       */

      const errorMessage =
        err?.message || "";

      if (
        errorMessage.includes(
          "Prototype details not found"
        )
      ) {
        setPrototype(null);
        clearForm();
        setError("");

        setMessage(
          "No prototype details found. You can create them below."
        );

        return;
      }

      setError(
        errorMessage ||
          "Failed to load prototype details."
      );
    } finally {
      setLoadingPrototype(false);
    }
  }

  /*
   * --------------------------------------------------
   * PORTFOLIO CHANGE
   * --------------------------------------------------
   */

  function handlePortfolioChange(
    value: string
  ) {
    setSelectedPortfolioId(value);

    setError("");
    setMessage("");

    if (value) {
      router.push(
        `/prototypes/details?portfolioId=${value}`
      );
    } else {
      router.push("/prototypes/details");
    }
  }

  /*
   * --------------------------------------------------
   * CREATE
   * --------------------------------------------------
   */

  async function handleCreate() {
    if (!selectedPortfolioId) {
      setError(
        "Please select a portfolio first."
      );
      return;
    }

    if (!prototypeName.trim()) {
      setError(
        "Prototype Name is required."
      );
      return;
    }

    try {
      setCreating(true);
      setError("");
      setMessage("");

      const requestBody = {
        prototype_name:
          prototypeName.trim(),

        prototype_type:
          prototypeType.trim() || null,

        development_stage:
          developmentStage.trim() || null,

        prototype_url:
          prototypeUrl.trim() || null,

        demo_video_url:
          demoVideoUrl.trim() || null,

        description:
          description.trim() || null,
      };

      const data = await apiRequest(
        `/prototype-details/${selectedPortfolioId}`,
        {
          method: "POST",
          body: JSON.stringify(requestBody),
        }
      );

      setPrototype(data);

      setPrototypeName(
        data.prototype_name || ""
      );

      setPrototypeType(
        data.prototype_type || ""
      );

      setDevelopmentStage(
        data.development_stage || ""
      );

      setPrototypeUrl(
        data.prototype_url || ""
      );

      setDemoVideoUrl(
        data.demo_video_url || ""
      );

      setDescription(
        data.description || ""
      );

      setMessage(
        "Prototype details created successfully."
      );
    } catch (err: any) {
      setError(
        err?.message ||
          "Failed to create prototype details."
      );
    } finally {
      setCreating(false);
    }
  }

  /*
   * --------------------------------------------------
   * UPDATE
   * --------------------------------------------------
   */

  async function handleUpdate() {
    if (!selectedPortfolioId) {
      setError(
        "Portfolio ID is missing."
      );
      return;
    }

    if (!prototype) {
      setError(
        "Prototype details do not exist."
      );
      return;
    }

    if (!prototypeName.trim()) {
      setError(
        "Prototype Name is required."
      );
      return;
    }

    try {
      setUpdating(true);
      setError("");
      setMessage("");

      const requestBody = {
        prototype_name:
          prototypeName.trim(),

        prototype_type:
          prototypeType.trim() || null,

        development_stage:
          developmentStage.trim() || null,

        prototype_url:
          prototypeUrl.trim() || null,

        demo_video_url:
          demoVideoUrl.trim() || null,

        description:
          description.trim() || null,
      };

      const data = await apiRequest(
        `/prototype-details/${selectedPortfolioId}`,
        {
          method: "PUT",
          body: JSON.stringify(requestBody),
        }
      );

      setPrototype(data);

      setPrototypeName(
        data.prototype_name || ""
      );

      setPrototypeType(
        data.prototype_type || ""
      );

      setDevelopmentStage(
        data.development_stage || ""
      );

      setPrototypeUrl(
        data.prototype_url || ""
      );

      setDemoVideoUrl(
        data.demo_video_url || ""
      );

      setDescription(
        data.description || ""
      );

      setMessage(
        "Prototype details updated successfully."
      );
    } catch (err: any) {
      setError(
        err?.message ||
          "Failed to update prototype details."
      );
    } finally {
      setUpdating(false);
    }
  }

  /*
   * --------------------------------------------------
   * DELETE
   * --------------------------------------------------
   */

  async function handleDelete() {
    if (!selectedPortfolioId) {
      setError(
        "Portfolio ID is missing."
      );
      return;
    }

    if (!prototype) {
      setError(
        "Prototype details do not exist."
      );
      return;
    }

    const confirmed =
      window.confirm(
        "Are you sure you want to delete this prototype?"
      );

    if (!confirmed) {
      return;
    }

    try {
      setDeleting(true);
      setError("");
      setMessage("");

      await apiRequest(
        `/prototype-details/${selectedPortfolioId}`,
        {
          method: "DELETE",
        }
      );

      setPrototype(null);

      clearForm();

      setMessage(
        "Prototype details deleted successfully."
      );
    } catch (err: any) {
      setError(
        err?.message ||
          "Failed to delete prototype details."
      );
    } finally {
      setDeleting(false);
    }
  }

  /*
   * --------------------------------------------------
   * LOADING PORTFOLIOS
   * --------------------------------------------------
   */

  if (loadingPortfolios) {
    return (
      <div className="min-h-screen bg-[#06111f] text-white">
        <main className="mx-auto max-w-5xl px-8 py-16">

          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-400">
            InnoBridge-AI
          </p>

          <h1 className="mt-3 text-5xl font-bold">
            Prototype Details
          </h1>

          <p className="mt-5 text-slate-400">
            Loading portfolios...
          </p>

        </main>
      </div>
    );
  }

  /*
   * --------------------------------------------------
   * MAIN UI
   * --------------------------------------------------
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
            Prototype Details
          </h1>

          <p className="mt-3 text-lg text-slate-400">
            Manage detailed information about your prototype.
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
            Select the portfolio whose prototype
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

        {/* NO PORTFOLIO */}

        {!selectedPortfolioId && (
          <div className="rounded-2xl border border-slate-700 bg-[#0b1a2b] p-10 text-center">

            <div className="text-5xl">
              🧪
            </div>

            <h2 className="mt-5 text-2xl font-bold">
              Select a Portfolio
            </h2>

            <p className="mt-3 text-slate-400">
              Select a portfolio above to
              create, view, update, or delete
              its prototype details.
            </p>

          </div>
        )}

        {/* LOADING PROTOTYPE */}

        {selectedPortfolioId &&
          loadingPrototype && (
            <div className="rounded-2xl border border-slate-700 bg-[#0b1a2b] p-10 text-center">

              <p className="text-lg text-slate-400">
                Loading prototype details...
              </p>

            </div>
          )}

        {/* FORM */}

        {selectedPortfolioId &&
          !loadingPrototype && (
            <div className="rounded-2xl border border-slate-700 bg-[#0b1a2b] p-8">

              <h2 className="mb-8 text-2xl font-bold">
                Prototype Information
              </h2>

              {/* PROTOTYPE NAME */}

              <div className="mb-6">

                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Prototype Name *
                </label>

                <input
                  type="text"
                  value={prototypeName}
                  onChange={(e) =>
                    setPrototypeName(
                      e.target.value
                    )
                  }
                  placeholder="Enter prototype name"
                  className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

              </div>

              {/* PROTOTYPE TYPE */}

              <div className="mb-6">

                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Prototype Type
                </label>

                <select
                  value={prototypeType}
                  onChange={(e) =>
                    setPrototypeType(
                      e.target.value
                    )
                  }
                  className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                >

                  <option value="">
                    -- Select Type --
                  </option>

                  <option value="Software">
                    Software
                  </option>

                  <option value="Hardware">
                    Hardware
                  </option>

                  <option value="AI/ML">
                    AI / ML
                  </option>

                  <option value="IoT">
                    IoT
                  </option>

                  <option value="Web Application">
                    Web Application
                  </option>

                  <option value="Mobile Application">
                    Mobile Application
                  </option>

                  <option value="Other">
                    Other
                  </option>

                </select>

              </div>

              {/* DEVELOPMENT STAGE */}

              <div className="mb-6">

                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Development Stage
                </label>

                <select
                  value={developmentStage}
                  onChange={(e) =>
                    setDevelopmentStage(
                      e.target.value
                    )
                  }
                  className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                >

                  <option value="">
                    -- Select Stage --
                  </option>

                  <option value="Idea">
                    Idea
                  </option>

                  <option value="Proof of Concept">
                    Proof of Concept
                  </option>

                  <option value="Prototype">
                    Prototype
                  </option>

                  <option value="MVP">
                    MVP
                  </option>

                  <option value="Beta">
                    Beta
                  </option>

                  <option value="Production Ready">
                    Production Ready
                  </option>

                </select>

              </div>

              {/* PROTOTYPE URL */}

              <div className="mb-6">

                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Prototype URL
                </label>

                <input
                  type="url"
                  value={prototypeUrl}
                  onChange={(e) =>
                    setPrototypeUrl(
                      e.target.value
                    )
                  }
                  placeholder="https://example.com/prototype"
                  className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

              </div>

              {/* DEMO VIDEO URL */}

              <div className="mb-6">

                <label className="mb-2 block text-sm font-semibold text-slate-400">
                  Demo Video URL
                </label>

                <input
                  type="url"
                  value={demoVideoUrl}
                  onChange={(e) =>
                    setDemoVideoUrl(
                      e.target.value
                    )
                  }
                  placeholder="https://youtube.com/watch?v=..."
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
                  placeholder="Describe your prototype..."
                  rows={7}
                  className="w-full resize-none rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

              </div>

              {/* BUTTONS */}

              <div className="flex flex-wrap gap-4">

                {/* CREATE */}

                {!prototype && (
                  <button
                    type="button"
                    onClick={handleCreate}
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

                {prototype && (
                  <button
                    type="button"
                    onClick={handleUpdate}
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

                {prototype && (
                  <button
                    type="button"
                    onClick={handleDelete}
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

        {/* CURRENT PROTOTYPE */}

        {prototype && (
          <div className="mt-8 rounded-2xl border border-slate-700 bg-[#0b1a2b] p-8">

            <h2 className="mb-6 text-2xl font-bold">
              Current Prototype Details
            </h2>

            <div className="space-y-5">

              <Detail
                label="Prototype ID"
                value={String(
                  prototype.id
                )}
              />

              <Detail
                label="Portfolio ID"
                value={String(
                  prototype.portfolio_id
                )}
              />

              <Detail
                label="Prototype Name"
                value={
                  prototype.prototype_name
                }
              />

              <Detail
                label="Prototype Type"
                value={
                  prototype.prototype_type
                }
              />

              <Detail
                label="Development Stage"
                value={
                  prototype.development_stage
                }
              />

              <div className="border-b border-slate-700 pb-4">

                <p className="text-sm text-slate-500">
                  Prototype URL
                </p>

                {prototype.prototype_url ? (
                  <a
                    href={
                      prototype.prototype_url
                    }
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-1 block break-all text-cyan-400 hover:underline"
                  >
                    {prototype.prototype_url}
                  </a>
                ) : (
                  <p className="mt-1 text-white">
                    Not provided
                  </p>
                )}

              </div>

              <div className="border-b border-slate-700 pb-4">

                <p className="text-sm text-slate-500">
                  Demo Video URL
                </p>

                {prototype.demo_video_url ? (
                  <a
                    href={
                      prototype.demo_video_url
                    }
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-1 block break-all text-cyan-400 hover:underline"
                  >
                    {prototype.demo_video_url}
                  </a>
                ) : (
                  <p className="mt-1 text-white">
                    Not provided
                  </p>
                )}

              </div>

              <Detail
                label="Description"
                value={
                  prototype.description
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
 * --------------------------------------------------
 * DETAIL COMPONENT
 * --------------------------------------------------
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