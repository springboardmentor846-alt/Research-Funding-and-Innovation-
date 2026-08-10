import { useEffect, useState } from "react";
import api from "../api/api";
import { toast } from "react-toastify";

export default function InnovationScore() {

  const [score, setScore] = useState(null);
  const [portfolio, setPortfolio] = useState(null);
  const [index, setIndex] = useState(null);
  const [impact, setImpact] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {

    try {

      const [s, p, i, r] = await Promise.all([
        api.get("/innovation/score"),
        api.get("/innovation/portfolio-strength"),
        api.get("/innovation/innovation-index"),
        api.get("/innovation/research-impact")
      ]);

      setScore(s.data);
      setPortfolio(p.data);
      setIndex(i.data);
      setImpact(r.data);

    } catch {

      toast.error("Unable to load innovation data");

    }

  };

  if (!score) {

    return (
      <section>
        <div className="loading">
          Loading Innovation Score...
        </div>
      </section>
    );

  }

  return (

    <section>

      <div className="page-heading">

        <div>

          <p className="eyebrow">
            INNOVATION SCORING ENGINE
          </p>

          <h1>Innovation Score</h1>

          <p>
            Overall innovation performance based on
            research publications and patents.
          </p>

        </div>

      </div>


      <div
        style={{
          display:"grid",
          gridTemplateColumns:"repeat(auto-fit,minmax(220px,1fr))",
          gap:"20px"
        }}
      >

        <div className="panel">
          <h3>Innovation Score</h3>
          <h1>{score.innovation_score}</h1>
        </div>

        <div className="panel">
          <h3>Innovation Index</h3>
          <h1>{index?.innovation_index}</h1>
        </div>

        <div className="panel">
          <h3>Research Impact</h3>
          <h1>{impact?.research_impact}</h1>
        </div>

        <div className="panel">
          <h3>Portfolio Strength</h3>
          <h2>{portfolio?.portfolio_strength}</h2>
        </div>

      </div>


      <div
        className="panel"
        style={{marginTop:"25px"}}
      >

        <h2>Research Portfolio</h2>

        <table className="table">

          <tbody>

            <tr>
              <td>Total Publications</td>
              <td>{score.publications}</td>
            </tr>

            <tr>
              <td>Total Patents</td>
              <td>{score.patents}</td>
            </tr>

            <tr>
              <td>Innovation Score</td>
              <td>{score.innovation_score}</td>
            </tr>

            <tr>
              <td>Innovation Index</td>
              <td>{index?.innovation_index}</td>
            </tr>

            <tr>
              <td>Research Impact</td>
              <td>{impact?.research_impact}</td>
            </tr>

            <tr>
              <td>Portfolio Strength</td>
              <td>{portfolio?.portfolio_strength}</td>
            </tr>

          </tbody>

        </table>

      </div>

    </section>

  );

}