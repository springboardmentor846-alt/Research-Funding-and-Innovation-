import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  useNavigate
} from "react-router-dom";

import DashboardLayout
  from "../components/DashboardLayout";

import {
  deletePublication,
  getMyPublications,
  uploadPublicationPdf,
  viewPublicationPdf,
} from "../api/publications";


function MyPublications() {

  const navigate =
    useNavigate();

  const fileInputRef =
    useRef(null);


  const [
    publications,
    setPublications
  ] = useState([]);

  const [
    loading,
    setLoading
  ] = useState(true);

  const [
    error,
    setError
  ] = useState("");

  const [
    message,
    setMessage
  ] = useState("");

  const [
    uploadingId,
    setUploadingId
  ] = useState(null);

  const [
    selectedPublicationId,
    setSelectedPublicationId
  ] = useState(null);


  // =========================================================
  // LOAD PUBLICATIONS
  // =========================================================

  async function loadPublications() {

    try {

      setLoading(true);
      setError("");

      const data =
        await getMyPublications();

      setPublications(
        data.publications || []
      );

    } catch (err) {

      console.error(
        "Unable to load publications:",
        err
      );

      setError(
        "Unable to load your publications."
      );

    } finally {

      setLoading(false);
    }
  }


  useEffect(() => {

    loadPublications();

  }, []);


  // =========================================================
  // DELETE PUBLICATION
  // =========================================================

  async function handleDelete(
    publicationId
  ) {

    const confirmed =
      window.confirm(
        "Delete this publication from your profile?"
      );

    if (!confirmed) {
      return;
    }


    try {

      setError("");
      setMessage("");

      await deletePublication(
        publicationId
      );

      setMessage(
        "Publication deleted successfully."
      );

      await loadPublications();

    } catch (err) {

      console.error(
        "Unable to delete publication:",
        err
      );

      setError(
        err.response?.data?.detail ||
        "Unable to delete publication."
      );
    }
  }


  // =========================================================
  // CHOOSE PDF
  // =========================================================

  function handleChoosePdf(
    publicationId
  ) {

    setError("");
    setMessage("");

    setSelectedPublicationId(
      publicationId
    );

    if (fileInputRef.current) {

      fileInputRef.current.value = "";

      fileInputRef.current.click();
    }
  }


  // =========================================================
  // UPLOAD / REPLACE PDF
  // =========================================================

  async function handlePdfSelected(
    event
  ) {

    const file =
      event.target.files?.[0];

    if (
      !file ||
      !selectedPublicationId
    ) {
      return;
    }


    // PDF validation

    if (
      file.type !== "application/pdf"
    ) {

      setError(
        "Only PDF files are allowed."
      );

      event.target.value = "";

      return;
    }


    // 10 MB validation

    const maxSize =
      10 * 1024 * 1024;

    if (
      file.size > maxSize
    ) {

      setError(
        "PDF must be 10 MB or smaller."
      );

      event.target.value = "";

      return;
    }


    try {

      setError("");
      setMessage("");

      setUploadingId(
        selectedPublicationId
      );


      await uploadPublicationPdf(
        selectedPublicationId,
        file
      );


      setMessage(
        "Publication PDF uploaded successfully."
      );


      await loadPublications();

    } catch (err) {

      console.error(
        "Unable to upload PDF:",
        err
      );

      setError(
        err.response?.data?.detail ||
        "Unable to upload publication PDF."
      );

    } finally {

      setUploadingId(null);

      setSelectedPublicationId(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }


  // =========================================================
  // VIEW PDF
  // =========================================================

  async function handleViewPdf(
    publicationId
  ) {

    try {

      setError("");

      await viewPublicationPdf(
        publicationId
      );

    } catch (err) {

      console.error(
        "Unable to open PDF:",
        err
      );

      setError(
        err.response?.data?.detail ||
        "Unable to open publication PDF."
      );
    }
  }


  // =========================================================
  // FORMAT DATE
  // =========================================================

  function formatDate(
    publicationDate
  ) {

    if (!publicationDate) {
      return "Not specified";
    }

    return new Date(
      `${publicationDate}T00:00:00`
    ).toLocaleDateString(
      "en-US",
      {
        year: "numeric",
        month: "short",
        day: "numeric",
      }
    );
  }


  // =========================================================
  // UI
  // =========================================================

  return (

      <div className="page-content">


        {/* ================================================= */}
        {/* HIDDEN PDF INPUT */}
        {/* ================================================= */}

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,application/pdf"
          onChange={handlePdfSelected}
          style={{
            display: "none"
          }}
        />


        {/* ================================================= */}
        {/* HEADER */}
        {/* ================================================= */}

        <div className="my-publications-topbar">

          <div>

            <button
              type="button"
              className="back-link-button"
              onClick={() =>
                navigate(
                  "/profile/publications"
                )
              }
            >
              ← Publications
            </button>


            <div className="eyebrow">

              RESEARCH OUTPUTS

            </div>


            <h1>

              My Publications

            </h1>


            <p>

              Manage publications authored by
              you and connected to your
              researcher profile.

            </p>

          </div>


          <div className="publication-count-box">

            <span>

              TOTAL PUBLICATIONS

            </span>

            <strong>

              {publications.length}

            </strong>

          </div>

        </div>


        {/* ================================================= */}
        {/* MESSAGE */}
        {/* ================================================= */}

        {message && (

          <div className="alert success">

            {message}

          </div>

        )}


        {/* ================================================= */}
        {/* ERROR */}
        {/* ================================================= */}

        {error && (

          <div className="alert error">

            {error}

          </div>

        )}


        {/* ================================================= */}
        {/* LOADING */}
        {/* ================================================= */}

        {loading ? (

          <div className="publications-loading">

            <p>
              Loading your publications...
            </p>

          </div>

        ) : publications.length === 0 ? (


          /* ================================================= */
          /* EMPTY STATE */
          /* ================================================= */

          <div className="publications-empty-state">

            <div className="empty-document-icon">

              PDF

            </div>

            <h2>

              No publications yet

            </h2>

            <p>

              Add your authored research work
              from the Publications page.

            </p>

            <button
              type="button"
              className="primary-button"
              onClick={() =>
                navigate(
                  "/profile/publications"
                )
              }
            >

              Add Publication

            </button>

          </div>

        ) : (


          /* ================================================= */
          /* PUBLICATION GRID */
          /* ================================================= */

          <div className="my-publication-grid">

            {publications.map(
              (publication) => (

                <article
                  className="my-publication-card"
                  key={publication.id}
                >


                  {/* ======================================= */}
                  {/* CARD HEADER */}
                  {/* ======================================= */}

                  <div className="publication-card-top">

                    <span className="publication-type">

                      {
                        publication.publication_type ||
                        "Publication"
                      }

                    </span>


                    {publication.pdf_path ? (

                      <span className="pdf-status available">

                        PDF AVAILABLE

                      </span>

                    ) : (

                      <span className="pdf-status unavailable">

                        NO PDF

                      </span>

                    )}

                  </div>


                  {/* ======================================= */}
                  {/* TITLE */}
                  {/* ======================================= */}

                  <h2 className="publication-card-title">

                    {publication.title}

                  </h2>


                  {/* ======================================= */}
                  {/* AUTHORS */}
                  {/* ======================================= */}

                  {publication.authors && (

                    <p className="publication-authors">

                      {publication.authors}

                    </p>

                  )}


                  {/* ======================================= */}
                  {/* PUBLICATION DETAILS */}
                  {/* ======================================= */}

                  <div className="publication-details">


                    {publication.journal_or_conference && (

                      <div className="publication-detail">

                        <span>
                          SOURCE
                        </span>

                        <strong>

                          {
                            publication
                              .journal_or_conference
                          }

                        </strong>

                      </div>

                    )}


                    {publication.publisher && (

                      <div className="publication-detail">

                        <span>
                          PUBLISHER
                        </span>

                        <strong>

                          {publication.publisher}

                        </strong>

                      </div>

                    )}


                    <div className="publication-detail">

                      <span>
                        PUBLISHED
                      </span>

                      <strong>

                        {
                          formatDate(
                            publication
                              .publication_date
                          )
                        }

                      </strong>

                    </div>


                    {publication.doi && (

                      <div className="publication-detail">

                        <span>
                          DOI
                        </span>

                        <strong>

                          {publication.doi}

                        </strong>

                      </div>

                    )}

                  </div>


                  {/* ======================================= */}
                  {/* ABSTRACT */}
                  {/* ======================================= */}

                  {publication.abstract && (

                    <div className="publication-abstract">

                      <span>
                        ABSTRACT
                      </span>

                      <p>

                        {publication.abstract}

                      </p>

                    </div>

                  )}


                  {/* ======================================= */}
                  {/* PDF PANEL */}
                  {/* ======================================= */}

                  <div
                    className={
                      publication.pdf_path
                        ? "publication-pdf-panel has-pdf"
                        : "publication-pdf-panel"
                    }
                  >

                    <div>

                      <strong>

                        {
                          publication.pdf_path
                            ? "Full-text PDF attached"
                            : "No PDF attached"
                        }

                      </strong>

                      <p>

                        {
                          publication.pdf_path
                            ? "The full publication document is available."
                            : "Attach the full-text publication document if available."
                        }

                      </p>

                    </div>


                    {publication.pdf_path ? (

                      <div className="pdf-buttons">


                        {/* VIEW PDF */}

                        <button
                          type="button"
                          className="primary-button small"
                          onClick={() =>
                            handleViewPdf(
                              publication.id
                            )
                          }
                        >

                          View PDF

                        </button>


                        {/* REPLACE PDF */}

                        <button
                          type="button"
                          className="secondary-button small"
                          disabled={
                            uploadingId ===
                            publication.id
                          }
                          onClick={() =>
                            handleChoosePdf(
                              publication.id
                            )
                          }
                        >

                          {
                            uploadingId ===
                            publication.id
                              ? "Uploading..."
                              : "Replace PDF"
                          }

                        </button>

                      </div>

                    ) : (


                      /* UPLOAD PDF */

                      <button
                        type="button"
                        className="secondary-button small"
                        disabled={
                          uploadingId ===
                          publication.id
                        }
                        onClick={() =>
                          handleChoosePdf(
                            publication.id
                          )
                        }
                      >

                        {
                          uploadingId ===
                          publication.id
                            ? "Uploading..."
                            : "Upload PDF"
                        }

                      </button>

                    )}

                  </div>


                  {/* ======================================= */}
                  {/* CARD FOOTER */}
                  {/* ======================================= */}

                  <div className="publication-card-footer">

                    <div>

                      {publication.url && (

                        <button
                          type="button"
                          className="text-action-button"
                          onClick={() =>
                            window.open(
                              publication.url,
                              "_blank",
                              "noopener,noreferrer"
                            )
                          }
                        >

                          External Publication ↗

                        </button>

                      )}

                    </div>


                    <button
                      type="button"
                      className="danger-button"
                      onClick={() =>
                        handleDelete(
                          publication.id
                        )
                      }
                    >

                      Delete

                    </button>

                  </div>

                </article>

              )
            )}

          </div>

        )}

      </div>

  );
}


export default MyPublications;