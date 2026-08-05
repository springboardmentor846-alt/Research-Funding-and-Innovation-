import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import DashboardLayout from "../../components/researcher/ResearcherLayout";

import {
  createPublication,
  getMyPublications,
  getResearchLibrary,
  importOpenAlexPublications,
  uploadPublicationPdf,
} from "../../api/researcher/publications";


function Publications() {
  const navigate = useNavigate();

  // ============================================================
  // COUNTS
  // ============================================================

  const [myPublicationCount, setMyPublicationCount] = useState(0);
  const [libraryCount, setLibraryCount] = useState(0);

  const [loadingCounts, setLoadingCounts] = useState(true);


  // ============================================================
  // OPENALEX DISCOVERY
  // ============================================================

  const [researchTopic, setResearchTopic] = useState("");
  const [publicationLimit, setPublicationLimit] = useState(10);
  const [importing, setImporting] = useState(false);


  // ============================================================
  // MANUAL PUBLICATION FORM
  // ============================================================

  const [formData, setFormData] = useState({
    title: "",
    publication_type: "",
    publication_date: "",
    authors: "",
    publisher: "",
    journal_or_conference: "",
    doi: "",
    url: "",
    abstract: "",
  });

  const [pdfFile, setPdfFile] = useState(null);

  const [submitting, setSubmitting] = useState(false);


  // ============================================================
  // MESSAGES
  // ============================================================

  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");


  // ============================================================
  // LOAD COUNTS
  // ============================================================

  async function loadCounts() {
    try {
      setLoadingCounts(true);

      const [
        myPublicationsData,
        researchLibraryData,
      ] = await Promise.all([
        getMyPublications(),
        getResearchLibrary(),
      ]);

      setMyPublicationCount(
        myPublicationsData?.publications?.length || 0
      );

      setLibraryCount(
        researchLibraryData?.publications?.length || 0
      );

    } catch (err) {
      console.error(
        "Unable to load publication counts:",
        err
      );

      setError(
        "Unable to load publication information."
      );

    } finally {
      setLoadingCounts(false);
    }
  }


  useEffect(() => {
    loadCounts();
  }, []);


  // ============================================================
  // CLEAR MESSAGES
  // ============================================================

  function clearMessages() {
    setSuccess("");
    setError("");
  }


  // ============================================================
  // FORM INPUT
  // ============================================================

  function handleChange(event) {
    const {
      name,
      value,
    } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  }


  // ============================================================
  // PDF INPUT
  // ============================================================

  function handlePdfChange(event) {
    clearMessages();

    const file = event.target.files?.[0];

    if (!file) {
      setPdfFile(null);
      return;
    }

    if (file.type !== "application/pdf") {
      setError(
        "Please select a valid PDF document."
      );

      event.target.value = "";
      setPdfFile(null);

      return;
    }

    // 10 MB limit
    const maxSize =
      10 * 1024 * 1024;

    if (file.size > maxSize) {
      setError(
        "PDF file must be smaller than 10 MB."
      );

      event.target.value = "";
      setPdfFile(null);

      return;
    }

    setPdfFile(file);
  }


  // ============================================================
  // OPENALEX IMPORT
  // ============================================================

  async function handleOpenAlexImport(event) {
    event.preventDefault();

    clearMessages();

    const topic =
      researchTopic.trim();

    if (!topic) {
      setError(
        "Enter a research topic before searching OpenAlex."
      );

      return;
    }

    try {
      setImporting(true);

      const result =
        await importOpenAlexPublications(
          topic,
          Number(publicationLimit)
        );

      const added =
        result?.added ??
        result?.imported ??
        result?.created ??
        0;

      const existing =
        result?.already_saved ??
        result?.existing ??
        result?.skipped ??
        0;

      if (result?.message) {
        setSuccess(result.message);
      } else {
        setSuccess(
          `${added} publication(s) added to your Research Library.` +
          (existing
            ? ` ${existing} already saved.`
            : "")
        );
      }

      setResearchTopic("");

      await loadCounts();

    } catch (err) {
      console.error(
        "OpenAlex import failed:",
        err
      );

      const detail =
        err?.response?.data?.detail;

      if (typeof detail === "string") {
        setError(detail);
      } else {
        setError(
          "Unable to search OpenAlex. Please try again."
        );
      }

    } finally {
      setImporting(false);
    }
  }


  // ============================================================
  // ADD MY PUBLICATION
  // ============================================================

  async function handleSubmit(event) {
    event.preventDefault();

    clearMessages();

    if (!formData.title.trim()) {
      setError(
        "Publication title is required."
      );

      return;
    }

    try {
      setSubmitting(true);

      // --------------------------------------------------------
      // Clean request payload
      // --------------------------------------------------------

      const payload = {
        title: formData.title.trim(),

        publication_type:
          formData.publication_type || null,

        publication_date:
          formData.publication_date || null,

        authors:
          formData.authors.trim() || null,

        publisher:
          formData.publisher.trim() || null,

        journal_or_conference:
          formData.journal_or_conference.trim() || null,

        doi:
          formData.doi.trim() || null,

        url:
          formData.url.trim() || null,

        abstract:
          formData.abstract.trim() || null,
      };


      // --------------------------------------------------------
      // First create publication
      // --------------------------------------------------------

      const createdPublication =
        await createPublication(payload);


      // --------------------------------------------------------
      // Determine publication ID
      // --------------------------------------------------------

      const publicationId =
        createdPublication?.id ||
        createdPublication?.publication?.id;


      if (!publicationId) {
        throw new Error(
          "Publication was created but no publication ID was returned."
        );
      }


      // --------------------------------------------------------
      // Upload PDF if selected
      // --------------------------------------------------------

      if (pdfFile) {
        await uploadPublicationPdf(
          publicationId,
          pdfFile
        );
      }


      // --------------------------------------------------------
      // Success
      // --------------------------------------------------------

      if (pdfFile) {
        setSuccess(
          "Publication and PDF added successfully."
        );
      } else {
        setSuccess(
          "Publication added successfully."
        );
      }


      // --------------------------------------------------------
      // Reset form
      // --------------------------------------------------------

      setFormData({
        title: "",
        publication_type: "",
        publication_date: "",
        authors: "",
        publisher: "",
        journal_or_conference: "",
        doi: "",
        url: "",
        abstract: "",
      });

      setPdfFile(null);

      const pdfInput =
        document.getElementById(
          "publication-pdf"
        );

      if (pdfInput) {
        pdfInput.value = "";
      }

      await loadCounts();

    } catch (err) {
      console.error(
        "Publication creation failed:",
        err
      );

      const detail =
        err?.response?.data?.detail;

      if (typeof detail === "string") {
        setError(detail);
      } else {
        setError(
          "Unable to add publication. Please check the entered information and try again."
        );
      }

    } finally {
      setSubmitting(false);
    }
  }


  // ============================================================
  // PAGE
  // ============================================================

  return (

      <main className="publications-page">

        {/* ====================================================
            PAGE HEADER
        ==================================================== */}

        <section className="publications-header">

          <div>

            <div className="publications-eyebrow">
              RESEARCH OUTPUTS
            </div>

            <h1>
              Publications
            </h1>

            <p>
              Build your scholarly record, manage your
              publications, and discover relevant academic
              literature through OpenAlex.
            </p>

          </div>

        </section>


        {/* ====================================================
            ALERTS
        ==================================================== */}

        {success && (
          <div className="publication-alert success">
            {success}
          </div>
        )}


        {error && (
          <div className="publication-alert error">
            {error}
          </div>
        )}


        {/* ====================================================
            PUBLICATION STATISTICS
        ==================================================== */}

        <section className="publication-stats">

          {/* MY PUBLICATIONS */}

          <article className="publication-stat-card">

            <div className="publication-stat-top">

              <div>

                <span className="publication-stat-label">
                  MY PUBLICATIONS
                </span>

                <h2>
                  {loadingCounts
                    ? "—"
                    : myPublicationCount}
                </h2>

              </div>

              <div className="publication-stat-icon">
                📄
              </div>

            </div>


            <p>
              Scholarly publications authored by you and
              connected to your researcher profile.
            </p>


            <button
              type="button"
              className="publication-secondary-button"
              onClick={() =>
                navigate(
                  "/profile/publications/mine"
                )
              }
            >
              View My Publications
            </button>

          </article>


          {/* RESEARCH LIBRARY */}

          <article className="publication-stat-card">

            <div className="publication-stat-top">

              <div>

                <span className="publication-stat-label">
                  RESEARCH LIBRARY
                </span>

                <h2>
                  {loadingCounts
                    ? "—"
                    : libraryCount}
                </h2>

              </div>

              <div className="publication-stat-icon">
                📚
              </div>

            </div>


            <p>
              External academic literature discovered and
              saved from OpenAlex.
            </p>


            <button
              type="button"
              className="publication-secondary-button"
              onClick={() =>
                navigate(
                  "/profile/publications/library"
                )
              }
            >
              View Research Library
            </button>

          </article>

        </section>


        {/* ====================================================
            DISCOVER PUBLICATIONS
        ==================================================== */}

        <section className="publication-section">

          <div className="publication-section-header">

            <div>

              <span className="publication-section-kicker">
                ACADEMIC DISCOVERY
              </span>

              <h2>
                Discover Academic Literature
              </h2>

              <p>
                Search OpenAlex by research topic and save
                relevant publications to your personal
                research library.
              </p>

            </div>

          </div>


          <form
            onSubmit={handleOpenAlexImport}
          >

            <div className="publication-discovery-grid">

              <div className="publication-form-group">

                <label htmlFor="research-topic">
                  Research Topic
                </label>

                <input
                  id="research-topic"
                  type="text"
                  value={researchTopic}
                  onChange={(event) =>
                    setResearchTopic(
                      event.target.value
                    )
                  }
                  placeholder="e.g. Quantum Computing"
                />

              </div>


              <div className="publication-form-group">

                <label htmlFor="publication-limit">
                  Number of Results
                </label>

                <select
                  id="publication-limit"
                  value={publicationLimit}
                  onChange={(event) =>
                    setPublicationLimit(
                      Number(
                        event.target.value
                      )
                    )
                  }
                >
                  <option value={5}>
                    5 publications
                  </option>

                  <option value={10}>
                    10 publications
                  </option>

                  <option value={15}>
                    15 publications
                  </option>

                  <option value={20}>
                    20 publications
                  </option>

                  <option value={25}>
                    25 publications
                  </option>

                  <option value={50}>
                    50 publications
                  </option>
                </select>

              </div>

            </div>


            <div className="publication-discovery-action">

              <button
                type="submit"
                className="publication-primary-button"
                disabled={importing}
              >
                {importing
                  ? "Searching OpenAlex..."
                  : "Search & Add to Library"}
              </button>

            </div>

          </form>

        </section>


        {/* ====================================================
            ADD MY PUBLICATION
        ==================================================== */}

        <section className="publication-section">

          <div className="publication-section-header">

            <div>

              <span className="publication-section-kicker">
                SCHOLARLY RECORD
              </span>

              <h2>
                Add My Publication
              </h2>

              <p>
                Add a publication that you authored.
                You can also attach the full-text PDF
                to your publication record.
              </p>

            </div>

          </div>


          <form
            onSubmit={handleSubmit}
          >

            <div className="publication-form-grid">

              {/* TITLE */}

              <div className="publication-form-group publication-full-width">

                <label htmlFor="title">
                  Publication Title
                  <span className="required">
                    *
                  </span>
                </label>

                <input
                  id="title"
                  name="title"
                  type="text"
                  value={formData.title}
                  onChange={handleChange}
                  placeholder="Enter the complete publication title"
                  required
                />

              </div>


              {/* TYPE */}

              <div className="publication-form-group">

                <label htmlFor="publication_type">
                  Publication Type
                </label>

                <select
                  id="publication_type"
                  name="publication_type"
                  value={
                    formData.publication_type
                  }
                  onChange={handleChange}
                >
                  <option value="">
                    Select publication type
                  </option>

                  <option value="article">
                    Journal Article
                  </option>

                  <option value="conference-paper">
                    Conference Paper
                  </option>

                  <option value="book">
                    Book
                  </option>

                  <option value="book-chapter">
                    Book Chapter
                  </option>

                  <option value="preprint">
                    Preprint
                  </option>

                  <option value="thesis">
                    Thesis
                  </option>

                  <option value="report">
                    Research Report
                  </option>

                  <option value="other">
                    Other
                  </option>
                </select>

              </div>


              {/* DATE */}

              <div className="publication-form-group">

                <label htmlFor="publication_date">
                  Publication Date
                </label>

                <input
                  id="publication_date"
                  name="publication_date"
                  type="date"
                  value={
                    formData.publication_date
                  }
                  onChange={handleChange}
                />

              </div>


              {/* AUTHORS */}

              <div className="publication-form-group">

                <label htmlFor="authors">
                  Authors
                </label>

                <input
                  id="authors"
                  name="authors"
                  type="text"
                  value={formData.authors}
                  onChange={handleChange}
                  placeholder="e.g. A. Sharma, R. Kumar"
                />

              </div>


              {/* PUBLISHER */}

              <div className="publication-form-group">

                <label htmlFor="publisher">
                  Publisher
                </label>

                <input
                  id="publisher"
                  name="publisher"
                  type="text"
                  value={formData.publisher}
                  onChange={handleChange}
                  placeholder="Publisher name"
                />

              </div>


              {/* JOURNAL */}

              <div className="publication-form-group">

                <label htmlFor="journal_or_conference">
                  Journal / Conference
                </label>

                <input
                  id="journal_or_conference"
                  name="journal_or_conference"
                  type="text"
                  value={
                    formData.journal_or_conference
                  }
                  onChange={handleChange}
                  placeholder="Journal or conference name"
                />

              </div>


              {/* DOI */}

              <div className="publication-form-group">

                <label htmlFor="doi">
                  DOI
                  <span className="optional-label">
                    Optional
                  </span>
                </label>

                <input
                  id="doi"
                  name="doi"
                  type="text"
                  value={formData.doi}
                  onChange={handleChange}
                  placeholder="10.xxxx/xxxxx"
                />

              </div>


              {/* URL */}

              <div className="publication-form-group publication-full-width">

                <label htmlFor="url">
                  Publication URL
                  <span className="optional-label">
                    Optional
                  </span>
                </label>

                <input
                  id="url"
                  name="url"
                  type="url"
                  value={formData.url}
                  onChange={handleChange}
                  placeholder="https://..."
                />

              </div>


              {/* ABSTRACT */}

              <div className="publication-form-group publication-full-width">

                <label htmlFor="abstract">
                  Abstract
                </label>

                <textarea
                  id="abstract"
                  name="abstract"
                  value={formData.abstract}
                  onChange={handleChange}
                  rows={6}
                  placeholder="Provide a concise abstract or summary of the publication..."
                />

              </div>


              {/* PDF */}

              <div className="publication-form-group publication-full-width">

                <label>
                  Full-text Document
                  <span className="optional-label">
                    Optional
                  </span>
                </label>


                <div className="publication-pdf-upload">

                  <div className="publication-pdf-icon">
                    PDF
                  </div>


                  <div className="publication-pdf-content">

                    <strong>
                      Attach publication PDF
                    </strong>

                    <p>
                      Select the full-text PDF
                      from your computer.
                      Maximum file size: 10 MB.
                    </p>


                    <input
                      id="publication-pdf"
                      type="file"
                      accept=".pdf,application/pdf"
                      onChange={
                        handlePdfChange
                      }
                    />


                    {pdfFile && (

                      <div className="publication-selected-file">

                        <span>
                          Selected:
                        </span>

                        <strong>
                          {pdfFile.name}
                        </strong>

                      </div>

                    )}

                  </div>

                </div>

              </div>

            </div>


            {/* ==================================================
                FORM ACTIONS
            ================================================== */}

            <div className="publication-form-actions">

              <div className="publication-form-note">

                <strong>
                  Personal scholarly record
                </strong>

                <span>
                  This publication will appear
                  under My Publications.
                </span>

              </div>


              <button
                type="submit"
                className="publication-primary-button"
                disabled={submitting}
              >
                {submitting
                  ? pdfFile
                    ? "Adding & Uploading PDF..."
                    : "Adding Publication..."
                  : "Add Publication"}
              </button>

            </div>

          </form>

        </section>

      </main>

  );
}


export default Publications;