import {
  useEffect,
  useState
} from "react";

import {
  useNavigate
} from "react-router-dom";

import DashboardLayout
  from "../components/DashboardLayout";

import {
  getResearchLibrary,
  removeFromResearchLibrary,
} from "../api/publications";


function ResearchLibrary() {

  const navigate = useNavigate();

  const [
    publications,
    setPublications
  ] = useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  async function loadLibrary() {

    try {

      setLoading(true);

      const data =
        await getResearchLibrary();

      setPublications(
        data.publications || []
      );

    } catch (err) {

      setError(
        "Unable to load research library."
      );

    } finally {

      setLoading(false);
    }
  }


  useEffect(() => {

    loadLibrary();

  }, []);


  async function handleRemove(
    publicationId
  ) {

    try {

      await removeFromResearchLibrary(
        publicationId
      );

      await loadLibrary();

    } catch (err) {

      setError(
        "Unable to remove publication."
      );
    }
  }


  return (

    <DashboardLayout>

      <div className="page-content">

        <button
          className="secondary-button"
          onClick={() =>
            navigate(
              "/profile/publications"
            )
          }
        >
          ← Back to Publications
        </button>


        <div className="page-header">

          <div>

            <div className="eyebrow">
              RESEARCH LIBRARY
            </div>

            <h1>
              Imported Publications
            </h1>

            <p>
              External academic literature
              you discovered through OpenAlex.
              These are not treated as your
              authored publications.
            </p>

          </div>

          <strong>
            {publications.length} saved
          </strong>

        </div>


        {error && (

          <div className="alert error">
            {error}
          </div>

        )}


        {loading ? (

          <p>
            Loading research library...
          </p>

        ) : publications.length === 0 ? (

          <div className="empty-state">

            <h3>
              Your research library is empty
            </h3>

            <p>
              Search for a topic from the
              Publications page and import
              relevant literature from
              OpenAlex.
            </p>

          </div>

        ) : (

          <div className="publication-list">

            {publications.map(
              (publication) => (

                <article
                  className="publication-card"
                  key={publication.id}
                >

                  <div>

                    <span className="publication-type">

                      {
                        publication
                          .publication_type
                        || "Publication"
                      }

                    </span>

                    <span>
                      {" "}OpenAlex
                    </span>

                  </div>


                  <h3>
                    {publication.title}
                  </h3>


                  {publication.authors && (

                    <p>
                      {publication.authors}
                    </p>

                  )}


                  {publication.journal_or_conference && (

                    <p>

                      <strong>
                        Source:
                      </strong>{" "}

                      {
                        publication
                          .journal_or_conference
                      }

                    </p>

                  )}


                  <p>

                    <strong>
                      Citations:
                    </strong>{" "}

                    {
                      publication
                        .citation_count ?? 0
                    }

                  </p>


                  {publication.language && (

                    <p>

                      <strong>
                        Language:
                      </strong>{" "}

                      {publication.language}

                    </p>

                  )}


                  <p>

                    <strong>
                      Open Access:
                    </strong>{" "}

                    {
                      publication
                        .is_open_access
                        ? "Yes"
                        : "No"
                    }

                  </p>


                  <div className="card-actions">

                    {publication.url && (

                      <button
                        onClick={() =>
                          window.open(
                            publication.url,
                            "_blank",
                            "noopener,noreferrer"
                          )
                        }
                      >
                        View Publication
                      </button>

                    )}


                    <button
                      className="danger-button"
                      onClick={() =>
                        handleRemove(
                          publication.id
                        )
                      }
                    >
                      Remove from Library
                    </button>

                  </div>

                </article>

              )
            )}

          </div>

        )}

      </div>

    </DashboardLayout>
  );
}


export default ResearchLibrary;