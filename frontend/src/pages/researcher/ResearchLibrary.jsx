import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getResearchLibrary,
  removeFromResearchLibrary,
} from "../../api/researcher/publications";

function ResearchLibrary() {
  const navigate = useNavigate();

  const [publications, setPublications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [removingId, setRemovingId] = useState(null);

  async function loadLibrary() {
    try {
      setLoading(true);
      setError("");

      const data = await getResearchLibrary();

      setPublications(data?.publications || []);
    } catch (err) {
      console.error("Research library error:", err);

      setError(
        err?.response?.data?.detail ||
          "Unable to load research library."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadLibrary();
  }, []);

  async function handleRemove(publicationId) {
    try {
      setRemovingId(publicationId);
      setError("");

      await removeFromResearchLibrary(publicationId);

      await loadLibrary();
    } catch (err) {
      console.error("Remove publication error:", err);

      setError(
        err?.response?.data?.detail ||
          "Unable to remove publication."
      );
    } finally {
      setRemovingId(null);
    }
  }

  function openPublication(url) {
    if (!url) return;

    window.open(
      url,
      "_blank",
      "noopener,noreferrer"
    );
  }

  return (
    <div className="research-library-page">

      {/* BACK */}
      <button
        type="button"
        className="back-link-button"
        onClick={() =>
          navigate("/profile/publications")
        }
      >
        ← Publications
      </button>

      {/* HEADER */}
      <div className="my-publications-topbar">

        <div>
          <div className="publications-eyebrow">
            RESEARCH LIBRARY
          </div>

          <h1>
            Imported Publications
          </h1>

          <p>
            External academic literature discovered
            through OpenAlex and saved to your
            research library.
          </p>
        </div>

        <div className="publication-count-box">
          <span>
            SAVED PUBLICATIONS
          </span>

          <strong>
            {loading ? "—" : publications.length}
          </strong>
        </div>

      </div>

      {/* ERROR */}
      {error && (
        <div className="publication-alert error">
          {error}
        </div>
      )}

      {/* LOADING */}
      {loading ? (

        <div className="publications-loading">
          Loading research library...
        </div>

      ) : publications.length === 0 ? (

        /* EMPTY */
        <div className="publications-empty-state">

          <div className="empty-document-icon">
            LIBRARY
          </div>

          <h2>
            Your research library is empty
          </h2>

          <p>
            Search for a topic from the Publications
            page and import relevant academic
            literature from OpenAlex.
          </p>

          <button
            type="button"
            className="primary-button"
            onClick={() =>
              navigate("/profile/publications")
            }
          >
            Discover Publications
          </button>

        </div>

      ) : (

        /* PUBLICATIONS */
        <div className="publication-list">

          {publications.map((publication) => (

            <article
              className="publication-card"
              key={publication.id}
            >

              {/* TOP */}
              <div className="publication-card-top">

                <span className="publication-type">
                  {publication.publication_type ||
                    "Publication"}
                </span>

                <span className="pdf-status available">
                  OPENALEX
                </span>

              </div>

              {/* TITLE */}
              <h3 className="publication-card-title">
                {publication.title}
              </h3>

              {/* AUTHORS */}
              {publication.authors && (
                <p className="publication-authors">
                  {publication.authors}
                </p>
              )}

              {/* DETAILS */}
              <div className="publication-details">

                <div className="publication-detail">
                  <span>
                    SOURCE
                  </span>

                  <strong>
                    {publication.journal_or_conference ||
                      "OpenAlex"}
                  </strong>
                </div>

                <div className="publication-detail">
                  <span>
                    CITATIONS
                  </span>

                  <strong>
                    {publication.citation_count ?? 0}
                  </strong>
                </div>

                {publication.language && (
                  <div className="publication-detail">
                    <span>
                      LANGUAGE
                    </span>

                    <strong>
                      {publication.language}
                    </strong>
                  </div>
                )}

                <div className="publication-detail">
                  <span>
                    OPEN ACCESS
                  </span>

                  <strong>
                    {publication.is_open_access
                      ? "Yes"
                      : "No"}
                  </strong>
                </div>

              </div>

              {/* ABSTRACT */}
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

              {/* ACTIONS */}
              <div className="card-actions">

                {publication.url && (
                  <button
                    type="button"
                    onClick={() =>
                      openPublication(
                        publication.url
                      )
                    }
                  >
                    View Publication ↗
                  </button>
                )}

                <button
                  type="button"
                  className="danger-button"
                  disabled={
                    removingId === publication.id
                  }
                  onClick={() =>
                    handleRemove(
                      publication.id
                    )
                  }
                >
                  {removingId === publication.id
                    ? "Removing..."
                    : "Remove from Library"}
                </button>

              </div>

            </article>

          ))}

        </div>

      )}

    </div>
  );
}

export default ResearchLibrary;