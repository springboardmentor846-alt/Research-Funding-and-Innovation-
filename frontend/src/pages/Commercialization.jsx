import { useEffect, useState } from "react";
import api from "../api/api";
import { toast } from "react-toastify";

export default function Commercialization() {

  const [recommendations, setRecommendations] = useState([]);
  const [licensing, setLicensing] = useState(null);
  const [startup, setStartup] = useState(null);
  const [industry, setIndustry] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {

    try {

      const [r, l, s, i] = await Promise.all([
        api.get("/commercialization/recommendations"),
        api.get("/commercialization/licensing"),
        api.get("/commercialization/startup"),
        api.get("/commercialization/industry")
      ]);

      setRecommendations(r.data);
      setLicensing(l.data);
      setStartup(s.data);
      setIndustry(i.data);

    } catch {

      toast.error("Unable to load commercialization data");

    }

  };

  return (

    <section>

      <div className="page-heading">

        <div>

          <p className="eyebrow">
            COMMERCIALIZATION ENGINE
          </p>

          <h1>Commercialization</h1>

          <p>
            Commercialization opportunities generated
            from patents and publications.
          </p>

        </div>

      </div>


      <div
        style={{
          display:"grid",
          gridTemplateColumns:"repeat(auto-fit,minmax(250px,1fr))",
          gap:"20px",
          marginBottom:"30px"
        }}
      >

        <div className="panel">
          <h3>Licensing</h3>
          <h2>{licensing?.eligible ? "Eligible" : "Not Eligible"}</h2>
        </div>

        <div className="panel">
          <h3>Startup</h3>
          <h2>{startup?.recommended ? "Recommended" : "Not Recommended"}</h2>
        </div>

        <div className="panel">
          <h3>Industry Collaboration</h3>
          <h2>{industry?.recommended ? "Recommended" : "Not Recommended"}</h2>
        </div>

      </div>


      <div className="record-list">

        {recommendations.map((item,index)=>(

          <article
            className="record"
            key={index}
          >

            <div>

              <h3>{item.type}</h3>

              <p>{item.description}</p>

            </div>

          </article>

        ))}

      </div>

    </section>

  );

}