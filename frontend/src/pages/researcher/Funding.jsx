import {
  useEffect,
  useState
} from "react";

import {
  useNavigate
} from "react-router-dom";

import {
  getFundingRecommendations,
  getFundingAlerts
} from "../../api/researcher/funding";


function Funding() {

  const navigate = useNavigate();

  const [funding, setFunding] =
    useState([]);

  const [alerts, setAlerts] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [lastUpdated, setLastUpdated] =
    useState(null);

  const [error, setError] =
    useState("");


  // ==========================================================
  // INITIAL LOAD
  // ==========================================================

  useEffect(() => {

    loadRecommendations();
    loadAlerts();

  }, []);


  // ==========================================================
  // LOAD PERSONALIZED RECOMMENDATIONS
  // ==========================================================

  async function loadRecommendations() {

    try {

      setLoading(true);
      setError("");

      const data =
        await getFundingRecommendations();

      setFunding(
        data.recommendations || []
      );

      setLastUpdated(new Date());

    } catch (error) {

      console.error(error);

      setError(
        error.response?.data?.detail ||
        "Failed to load funding recommendations."
      );

    } finally {

      setLoading(false);

    }

  }


  // ==========================================================
  // LOAD FUNDING ALERTS
  // ==========================================================

  async function loadAlerts() {

    try {

      const data =
        await getFundingAlerts(30);

      setAlerts(
        data.alerts || []
      );

    } catch (error) {

      console.error(
        "Failed to load funding alerts:",
        error
      );

    }

  }


  // ==========================================================
  // RELEVANCE BADGE
  // ==========================================================

  function getRelevanceClass(level) {

    if (level === "Highly Relevant") {

      return "bg-success";

    }

    if (level === "Relevant") {

      return "bg-primary";

    }

    if (level === "Moderate Match") {

      return "bg-warning text-dark";

    }

    return "bg-secondary";

  }


  // ==========================================================
  // ELIGIBILITY BADGE
  // ==========================================================

  function getEligibilityClass(status) {

    if (status === "Eligible") {

      return "bg-success";

    }

    if (
      status === "Potentially Eligible"
    ) {

      return "bg-warning text-dark";

    }

    if (status === "Not Eligible") {

      return "bg-danger";

    }

    return "bg-secondary";

  }


  return (

    <div className="module-page">


      {/* ======================================================
          PAGE HEADER
      ====================================================== */}

      <div className="module-page-header mb-4">

        <div>

          <span className="module-eyebrow">

            PERSONALIZED FUNDING DISCOVERY

          </span>

          <h1>

            Recommended Funding Opportunities

          </h1>

          <p>

            Discover funding opportunities ranked
            according to their relevance to your
            research profile, domains, keywords and
            technology areas.

          </p>

        </div>

      </div>


      {/* ======================================================
          LIVE FUNDING SOURCES
      ====================================================== */}

      <div className="card shadow-sm mb-4">

        <div className="card-body">

          <div className="d-flex justify-content-between align-items-center flex-wrap gap-3">

            <div>

              <h5 className="mb-1">

                Live Funding Discovery

              </h5>

              <p className="text-muted mb-2">

                Current opportunities are fetched from multiple
                Indian and international funding sources and ranked
                according to your research profile.

              </p>

              {lastUpdated && (

                <div className="small text-muted mb-2">

                  Last refreshed: {lastUpdated.toLocaleTimeString()}

                </div>

              )}

              <div className="d-flex flex-wrap gap-2">

                <span className="badge bg-light text-dark border">

                  🇮🇳 ANRF

                </span>

                <span className="badge bg-light text-dark border">

                  🇮🇳 DBT

                </span>

                <span className="badge bg-light text-dark border">

                  🇮🇳 ICMR

                </span>

                <span className="badge bg-light text-dark border">

                  🇮🇳 BIRAC

                </span>

                <span className="badge bg-light text-dark border">

                  🇺🇸 Grants.gov

                </span>

                <span className="badge bg-light text-dark border">

                  🇪🇺 Horizon Europe

                </span>

                <span className="badge bg-light text-dark border">

                  🇬🇧 UKRI

                </span>

                <span className="badge bg-light text-dark border">

                  🌍 Wellcome

                </span>

              </div>

            </div>

            <button

              className="btn btn-outline-primary"

              onClick={() => {
                loadRecommendations();
                loadAlerts();
              }}

              disabled={loading}

            >

              ↻ Refresh Opportunities

            </button>

          </div>

        </div>

      </div>


      {/* ======================================================
          ERROR
      ====================================================== */}

      {error && (

        <div
          className=
            "alert alert-danger mb-4"
        >

          {error}

        </div>

      )}


      {/* ======================================================
          FUNDING ALERTS
      ====================================================== */}

      {alerts.length > 0 && (

        <div className="card shadow-sm mb-4">

          <div className="card-body">

            <div
              className=
                "d-flex justify-content-between align-items-center mb-3"
            >

              <div>

                <h4 className="mb-1">

                  🔔 Upcoming Funding Deadlines

                </h4>

                <p className="text-muted mb-0">

                  Opportunities closing within
                  the next 30 days.

                </p>

              </div>

              <span className="badge bg-danger">

                {alerts.length}

              </span>

            </div>


            {alerts.map((alert) => (

              <div

                key={alert.id}

                className=
                  "border-top py-3"

              >

                <div
                  className=
                    "d-flex justify-content-between align-items-start"
                >

                  <div>

                    <strong>

                      {alert.title}

                    </strong>

                    <div className="text-muted">

                      {alert.organization}

                    </div>

                  </div>

                  <span
                    className=
                      "badge bg-warning text-dark"
                  >

                    {alert.days_remaining}
                    {" "}
                    days remaining

                  </span>

                </div>

              </div>

            ))}

          </div>

        </div>

      )}


      {/* ======================================================
          RECOMMENDATIONS TITLE
      ====================================================== */}

      <div className="mb-3">

        <h4>

          Personalized Recommendations

        </h4>

        <p className="text-muted mb-0">

          Ranked using your research domains, keywords,
          technology areas and profile details.

        </p>

      </div>


      {/* ======================================================
          LOADING
      ====================================================== */}

      {loading && (

        <div
          className=
            "text-center my-5"
        >

          <div
            className=
              "spinner-border text-primary"
          >
          </div>

          <div className="mt-3">

            Finding funding opportunities...

          </div>

        </div>

      )}


      {/* ======================================================
          NO RESULTS
      ====================================================== */}

      {!loading &&
       funding.length === 0 && (

        <div
          className=
            "alert alert-info"
        >

          No funding recommendations are currently available.

        </div>

      )}


      {/* ======================================================
          FUNDING CARDS
      ====================================================== */}

      {!loading && (

        <div className="row">

          {funding.map((item) => (

            <div

              key={item.id}

              className=
                "col-md-6 col-xl-4 mb-4"

            >

              <div
                className=
                  "card h-100 shadow-sm border-0"
              >

                <div className="card-body">


                  {/* ==========================================
                      RELEVANCE
                  ========================================== */}

                  {item.relevance_level && (

                    <div
                      className=
                        "d-flex justify-content-between align-items-center mb-3"
                    >

                      <span
                        className={
                          `badge ${
                            getRelevanceClass(
                              item.relevance_level
                            )
                          }`
                        }
                      >

                        {item.relevance_level}

                      </span>

                      <span
                        className=
                          "badge bg-light text-primary border"
                      >

                        {item.relevance_score}%
                        {" "}
                        Match

                      </span>

                    </div>

                  )}


                  {/* ==========================================
                      TITLE
                  ========================================== */}

                  <h4 className="mb-4">

                    {item.title}

                  </h4>


                  {/* ==========================================
                      ORGANIZATION
                  ========================================== */}

                  <div className="mb-3">

                    <strong>

                      Organization

                    </strong>

                    <div>

                      {item.organization ||
                       "Not specified"}

                    </div>

                  </div>


                  {/* ==========================================
                      RESEARCH DOMAIN
                  ========================================== */}

                  {item.research_domain && (

                    <div className="mb-3">

                      <strong>

                        Research Domain

                      </strong>

                      <div>

                        {item.research_domain}

                      </div>

                    </div>

                  )}


                  {/* ==========================================
                      FUNDING TYPE
                  ========================================== */}

                  {item.funding_type && (

                    <div className="mb-3">

                      <strong>

                        Funding Type

                      </strong>

                      <div>

                        {item.funding_type}

                      </div>

                    </div>

                  )}


                  {/* ==========================================
                      FUNDING AMOUNT
                  ========================================== */}

                  {item.funding_amount && (

                    <div className="mb-3">

                      <strong>

                        Funding Amount

                      </strong>

                      <div>

                        {item.funding_amount}

                      </div>

                    </div>

                  )}


                  {/* ==========================================
                      COUNTRY
                  ========================================== */}

                  {item.country && (

                    <div className="mb-3">

                      <strong>

                        Country

                      </strong>

                      <div>

                        {item.country}

                      </div>

                    </div>

                  )}


                  {/* ==========================================
                      DEADLINE
                  ========================================== */}

                  {item.deadline && (

                    <div className="mb-3">

                      <strong>

                        Deadline

                      </strong>

                      <div>

                        {item.deadline}

                      </div>

                    </div>

                  )}


                  {/* ==========================================
                      CAREER STAGE
                  ========================================== */}

                  {item.career_stage && (

                    <div className="mb-3">

                      <strong>

                        Career Stage

                      </strong>

                      <div>

                        {item.career_stage}

                      </div>

                    </div>

                  )}


                  {/* ==========================================
                      ELIGIBILITY
                  ========================================== */}

                  {item.eligibility && (

                    <div className="mb-3">

                      <strong>

                        Eligibility

                      </strong>

                      <div className="mt-1">

                        <span
                          className={
                            `badge ${
                              getEligibilityClass(
                                item.eligibility.status
                              )
                            }`
                          }
                        >

                          {
                            item.eligibility
                              .status
                          }

                        </span>

                      </div>

                    </div>

                  )}


                  {/* ==========================================
                      ELIGIBILITY WARNINGS
                  ========================================== */}

                  {item.eligibility
                     ?.warnings
                     ?.length > 0 && (

                    <div
                      className=
                        "alert alert-warning py-2"
                    >

                      {
                        item.eligibility
                          .warnings
                          .map(
                            (
                              warning,
                              index
                            ) => (

                              <div
                                key={index}
                                className="small"
                              >

                                {warning}

                              </div>

                            )
                          )
                      }

                    </div>

                  )}


                  {/* ==========================================
                      NOT ELIGIBLE REASONS
                  ========================================== */}

                  {item.eligibility
                     ?.reasons
                     ?.length > 0 && (

                    <div
                      className=
                        "alert alert-danger py-2"
                    >

                      {
                        item.eligibility
                          .reasons
                          .map(
                            (
                              reason,
                              index
                            ) => (

                              <div
                                key={index}
                                className="small"
                              >

                                {reason}

                              </div>

                            )
                          )
                      }

                    </div>

                  )}


                  {/* ==========================================
                      DESCRIPTION
                  ========================================== */}

                  {item.description && (

                    <p className="text-muted">

                      {item.description}

                    </p>

                  )}


                  {/* ==========================================
                      ACTION BUTTONS
                  ========================================== */}

                  <div className="d-grid gap-2 mt-4">

                    <button

                      className="btn btn-primary"

                      onClick={() =>
                        navigate(
                          `/grant-prediction/${item.id}`
                        )
                      }

                    >

                      Predict Grant Success

                    </button>


                    {item.official_link && (

                      <a

                        href={
                          item.official_link
                        }

                        target="_blank"

                        rel="noreferrer"

                        className=
                          "btn btn-outline-primary"

                      >

                        Official Website

                      </a>

                    )}

                  </div>

                </div>

              </div>

            </div>

          ))}

        </div>

      )}

    </div>

  );

}


export default Funding;