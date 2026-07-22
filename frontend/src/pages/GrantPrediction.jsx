import { useEffect, useState } from "react";
import { getGrantPrediction } from "../api/grantPrediction";
import { useParams } from "react-router-dom";


function GrantPrediction() {
  const { fundingId } = useParams();
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPrediction();
  }, [fundingId]);

  async function loadPrediction() {

    try {

      const data = await getGrantPrediction(Number(fundingId));

setPrediction(data);
    } catch (error) {

      console.error(error);

    } finally {

      setLoading(false);

    }

  }

  if (loading) {
    return <h3>Loading...</h3>;
  }
  if (!prediction) {
  return <h3>No prediction available.</h3>;
}

  return (

    <div>

      <h2 className="mb-4">
        AI Grant Prediction
      </h2>

      <div className="card shadow-sm mb-4">

        <div className="card-body">

          <h4>
            {prediction.funding}
          </h4>

          <hr />

          <div className="row">

            <div className="col-md-4">

              <h6>Grant Probability</h6>

              <h2 className="text-primary">
                {prediction.grant_probability}%
              </h2>

            </div>

            <div className="col-md-4">

              <h6>Innovation Score</h6>

              <h2 className="text-success">
                {prediction.innovation_score}
              </h2>

            </div>

            <div className="col-md-4">

              <h6>Confidence</h6>

              <h2 className="text-warning">
                {prediction.confidence}
              </h2>

            </div>

          </div>

        </div>

      </div>

      <div className="row">

        <div className="col-md-6">

          <div className="card h-100">

            <div className="card-body">

              <h5>Strengths</h5>

              <ul>

                {prediction.strengths.map((item, index) => (

                  <li key={index}>
                    {item}
                  </li>

                ))}

              </ul>

            </div>

          </div>

        </div>

        <div className="col-md-6">

          <div className="card h-100">

            <div className="card-body">

              <h5>Improvements</h5>

              <ul>

                {prediction.improvements.map((item, index) => (

                  <li key={index}>
                    {item}
                  </li>

                ))}

              </ul>

            </div>

          </div>

        </div>

      </div>

      <div className="card mt-4">

        <div className="card-body">

          <h5>Profile Features Used</h5>

          <table className="table">

            <tbody>

              <tr>
                <td>Publications</td>
                <td>{prediction.features.publications}</td>
              </tr>

              <tr>
                <td>Patents</td>
                <td>{prediction.features.patents}</td>
              </tr>

              <tr>
                <td>Domains</td>
                <td>{prediction.features.domains}</td>
              </tr>

              <tr>
                <td>Keywords</td>
                <td>{prediction.features.keywords}</td>
              </tr>

              <tr>
                <td>Technology Areas</td>
                <td>{prediction.features.technology_areas}</td>
              </tr>

            </tbody>

          </table>

        </div>

      </div>

    </div>

  );

}

export default GrantPrediction;