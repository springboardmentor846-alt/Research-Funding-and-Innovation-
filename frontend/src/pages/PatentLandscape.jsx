import { useState } from "react";
import { getPatentLandscape } from "../api/patentLandscape";

function PatentLandscape() {

  const [query, setQuery] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  async function loadLandscape() {

    if (!query.trim()) {
      alert("Please enter a technology or keyword.");
      return;
    }

    setLoading(true);

    try {

      const response = await getPatentLandscape(query);

      setData(response);

    } catch (error) {

      console.error(error);

    } finally {

      setLoading(false);

    }

  }

  return (

    <div>

      <div className="module-page-header mb-4">

        <div>

          <span className="module-eyebrow">
            PATENT INTELLIGENCE
          </span>

          <h1>Global Patent Landscape</h1>

          <p>
            Analyze worldwide patent activity,
            leading organizations,
            technology classes and AI-generated insights.
          </p>

        </div>

      </div>

      <div className="card shadow-sm mb-4">

        <div className="card-body">

          <label className="form-label">
            Technology / Keyword
          </label>

          <div className="input-group">

            <input
              type="text"
              className="form-control"
              placeholder="Example: Machine Learning"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />

            <button
              className="btn btn-primary"
              onClick={loadLandscape}
            >
              Analyze
            </button>

          </div>

        </div>

      </div>

      {loading && (

        <div className="text-center my-4">

          <div className="spinner-border text-primary"></div>

        </div>

      )}

      {!loading && data && (

        <>

          {/* Summary */}

          <div className="row mb-4">

            <div className="col-md-3">

              <div className="card border-0 shadow h-100">

                <div className="card-body">

<h6>Patents Analyzed</h6>

                  <h2>{data.summary.total_patents}</h2>

                </div>

              </div>

            </div>

            <div className="col-md-3">

              <div className="card border-0 shadow h-100">

                <div className="card-body">

                  <h6>Countries</h6>

                  <h2>{data.summary.countries}</h2>

                </div>

              </div>

            </div>

            <div className="col-md-3">

              <div className="card border-0 shadow h-100">

                <div className="card-body">

                  <h6>Organizations</h6>

                  <h2>{data.summary.organizations}</h2>

                </div>

              </div>

            </div>

            <div className="col-md-3">

              <div className="card border-0 shadow h-100">

                <div className="card-body">

                  <h6>Technology Classes</h6>

                  <h2>{data.summary.technology_classes}</h2>

                </div>

              </div>

            </div>

          </div>

          {/* Filing Trends */}

{data.filing_trends &&
  Object.keys(data.filing_trends).length > 0 && (

    <div className="card shadow-sm mb-4">

      <div className="card-body">

        <h4 className="mb-4">
          📈 Patent Filing Trends
        </h4>

        <p className="text-muted mb-4">
          Year-wise distribution of patent publications
          related to the searched technology.
        </p>

        {Object.entries(data.filing_trends).map(
          ([year, count]) => {

            const maxCount = Math.max(
              ...Object.values(data.filing_trends)
            );

            const percentage =
              maxCount > 0
                ? (count / maxCount) * 100
                : 0;

            return (

              <div
                key={year}
                className="mb-3"
              >

                <div className="d-flex justify-content-between mb-1">

                  <strong>
                    {year}
                  </strong>

                  <span>
                    {count} patents
                  </span>

                </div>

                <div
                  className="progress"
                  style={{ height: "10px" }}
                >

                  <div
                    className="progress-bar"
                    role="progressbar"
                    style={{
                      width: `${percentage}%`
                    }}
                    aria-valuenow={count}
                    aria-valuemin="0"
                    aria-valuemax={maxCount}
                  />

                </div>

              </div>

            );

          }
        )}

      </div>

    </div>

)}

{/* Patent Status Distribution */}

{data.status_distribution &&
  Object.keys(data.status_distribution).length > 0 && (

    <div className="card shadow-sm mb-4">

      <div className="card-body">

        <h4 className="mb-3">
          📊 Patent Status Distribution
        </h4>

        <p className="text-muted mb-4">
          Distribution of patents based on their
          current legal or application status.
        </p>

        <div className="row">

          {Object.entries(
            data.status_distribution
          ).map(([status, count]) => (

            <div
              key={status}
              className="col-md-3 mb-3"
            >

              <div className="border rounded p-3 h-100">

                <div
                  className="text-muted mb-2"
                  style={{
                    fontSize: "13px",
                    fontWeight: "600"
                  }}
                >
                  {status
                    .replaceAll("_", " ")
                    .toUpperCase()}
                </div>

                <h3 className="mb-0">
                  {count}
                </h3>

                <small className="text-muted">
                  Patents
                </small>

              </div>

            </div>

          ))}

        </div>

      </div>

    </div>

)}

          {/*Insights */}

          <div className="card shadow-sm mb-4">

            <div className="card-body">

              <h4>🤖 AI Insights</h4>

              <ul>

                {data.insights.map((item, index) => (

                  <li key={index} className="mb-2">

                    {item}

                  </li>

                ))}

              </ul>

            </div>

          </div>

          {/* Country Distribution */}

          <div className="card shadow-sm mb-4">

            <div className="card-body">

              <h4>🌍 Country Distribution</h4>

              <div className="table-responsive">

                <table className="table table-hover align-middle">

                  <thead>

                    <tr>

                      <th>Country</th>

                      <th>Patents</th>

                    </tr>

                  </thead>

<tbody>

  {data.country_distribution.map((item) => (

    <tr key={item.code}>

      <td>

        {item.name}

        <span className="text-muted ms-2">
          ({item.code})
        </span>

      </td>

      <td>

        <span className="badge bg-primary">
          {item.count}
        </span>

      </td>

    </tr>

  ))}

</tbody>

                </table>

              </div>

            </div>

          </div>

          {/* Top Applicants */}

          <div className="card shadow-sm mb-4">

            <div className="card-body">

              <h4>🏢 Top Applicants</h4>

              <div className="table-responsive">

                <table className="table table-hover align-middle">

                  <thead>

                    <tr>

                      <th>Organization</th>

                      <th>Patents</th>

                    </tr>

                  </thead>

                  <tbody>

                    {Object.entries(data.top_applicants).map(

                      ([org, count]) => (

                        <tr key={org}>

                          <td>{org}</td>

                          <td>

                            <span className="badge bg-primary">

                              {count}

                            </span>

                          </td>

                        </tr>

                      )

                    )}

                  </tbody>

                </table>

              </div>

            </div>

          </div>

          {/* Technology Classes */}

          <div className="card shadow-sm mb-4">

            <div className="card-body">

              <h4>💡 Technology Classes</h4>

              <div className="table-responsive">

                <table className="table table-hover align-middle">

                  <thead>

                    <tr>

                      <th>CPC</th>

                      <th>Count</th>

                    </tr>

                  </thead>

                  <tbody>

                    {Object.entries(data.technology_classes).map(

                      ([cpc, count]) => (

                        <tr key={cpc}>

                          <td>{cpc}</td>

                          <td>

                            <span className="badge bg-primary">

                              {count}

                            </span>

                          </td>

                        </tr>

                      )

                    )}

                  </tbody>

                </table>

              </div>

            </div>

{/* =====================================================
    PERSONALIZED RELEVANT PATENTS
===================================================== */}

{data.relevant_patents &&
  data.relevant_patents.length > 0 && (

    <div className="card shadow-sm mb-4">

      <div className="card-body">


        <div className="mb-4">

          <h4>
            📄 Relevant Patents
          </h4>


          <p className="text-muted mb-0">

            Patents identified from the searched technology
            and ranked according to similarity with your
            research profile, domains, keywords and
            technology areas.

          </p>

        </div>


        {!data.personalized_relevance && (

          <div className="alert alert-warning">

            Complete your research profile, research domains,
            keywords and technology areas to enable
            personalized patent relevance ranking.

          </div>

        )}


        <div className="table-responsive">

          <table className="table table-hover align-middle">


            <thead>

              <tr>

                <th>
                  Patent Title
                </th>

                <th>
                  Applicant
                </th>

                <th>
                  Country
                </th>

                <th>
                  Publication Date
                </th>

                <th>
                  Status
                </th>

                <th>
                  CPC
                </th>

                <th>
                  Profile Relevance
                </th>

              </tr>

            </thead>


            <tbody>


              {data.relevant_patents.map(

                (patent, index) => (

                  <tr
                    key={
                      patent.publication_number
                      || index
                    }
                  >


                    {/* Patent Title */}

                    <td>

                      <strong>

                        {patent.title
                          || "Title unavailable"}

                      </strong>


                      {patent.publication_number && (

                        <div
                          className="text-muted mt-1"
                          style={{
                            fontSize: "12px"
                          }}
                        >

                          {
                            patent.publication_number
                          }

                        </div>

                      )}

                    </td>


                    {/* Applicant */}

                    <td>

                      {patent.applicants &&
                      patent.applicants.length > 0

                        ? patent.applicants.join(", ")

                        : "Not available"}

                    </td>


                    {/* Country */}

                    <td>

                      {patent.jurisdiction_name
                        || patent.jurisdiction
                        || "Not available"}

                      {patent.jurisdiction &&
                        patent.jurisdiction_name && (

                          <div
                            className="text-muted"
                            style={{
                              fontSize: "12px"
                            }}
                          >

                            {
                              patent.jurisdiction
                            }

                          </div>

                        )}

                    </td>


                    {/* Publication Date */}

                    <td>

                      {patent.publication_date
                        || "Not available"}

                    </td>


                    {/* Status */}

                    <td>

                      {patent.status ? (

                        <span className="badge bg-secondary">

                          {patent.status}

                        </span>

                      ) : (

                        "Not available"

                      )}

                    </td>


                    {/* CPC */}

                    <td>

                      {patent.cpc_codes &&
                      patent.cpc_codes.length > 0

                        ? patent.cpc_codes.join(", ")

                        : "Not available"}

                    </td>


                    {/* Personalized relevance */}

                    <td>

                      {data.personalized_relevance ? (

                        <span className="badge bg-success">

                          {
                            patent.relevance_score
                          }%

                        </span>

                      ) : (

                        <span className="badge bg-secondary">

                          N/A

                        </span>

                      )}

                    </td>


                  </tr>

                )

              )}


            </tbody>

          </table>

        </div>

      </div>

    </div>

)}

{/* Patent Clusters */}

{data.patent_clusters &&
  Object.keys(data.patent_clusters).length > 0 && (

    <div className="card shadow-sm mb-4">

      <div className="card-body">

        <h4 className="mb-3">
          🧩 Patent Technology Clusters
        </h4>

        <p className="text-muted mb-4">
          Broad technology areas identified from
          CPC classifications within the retrieved patents.
        </p>


        <div className="row">

          {Object.entries(
            data.patent_clusters
          ).map(([cluster, count]) => (

            <div
              key={cluster}
              className="col-md-6 col-lg-4 mb-3"
            >

              <div className="border rounded p-3 h-100">

                <div className="d-flex justify-content-between align-items-start">

                  <strong>
                    {cluster}
                  </strong>

                  <span className="badge bg-primary">

                    {count}

                  </span>

                </div>

                <small className="text-muted">

                  Classification occurrences

                </small>

              </div>

            </div>

          ))}

        </div>

      </div>

    </div>

)}

{/* Innovation Mapping */}

{data.innovation_map &&
  data.innovation_map.length > 0 && (

    <div className="card shadow-sm mb-4">

      <div className="card-body">

        <h4 className="mb-3">
          🗺️ Innovation Mapping
        </h4>

        <p className="text-muted mb-4">
          Distribution of patent classification activity
          across broad technology areas.
        </p>


        {data.innovation_map.map(
          (item) => (

            <div
              key={item.technology_cluster}
              className="mb-4"
            >

              <div className="d-flex justify-content-between mb-2">

                <div>

                  <strong>
                    {item.technology_cluster}
                  </strong>

                  <div
                    className="text-muted"
                    style={{
                      fontSize: "12px"
                    }}
                  >

                    {
                      item.classification_occurrences
                    }{" "}
                    classification occurrences

                  </div>

                </div>


                <strong>

                  {item.share_percentage}%

                </strong>

              </div>


              <div
                className="progress"
                style={{
                  height: "12px"
                }}
              >

                <div
                  className="progress-bar"
                  role="progressbar"
                  style={{
                    width:
                      `${item.share_percentage}%`
                  }}
                  aria-valuenow={
                    item.share_percentage
                  }
                  aria-valuemin="0"
                  aria-valuemax="100"
                />

              </div>

            </div>

          )
        )}

      </div>

    </div>

)}

          </div>

        </>

      )}

    </div>

  );

}

export default PatentLandscape;