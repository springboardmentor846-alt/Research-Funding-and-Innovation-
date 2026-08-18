"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { apiRequest, logout } from "@/lib/api";
import Sidebar from "@/components/Sidebar";

interface Portfolio {
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
}

interface PortfolioForm {
  title: string;
  category: string;
  description: string;
  status: string;
  visibility: string;
  github_url: string;
  paper_url: string;
  prototype_link: string;
}

const emptyForm: PortfolioForm = {
  title: "",
  category: "Project",
  description: "",
  status: "Ongoing",
  visibility: "Private",
  github_url: "",
  paper_url: "",
  prototype_link: "",
};

export default function PortfolioPage() {
  const router = useRouter();

  const [portfolios, setPortfolios] =
    useState<Portfolio[]>([]);

  const [formData, setFormData] =
    useState<PortfolioForm>(emptyForm);

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [showForm, setShowForm] =
    useState(false);

  const [editingId, setEditingId] =
    useState<number | null>(null);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  /* =========================================
     LOAD PORTFOLIOS
  ========================================= */

  const loadPortfolios = async () => {
    try {
      setLoading(true);
      setError("");

      const token =
        localStorage.getItem("access_token");

      if (!token) {
        router.push("/login");
        return;
      }

      const data =
        await apiRequest("/portfolio/my");

      setPortfolios(data);

    } catch (err: any) {
      console.error(
        "Portfolio loading error:",
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
          "Unable to load portfolios"
      );

    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPortfolios();
  }, []);

  /* =========================================
     INPUT CHANGE
  ========================================= */

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement |
      HTMLTextAreaElement |
      HTMLSelectElement
    >
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  /* =========================================
     OPEN CREATE FORM
  ========================================= */

  const openCreateForm = () => {
    setFormData(emptyForm);
    setEditingId(null);
    setShowForm(true);
    setError("");
    setSuccess("");
  };

  /* =========================================
     OPEN EDIT FORM
  ========================================= */

  const openEditForm = (
    portfolio: Portfolio
  ) => {
    setFormData({
      title: portfolio.title,
      category: portfolio.category,
      description:
        portfolio.description ?? "",
      status: portfolio.status,
      visibility:
        portfolio.visibility,
      github_url:
        portfolio.github_url ?? "",
      paper_url:
        portfolio.paper_url ?? "",
      prototype_link:
        portfolio.prototype_link ?? "",
    });

    setEditingId(portfolio.id);
    setShowForm(true);
    setError("");
    setSuccess("");
  };

  /* =========================================
     SAVE PORTFOLIO
  ========================================= */

  const handleSubmit = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    setSaving(true);
    setError("");
    setSuccess("");

    try {
      const payload = {
        title: formData.title,
        category: formData.category,
        description:
          formData.description || null,
        status: formData.status,
        visibility:
          formData.visibility,
        github_url:
          formData.github_url || null,
        paper_url:
          formData.paper_url || null,
        prototype_link:
          formData.prototype_link || null,
      };

      if (editingId !== null) {
        await apiRequest(
          `/portfolio/update/${editingId}`,
          {
            method: "PUT",
            body: JSON.stringify(payload),
          }
        );

        setSuccess(
          "Portfolio updated successfully."
        );
      } else {
        await apiRequest(
          "/portfolio/create",
          {
            method: "POST",
            body: JSON.stringify(payload),
          }
        );

        setSuccess(
          "Portfolio created successfully."
        );
      }

      setFormData(emptyForm);
      setEditingId(null);
      setShowForm(false);

      await loadPortfolios();

    } catch (err: any) {
      setError(
        err.message ||
          "Unable to save portfolio"
      );
    } finally {
      setSaving(false);
    }
  };

  /* =========================================
     DELETE
  ========================================= */

  const handleDelete = async (
    portfolioId: number
  ) => {
    const confirmed =
      window.confirm(
        "Are you sure you want to delete this portfolio?"
      );

    if (!confirmed) {
      return;
    }

    try {
      setError("");
      setSuccess("");

      await apiRequest(
        `/portfolio/delete/${portfolioId}`,
        {
          method: "DELETE",
        }
      );

      setSuccess(
        "Portfolio deleted successfully."
      );

      await loadPortfolios();

    } catch (err: any) {
      setError(
        err.message ||
          "Unable to delete portfolio"
      );
    }
  };

  /* =========================================
     LOGOUT
  ========================================= */

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  /* =========================================
     LOADING
  ========================================= */

  if (loading) {
    return (
      <main className="min-h-screen bg-[#06111f] text-white flex items-center justify-center">
        <div className="text-xl font-semibold text-cyan-400">
          Loading portfolio...
        </div>
      </main>
    );
  }

  return (
    <div className="min-h-screen bg-[#06111f] text-white">

      <Sidebar />

      <main className="min-h-screen ml-80">

        {/* =========================
            NAVBAR
        ========================= */}

        <header className="border-b border-slate-800 bg-[#071321]">

          <div className="mx-auto flex max-w-7xl items-center justify-between px-8 py-5">

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

            <button
              onClick={handleLogout}
              className="rounded-lg border border-slate-600 px-5 py-2 text-sm font-semibold transition hover:border-red-400 hover:text-red-400"
            >
              Logout
            </button>

          </div>

        </header>

        {/* =========================
            CONTENT
        ========================= */}

        <section className="mx-auto max-w-7xl px-8 py-12">

          {/* Heading */}

          <div className="mb-10 flex flex-col gap-6 md:flex-row md:items-end md:justify-between">

            <div>

              <p className="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-400">
                InnoBridge-AI
              </p>

              <h1 className="mt-3 text-5xl font-bold">
                Innovation Portfolio
              </h1>

              <p className="mt-3 text-lg text-slate-400">
                Manage your research, projects, patents, and prototypes.
              </p>

            </div>

            <button
              onClick={openCreateForm}
              className="rounded-xl bg-cyan-500 px-6 py-3 font-bold text-black transition hover:bg-cyan-400"
            >
              + Add Innovation
            </button>

          </div>

          {/* Messages */}

          {success && (
            <div className="mb-6 rounded-xl border border-green-500/40 bg-green-500/10 px-5 py-4 text-green-400">
              {success}
            </div>
          )}

          {error && (
            <div className="mb-6 rounded-xl border border-red-500/40 bg-red-500/10 px-5 py-4 text-red-400">
              {error}
            </div>
          )}

          {/* =========================
              CREATE / EDIT FORM
          ========================= */}

          {showForm && (
            <div className="mb-10 rounded-3xl border border-slate-700 bg-[#0c1929] p-8 md:p-10">

              <div className="mb-8">

                <h2 className="text-2xl font-bold">
                  {editingId !== null
                    ? "Edit Innovation"
                    : "Add Innovation"}
                </h2>

                <p className="mt-2 text-slate-400">
                  Add the basic information about your innovation.
                </p>

              </div>

              <form
                onSubmit={handleSubmit}
                className="grid gap-6 md:grid-cols-2"
              >

                {/* Title */}

                <div className="md:col-span-2">

                  <label className="mb-3 block text-sm font-semibold text-slate-300">
                    Title *
                  </label>

                  <input
                    type="text"
                    name="title"
                    value={formData.title}
                    onChange={handleChange}
                    required
                    placeholder="Enter innovation title"
                    className="w-full rounded-xl border border-slate-600 bg-[#071321] px-5 py-4 text-white outline-none focus:border-cyan-400"
                  />

                </div>

                {/* Category */}

                <div>

                  <label className="mb-3 block text-sm font-semibold text-slate-300">
                    Category *
                  </label>

                  <select
                    name="category"
                    value={formData.category}
                    onChange={handleChange}
                    className="w-full rounded-xl border border-slate-600 bg-[#071321] px-5 py-4 text-white outline-none focus:border-cyan-400"
                  >
                    <option value="Project">
                      Project
                    </option>

                    <option value="Research Paper">
                      Research Paper
                    </option>

                    <option value="Patent">
                      Patent
                    </option>

                    <option value="Prototype">
                      Prototype
                    </option>
                  </select>

                </div>

                {/* Status */}

                <div>

                  <label className="mb-3 block text-sm font-semibold text-slate-300">
                    Status *
                  </label>

                  <select
                    name="status"
                    value={formData.status}
                    onChange={handleChange}
                    className="w-full rounded-xl border border-slate-600 bg-[#071321] px-5 py-4 text-white outline-none focus:border-cyan-400"
                  >
                    <option value="Ongoing">
                      Ongoing
                    </option>

                    <option value="Completed">
                      Completed
                    </option>

                    <option value="Published">
                      Published
                    </option>

                    <option value="Filed">
                      Filed
                    </option>
                  </select>

                </div>

                {/* Visibility */}

                <div>

                  <label className="mb-3 block text-sm font-semibold text-slate-300">
                    Visibility *
                  </label>

                  <select
                    name="visibility"
                    value={formData.visibility}
                    onChange={handleChange}
                    className="w-full rounded-xl border border-slate-600 bg-[#071321] px-5 py-4 text-white outline-none focus:border-cyan-400"
                  >
                    <option value="Private">
                      Private
                    </option>

                    <option value="Public">
                      Public
                    </option>
                  </select>

                </div>

                {/* Description */}

                <div className="md:col-span-2">

                  <label className="mb-3 block text-sm font-semibold text-slate-300">
                    Description
                  </label>

                  <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    rows={5}
                    placeholder="Describe your innovation..."
                    className="w-full resize-none rounded-xl border border-slate-600 bg-[#071321] px-5 py-4 text-white outline-none focus:border-cyan-400"
                  />

                </div>

                {/* GitHub */}

                <div>

                  <label className="mb-3 block text-sm font-semibold text-slate-300">
                    GitHub URL
                  </label>

                  <input
                    type="url"
                    name="github_url"
                    value={formData.github_url}
                    onChange={handleChange}
                    placeholder="https://github.com/..."
                    className="w-full rounded-xl border border-slate-600 bg-[#071321] px-5 py-4 text-white outline-none focus:border-cyan-400"
                  />

                </div>

                {/* Paper */}

                <div>

                  <label className="mb-3 block text-sm font-semibold text-slate-300">
                    Research Paper URL
                  </label>

                  <input
                    type="url"
                    name="paper_url"
                    value={formData.paper_url}
                    onChange={handleChange}
                    placeholder="https://..."
                    className="w-full rounded-xl border border-slate-600 bg-[#071321] px-5 py-4 text-white outline-none focus:border-cyan-400"
                  />

                </div>

                {/* Prototype */}

                <div className="md:col-span-2">

                  <label className="mb-3 block text-sm font-semibold text-slate-300">
                    Prototype URL
                  </label>

                  <input
                    type="url"
                    name="prototype_link"
                    value={formData.prototype_link}
                    onChange={handleChange}
                    placeholder="https://..."
                    className="w-full rounded-xl border border-slate-600 bg-[#071321] px-5 py-4 text-white outline-none focus:border-cyan-400"
                  />

                </div>

                {/* Buttons */}

                <div className="md:col-span-2 flex flex-col gap-4 sm:flex-row">

                  <button
                    type="submit"
                    disabled={saving}
                    className="rounded-xl bg-cyan-500 px-8 py-4 font-bold text-black transition hover:bg-cyan-400 disabled:opacity-50"
                  >
                    {saving
                      ? "Saving..."
                      : editingId !== null
                      ? "Save Changes"
                      : "Create Innovation"}
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setShowForm(false);
                      setEditingId(null);
                      setFormData(emptyForm);
                    }}
                    className="rounded-xl border border-slate-600 px-8 py-4 font-semibold text-slate-300 transition hover:border-white hover:text-white"
                  >
                    Cancel
                  </button>

                </div>

              </form>

            </div>
          )}

          {/* =========================
              EMPTY STATE
          ========================= */}

          {portfolios.length === 0 && !showForm && (

            <div className="rounded-3xl border border-dashed border-slate-700 bg-[#0c1929] p-16 text-center">

              <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-2xl bg-cyan-400/10 text-4xl">
                💡
              </div>

              <h2 className="mt-6 text-2xl font-bold">
                No Innovations Yet
              </h2>

              <p className="mx-auto mt-3 max-w-xl text-slate-400">
                Start building your innovation portfolio by adding your first project, research paper, patent, or prototype.
              </p>

              <button
                onClick={openCreateForm}
                className="mt-6 rounded-xl bg-cyan-500 px-6 py-3 font-bold text-black hover:bg-cyan-400"
              >
                + Add Your First Innovation
              </button>

            </div>

          )}

          {/* =========================
              PORTFOLIO CARDS
          ========================= */}

          <div className="grid gap-6 md:grid-cols-2">

            {portfolios.map(
              (portfolio) => (

                <div
                  key={portfolio.id}
                  className="rounded-3xl border border-slate-700 bg-[#0c1929] p-7 transition hover:border-cyan-400/40"
                >

                  {/* Top */}

                  <div className="flex items-start justify-between gap-4">

                    <div>

                      <span className="inline-flex rounded-full border border-cyan-400/30 bg-cyan-400/10 px-3 py-1 text-xs font-semibold text-cyan-400">
                        {portfolio.category}
                      </span>

                      <h2 className="mt-4 text-2xl font-bold">
                        {portfolio.title}
                      </h2>

                    </div>

                    <span className="shrink-0 rounded-full border border-slate-600 px-3 py-1 text-xs text-slate-400">
                      {portfolio.visibility}
                    </span>

                  </div>

                  {/* Description */}

                  <p className="mt-5 min-h-12 text-slate-400">
                    {portfolio.description ||
                      "No description provided."}
                  </p>

                  {/* Status */}

                  <div className="mt-6">

                    <span className="text-sm text-slate-500">
                      Status
                    </span>

                    <p className="mt-1 font-semibold text-white">
                      {portfolio.status}
                    </p>

                  </div>

                  {/* Links */}

                  <div className="mt-6 flex flex-wrap gap-3">

                    {portfolio.github_url && (
                      <a
                        href={portfolio.github_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="rounded-lg border border-slate-600 px-4 py-2 text-sm text-slate-300 hover:border-cyan-400 hover:text-cyan-400"
                      >
                        GitHub ↗
                      </a>
                    )}

                    {portfolio.paper_url && (
                      <a
                        href={portfolio.paper_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="rounded-lg border border-slate-600 px-4 py-2 text-sm text-slate-300 hover:border-cyan-400 hover:text-cyan-400"
                      >
                        Research Paper ↗
                      </a>
                    )}

                    {portfolio.prototype_link && (
                      <a
                        href={portfolio.prototype_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="rounded-lg border border-slate-600 px-4 py-2 text-sm text-slate-300 hover:border-cyan-400 hover:text-cyan-400"
                      >
                        Prototype ↗
                      </a>
                    )}

                  </div>

                  {/* Actions */}

<div className="mt-7 flex gap-3 border-t border-slate-700 pt-6">

    {/* View Details */}
    <button
        onClick={() =>
            router.push(
                `/innovation-portfolio/${portfolio.id}`
            )
        }
        className="rounded-lg border border-cyan-500 px-5 py-2 text-sm font-semibold text-cyan-400 hover:bg-cyan-500 hover:text-white"
    >
        View Details
    </button>

    {/* Edit */}
    <button
        onClick={() =>
            openEditForm(
                portfolio
            )
        }
        className="rounded-lg bg-slate-700 px-5 py-2 text-sm font-semibold hover:bg-slate-600"
    >
        Edit
    </button>

    {/* Delete */}
    <button
        onClick={() =>
            handleDelete(
                portfolio.id
            )
        }
        className="rounded-lg border border-red-500/40 px-5 py-2 text-sm font-semibold text-red-400 hover:bg-red-500/10"
    >
        Delete
    </button>

</div>
                  </div>

                

              )
            )}

          </div>

        </section>

      </main>

    </div>
  );
}