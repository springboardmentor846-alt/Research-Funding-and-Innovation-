import { useEffect, useState } from "react";
import api from "../api/api";
import { toast } from "react-toastify";

export default function TechnologyIntelligence() {

  const [technologies, setTechnologies] = useState([]);
  const [maturity, setMaturity] = useState([]);
  const [gaps, setGaps] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {

    try {

      const [t, m, g] = await Promise.all([
        api.get("/technology/emerging-technologies"),
        api.get("/technology/technology-maturity"),
        api.get("/technology/research-gap")
      ]);

      setTechnologies(t.data);
      setMaturity(m.data);
      setGaps(g.data);

    } catch {

      toast.error("Unable to load technology intelligence");

    }

  };

  return (

    <section>

      <div className="page-heading">

        <div>

          <p className="eyebrow">
            TECHNOLOGY INTELLIGENCE
          </p>

          <h1>Technology Intelligence</h1>

          <p>
            Emerging technologies, maturity analysis
            and research gap identification.
          </p>

        </div>

      </div>


      <div className="panel">

        <h2>Emerging Technologies</h2>

        {technologies.map(item => (

          <div
            key={item.technology}
            style={{
              display:"flex",
              justifyContent:"space-between",
              padding:"8px 0"
            }}
          >

            <span>{item.technology}</span>

            <strong>{item.count}</strong>

          </div>

        ))}

      </div>


      <div
        style={{
          display:"grid",
          gridTemplateColumns:"1fr 1fr",
          gap:"20px",
          marginTop:"20px"
        }}
      >

        <div className="panel">

          <h2>Technology Maturity</h2>

          {maturity.map(item=>(

            <div key={item.title}>

              <strong>{item.title}</strong>

              <br/>

              {item.technology}

              <span style={{float:"right"}}>

                {item.maturity}%

              </span>

              <hr/>

            </div>

          ))}

        </div>


        <div className="panel">

          <h2>Research Gap</h2>

          {gaps.length===0 ?

          <p>No research gap detected.</p>

          :

          gaps.map(item=>(

            <div key={item.technology}>

              {item.technology}

              <hr/>

            </div>

          ))}

        </div>

      </div>

    </section>

  );

}