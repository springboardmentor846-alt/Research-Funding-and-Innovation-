"use client";

import { useEffect, useState } from "react";
import { apiRequest } from "@/lib/api";

type DocumentType =
  | "Research Paper"
  | "Patent"
  | "Prototype"
  | "Document"
  | "Image"
  | "Dataset";

type Visibility =
  | "Private"
  | "Team"
  | "Public";

interface Portfolio {
  id: number;
  title: string;
  category?: string;
}

interface VaultFile {
  id: number;
  user_id: number;
  portfolio_id: number;

  title: string;
  description: string | null;

  document_type: DocumentType;

  original_filename: string;
  stored_filename: string;
  file_path: string;
  file_extension: string;
  file_size: number;
  mime_type: string;

  visibility: Visibility;
  nda_required: boolean;

  uploaded_at: string;
  updated_at: string;
}

export default function InnovationVaultPage() {
  /*
   * ==================================================
   * STATES
   * ==================================================
   */

  const [portfolios, setPortfolios] =
    useState<Portfolio[]>([]);

  const [files, setFiles] =
    useState<VaultFile[]>([]);

  const [selectedPortfolioId, setSelectedPortfolioId] =
    useState("");

  const [title, setTitle] =
    useState("");

  const [description, setDescription] =
    useState("");

  const [documentType, setDocumentType] =
    useState<DocumentType | "">("");

  const [visibility, setVisibility] =
    useState<Visibility>("Private");

  const [ndaRequired, setNdaRequired] =
    useState(false);

  const [selectedFile, setSelectedFile] =
    useState<File | null>(null);

  /*
   * Edit states
   */

  const [editingId, setEditingId] =
    useState<number | null>(null);

  const [editTitle, setEditTitle] =
    useState("");

  const [editDescription, setEditDescription] =
    useState("");

  const [editVisibility, setEditVisibility] =
    useState<Visibility>("Private");

  const [editNdaRequired, setEditNdaRequired] =
    useState(false);

  /*
   * Loading states
   */

  const [loadingPortfolios, setLoadingPortfolios] =
    useState(true);

  const [loadingFiles, setLoadingFiles] =
    useState(true);

  const [uploading, setUploading] =
    useState(false);

  const [updating, setUpdating] =
    useState(false);

  const [deletingId, setDeletingId] =
    useState<number | null>(null);

  /*
   * Messages
   */

  const [message, setMessage] =
    useState("");

  const [error, setError] =
    useState("");

  /*
   * ==================================================
   * LOAD PORTFOLIOS
   * ==================================================
   */

  useEffect(() => {
    loadPortfolios();
  }, []);

  async function loadPortfolios() {
    try {
      setLoadingPortfolios(true);
      setError("");

      const data =
        await apiRequest("/portfolio/my");

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

  /*
   * ==================================================
   * LOAD VAULT FILES
   * ==================================================
   */

  useEffect(() => {
    loadFiles();
  }, []);

  async function loadFiles() {
    try {
      setLoadingFiles(true);
      setError("");

      const data =
        await apiRequest("/vault/files");

      setFiles(
        Array.isArray(data)
          ? data
          : []
      );
    } catch (err: any) {
      setError(
        err?.message ||
          "Failed to load vault files."
      );
    } finally {
      setLoadingFiles(false);
    }
  }

  /*
   * ==================================================
   * CLEAR UPLOAD FORM
   * ==================================================
   */

  function clearUploadForm() {
    setSelectedPortfolioId("");
    setTitle("");
    setDescription("");
    setDocumentType("");
    setVisibility("Private");
    setNdaRequired(false);
    setSelectedFile(null);

    const input =
      document.getElementById(
        "vault-file-input"
      ) as HTMLInputElement | null;

    if (input) {
      input.value = "";
    }
  }

  /*
   * ==================================================
   * FILE CHANGE
   * ==================================================
   */

  function handleFileChange(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    const file =
      event.target.files?.[0];

    if (!file) {
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
    setError("");
    setMessage("");
  }

  /*
   * ==================================================
   * UPLOAD
   * ==================================================
   */

  async function handleUpload() {
    setError("");
    setMessage("");

    if (!selectedPortfolioId) {
      setError(
        "Please select an innovation portfolio."
      );
      return;
    }

    if (!title.trim()) {
      setError(
        "Please enter a title."
      );
      return;
    }

    if (!documentType) {
      setError(
        "Please select a document type."
      );
      return;
    }

    if (!selectedFile) {
      setError(
        "Please select a file."
      );
      return;
    }

    try {
      setUploading(true);

      /*
       * IMPORTANT:
       * Vault upload uses FormData because
       * FastAPI expects UploadFile + Form fields.
       */

      const formData =
        new FormData();

      formData.append(
        "portfolio_id",
        selectedPortfolioId
      );

      formData.append(
        "title",
        title.trim()
      );

      formData.append(
        "description",
        description.trim()
      );

      formData.append(
        "document_type",
        documentType
      );

      formData.append(
        "visibility",
        visibility
      );

      formData.append(
        "nda_required",
        String(ndaRequired)
      );

      formData.append(
        "file",
        selectedFile
      );

      const createdFile =
        await apiRequest(
          "/vault/upload",
          {
            method: "POST",
            body: formData,
          }
        );

      setFiles((previous) => [
        createdFile,
        ...previous,
      ]);

      clearUploadForm();

      setMessage(
        "File uploaded successfully."
      );
    } catch (err: any) {
      setError(
        err?.message ||
          "Failed to upload file."
      );
    } finally {
      setUploading(false);
    }
  }

  /*
   * ==================================================
   * START EDIT
   * ==================================================
   */

  function startEdit(file: VaultFile) {
    setEditingId(file.id);

    setEditTitle(
      file.title || ""
    );

    setEditDescription(
      file.description || ""
    );

    setEditVisibility(
      file.visibility
    );

    setEditNdaRequired(
      file.nda_required
    );

    setError("");
    setMessage("");
  }

  /*
   * ==================================================
   * CANCEL EDIT
   * ==================================================
   */

  function cancelEdit() {
    setEditingId(null);
    setEditTitle("");
    setEditDescription("");
    setEditVisibility("Private");
    setEditNdaRequired(false);
  }

  /*
   * ==================================================
   * UPDATE
   * ==================================================
   */

  async function handleUpdate(
    vaultId: number
  ) {
    setError("");
    setMessage("");

    if (!editTitle.trim()) {
      setError(
        "Title cannot be empty."
      );
      return;
    }

    try {
      setUpdating(true);

      const updatedFile =
        await apiRequest(
          `/vault/${vaultId}`,
          {
            method: "PUT",
            body: JSON.stringify({
              title:
                editTitle.trim(),

              description:
                editDescription.trim() ||
                null,

              visibility:
                editVisibility,

              nda_required:
                editNdaRequired,
            }),
          }
        );

      setFiles((previous) =>
        previous.map((file) =>
          file.id === vaultId
            ? updatedFile
            : file
        )
      );

      cancelEdit();

      setMessage(
        "Vault file updated successfully."
      );
    } catch (err: any) {
      setError(
        err?.message ||
          "Failed to update file."
      );
    } finally {
      setUpdating(false);
    }
  }

  /*
   * ==================================================
   * DELETE
   * ==================================================
   */

  async function handleDelete(
    vaultId: number
  ) {
    const confirmed =
      window.confirm(
        "Are you sure you want to delete this file?"
      );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingId(vaultId);
      setError("");
      setMessage("");

      await apiRequest(
        `/vault/${vaultId}`,
        {
          method: "DELETE",
        }
      );

      setFiles((previous) =>
        previous.filter(
          (file) =>
            file.id !== vaultId
        )
      );

      if (editingId === vaultId) {
        cancelEdit();
      }

      setMessage(
        "File deleted successfully."
      );
    } catch (err: any) {
      setError(
        err?.message ||
          "Failed to delete file."
      );
    } finally {
      setDeletingId(null);
    }
  }

  /*
   * ==================================================
   * FORMAT FILE SIZE
   * ==================================================
   */

  function formatFileSize(
    bytes: number
  ) {
    if (bytes < 1024) {
      return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
      return `${(
        bytes / 1024
      ).toFixed(1)} KB`;
    }

    if (bytes < 1024 * 1024 * 1024) {
      return `${(
        bytes /
        (1024 * 1024)
      ).toFixed(1)} MB`;
    }

    return `${(
      bytes /
      (1024 * 1024 * 1024)
    ).toFixed(1)} GB`;
  }

  /*
   * ==================================================
   * ICON
   * ==================================================
   */

  function getDocumentIcon(
    type: DocumentType
  ) {
    switch (type) {
      case "Research Paper":
        return "📄";

      case "Patent":
        return "📜";

      case "Prototype":
        return "🧪";

      case "Image":
        return "🖼️";

      case "Dataset":
        return "📊";

      default:
        return "📁";
    }
  }

  /*
   * ==================================================
   * LOADING
   * ==================================================
   */

  if (
    loadingPortfolios &&
    loadingFiles
  ) {
    return (
      <main className="min-h-screen bg-[#06111f] px-8 py-16 text-white">

        <p className="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-400">
          InnoBridge-AI
        </p>

        <h1 className="mt-3 text-5xl font-bold">
          Innovation Vault
        </h1>

        <p className="mt-5 text-slate-400">
          Loading...
        </p>

      </main>
    );
  }

  /*
   * ==================================================
   * MAIN
   * ==================================================
   */

  return (
    <main className="min-h-screen bg-[#06111f] px-8 py-12 text-white">

      <div className="mx-auto max-w-7xl">

        {/* HEADER */}

        <div className="mb-10">

          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-400">
            InnoBridge-AI
          </p>

          <h1 className="mt-3 text-5xl font-bold">
            Innovation Vault
          </h1>

          <p className="mt-3 text-lg text-slate-400">
            Securely manage your innovation files.
          </p>

        </div>

        {/* SUCCESS */}

        {message && (
          <div className="mb-6 rounded-xl border border-green-500/40 bg-green-500/10 p-4 text-green-400">
            {message}
          </div>
        )}

        {/* ERROR */}

        {error && (
          <div className="mb-6 rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-red-400">
            {error}
          </div>
        )}

        {/* ==================================================
            UPLOAD
        ================================================== */}

        <section className="rounded-2xl border border-slate-700 bg-[#0b1a2b] p-8">

          <h2 className="text-2xl font-bold">
            Upload File
          </h2>

          <p className="mt-2 text-slate-400">
            Add a file to your innovation vault.
          </p>

          <div className="mt-8 grid gap-6 md:grid-cols-2">

            {/* PORTFOLIO */}

            <div>

              <label className="mb-2 block text-sm font-semibold text-slate-400">
                Innovation Portfolio *
              </label>

              <select
                value={
                  selectedPortfolioId
                }
                onChange={(e) =>
                  setSelectedPortfolioId(
                    e.target.value
                  )
                }
                className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
              >

                <option value="">
                  -- Select Portfolio --
                </option>

                {portfolios.map(
                  (portfolio) => (
                    <option
                      key={portfolio.id}
                      value={
                        portfolio.id
                      }
                    >
                      #{portfolio.id} -{" "}
                      {portfolio.title}
                    </option>
                  )
                )}

              </select>

            </div>

            {/* TITLE */}

            <div>

              <label className="mb-2 block text-sm font-semibold text-slate-400">
                Title *
              </label>

              <input
                type="text"
                value={title}
                onChange={(e) =>
                  setTitle(
                    e.target.value
                  )
                }
                placeholder="Enter file title"
                className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
              />

            </div>

            {/* DOCUMENT TYPE */}

            <div>

              <label className="mb-2 block text-sm font-semibold text-slate-400">
                Document Type *
              </label>

              <select
                value={documentType}
                onChange={(e) =>
                  setDocumentType(
                    e.target.value as DocumentType
                  )
                }
                className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
              >

                <option value="">
                  -- Select Type --
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

                <option value="Document">
                  Document
                </option>

                <option value="Image">
                  Image
                </option>

                <option value="Dataset">
                  Dataset
                </option>

              </select>

            </div>

            {/* VISIBILITY */}

            <div>

              <label className="mb-2 block text-sm font-semibold text-slate-400">
                Visibility
              </label>

              <select
                value={visibility}
                onChange={(e) =>
                  setVisibility(
                    e.target.value as Visibility
                  )
                }
                className="w-full rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
              >

                <option value="Private">
                  Private
                </option>

                <option value="Team">
                  Team
                </option>

                <option value="Public">
                  Public
                </option>

              </select>

            </div>

            {/* DESCRIPTION */}

            <div className="md:col-span-2">

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
                rows={5}
                placeholder="Describe this file..."
                className="w-full resize-none rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-white outline-none focus:border-cyan-400"
              />

            </div>

            {/* FILE */}

            <div className="md:col-span-2">

              <label className="mb-2 block text-sm font-semibold text-slate-400">
                Choose File *
              </label>

              <input
                id="vault-file-input"
                type="file"
                onChange={
                  handleFileChange
                }
                className="w-full cursor-pointer rounded-lg border border-slate-600 bg-[#071525] px-4 py-3 text-slate-300 file:mr-4 file:rounded-lg file:border-0 file:bg-cyan-400 file:px-4 file:py-2 file:font-semibold file:text-black"
              />

              {selectedFile && (
                <div className="mt-3 rounded-lg border border-slate-700 bg-[#071525] p-4">

                  <p className="text-sm font-semibold text-cyan-400">
                    Selected File
                  </p>

                  <p className="mt-1 break-all text-white">
                    {selectedFile.name}
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    {formatFileSize(
                      selectedFile.size
                    )}
                  </p>

                </div>
              )}

            </div>

            {/* NDA */}

            <div className="md:col-span-2">

              <label className="flex cursor-pointer items-center gap-3">

                <input
                  type="checkbox"
                  checked={
                    ndaRequired
                  }
                  onChange={(e) =>
                    setNdaRequired(
                      e.target.checked
                    )
                  }
                  className="h-5 w-5 accent-cyan-400"
                />

                <span className="text-sm text-slate-300">
                  NDA Required
                </span>

              </label>

            </div>

          </div>

          {/* BUTTONS */}

          <div className="mt-8 flex gap-4">

            <button
              type="button"
              onClick={handleUpload}
              disabled={uploading}
              className="rounded-lg bg-cyan-500 px-7 py-3 font-semibold text-black hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {uploading
                ? "Uploading..."
                : "Upload File"}
            </button>

            <button
              type="button"
              onClick={
                clearUploadForm
              }
              disabled={uploading}
              className="rounded-lg border border-slate-600 px-7 py-3 font-semibold text-slate-300 hover:border-cyan-400 hover:text-cyan-400"
            >
              Clear
            </button>

          </div>

        </section>

        {/* ==================================================
            VAULT FILES
        ================================================== */}

        <section className="mt-10">

          <div className="mb-6">

            <h2 className="text-3xl font-bold">
              Vault Files
            </h2>

            <p className="mt-2 text-slate-400">
              {files.length} file
              {files.length === 1
                ? ""
                : "s"} stored.
            </p>

          </div>

          {loadingFiles ? (
            <div className="rounded-2xl border border-slate-700 bg-[#0b1a2b] p-10 text-center">

              <p className="text-slate-400">
                Loading files...
              </p>

            </div>
          ) : files.length === 0 ? (
            <div className="rounded-2xl border border-slate-700 bg-[#0b1a2b] p-10 text-center">

              <div className="text-5xl">
                🔐
              </div>

              <h3 className="mt-5 text-2xl font-bold">
                Your Vault is Empty
              </h3>

              <p className="mt-3 text-slate-400">
                Upload your first file above.
              </p>

            </div>
          ) : (
            <div className="grid gap-6 md:grid-cols-2">

              {files.map((file) => (

                <div
                  key={file.id}
                  className="rounded-2xl border border-slate-700 bg-[#0b1a2b] p-6"
                >

                  {/* FILE HEADER */}

                  <div className="flex items-start justify-between gap-4">

                    <div className="flex items-start gap-4">

                      <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-slate-800 text-2xl">
                        {getDocumentIcon(
                          file.document_type
                        )}
                      </div>

                      <div>

                        <h3 className="text-lg font-bold">
                          {file.title}
                        </h3>

                        <p className="mt-1 text-sm text-cyan-400">
                          {file.document_type}
                        </p>

                      </div>

                    </div>

                    <span className="rounded-full border border-slate-600 px-3 py-1 text-xs text-slate-400">
                      {file.visibility}
                    </span>

                  </div>

                  {/* DETAILS */}

                  <div className="mt-6 space-y-4">

                    <Info
                      label="Original Filename"
                      value={
                        file.original_filename
                      }
                    />

                    <Info
                      label="Portfolio ID"
                      value={`#${file.portfolio_id}`}
                    />

                    <Info
                      label="File Size"
                      value={formatFileSize(
                        file.file_size
                      )}
                    />

                    <Info
                      label="MIME Type"
                      value={
                        file.mime_type
                      }
                    />

                    <Info
                      label="Extension"
                      value={
                        file.file_extension
                      }
                    />

                    <Info
                      label="NDA"
                      value={
                        file.nda_required
                          ? "Required"
                          : "Not Required"
                      }
                    />

                    {file.description && (
                      <Info
                        label="Description"
                        value={
                          file.description
                        }
                      />
                    )}

                  </div>

                  {/* ACTIONS */}

                  <div className="mt-6 flex gap-3">

                    <button
                      type="button"
                      onClick={() =>
                        startEdit(file)
                      }
                      className="rounded-lg border border-indigo-400 px-5 py-2 text-sm font-semibold text-indigo-400 hover:bg-indigo-400 hover:text-white"
                    >
                      Update
                    </button>

                    <button
                      type="button"
                      onClick={() =>
                        handleDelete(
                          file.id
                        )
                      }
                      disabled={
                        deletingId ===
                        file.id
                      }
                      className="rounded-lg border border-red-400 px-5 py-2 text-sm font-semibold text-red-400 hover:bg-red-400 hover:text-white disabled:opacity-50"
                    >
                      {deletingId ===
                      file.id
                        ? "Deleting..."
                        : "Delete"}
                    </button>

                  </div>

                  {/* EDIT */}

                  {editingId ===
                    file.id && (
                    <div className="mt-6 rounded-xl border border-indigo-400/30 bg-[#071525] p-5">

                      <h4 className="mb-5 font-bold text-indigo-400">
                        Update File
                      </h4>

                      <div className="mb-4">

                        <label className="mb-2 block text-sm text-slate-400">
                          Title
                        </label>

                        <input
                          type="text"
                          value={
                            editTitle
                          }
                          onChange={(e) =>
                            setEditTitle(
                              e.target.value
                            )
                          }
                          className="w-full rounded-lg border border-slate-600 bg-[#06111f] px-4 py-3 text-white outline-none focus:border-indigo-400"
                        />

                      </div>

                      <div className="mb-4">

                        <label className="mb-2 block text-sm text-slate-400">
                          Description
                        </label>

                        <textarea
                          value={
                            editDescription
                          }
                          onChange={(e) =>
                            setEditDescription(
                              e.target.value
                            )
                          }
                          rows={4}
                          className="w-full resize-none rounded-lg border border-slate-600 bg-[#06111f] px-4 py-3 text-white outline-none focus:border-indigo-400"
                        />

                      </div>

                      <div className="mb-4">

                        <label className="mb-2 block text-sm text-slate-400">
                          Visibility
                        </label>

                        <select
                          value={
                            editVisibility
                          }
                          onChange={(e) =>
                            setEditVisibility(
                              e.target.value as Visibility
                            )
                          }
                          className="w-full rounded-lg border border-slate-600 bg-[#06111f] px-4 py-3 text-white outline-none focus:border-indigo-400"
                        >

                          <option value="Private">
                            Private
                          </option>

                          <option value="Team">
                            Team
                          </option>

                          <option value="Public">
                            Public
                          </option>

                        </select>

                      </div>

                      <label className="mb-5 flex items-center gap-3">

                        <input
                          type="checkbox"
                          checked={
                            editNdaRequired
                          }
                          onChange={(e) =>
                            setEditNdaRequired(
                              e.target.checked
                            )
                          }
                          className="h-5 w-5 accent-indigo-400"
                        />

                        <span className="text-sm text-slate-300">
                          NDA Required
                        </span>

                      </label>

                      <div className="flex gap-3">

                        <button
                          type="button"
                          onClick={() =>
                            handleUpdate(
                              file.id
                            )
                          }
                          disabled={
                            updating
                          }
                          className="rounded-lg bg-indigo-500 px-5 py-2 font-semibold text-white hover:bg-indigo-400 disabled:opacity-50"
                        >
                          {updating
                            ? "Saving..."
                            : "Save Changes"}
                        </button>

                        <button
                          type="button"
                          onClick={
                            cancelEdit
                          }
                          disabled={
                            updating
                          }
                          className="rounded-lg border border-slate-600 px-5 py-2 font-semibold text-slate-300 hover:border-slate-400"
                        >
                          Cancel
                        </button>

                      </div>

                    </div>
                  )}

                </div>

              ))}

            </div>
          )}

        </section>

      </div>

    </main>
  );
}

/*
 * ==================================================
 * INFO COMPONENT
 * ==================================================
 */

function Info({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="border-b border-slate-700 pb-3">

      <p className="text-xs text-slate-500">
        {label}
      </p>

      <p className="mt-1 break-all text-sm text-slate-300">
        {value}
      </p>

    </div>
  );
}