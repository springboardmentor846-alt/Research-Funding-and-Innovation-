import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";
import SummaryCards from "./components/SummaryCards";
import Sidebar from "./components/Sidebar";
import PublicationChart from "./components/PublicationChart";
function Dashboard({ setLoggedIn }) {

  const [summary, setSummary] = useState({});
  const [funding, setFunding] = useState([]);
  const [domain, setDomain] = useState("");
  const [generatedFunding, setGeneratedFunding] = useState([]);
  const [publicationTrends, setPublicationTrends] = useState([]);
  const [innovationScore, setInnovationScore] = useState(0);
  const [patents, setPatents] = useState([]);
  const [search, setSearch] = useState("");
  const [activePage, setActivePage] = useState("dashboard");
  useEffect(() => {
    getSummary();
    getFunding();
    getPublicationTrends();
    getInnovationScore();
    getPatents();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    setLoggedIn(false);
  };

  const getSummary = async () => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/dashboard-summary"
      );

      setSummary(response.data);

    } catch (error) {
      console.log(error);
    }
  };

  const getFunding = async () => {

    try {

      const response = await axios.get("http://127.0.0.1:8000/funding");

      setFunding(response.data.funding_opportunities);

    } catch (error) {
      console.log(error);
    }

  };

  const generateFunding = async () => {

  if (domain.trim() === "") {
    alert("Please enter a domain");
    return;
  }

  try {

    const response = await axios.get(
      `http://127.0.0.1:8000/generate-funding/${domain}`
    );

    console.log(response.data);

    setGeneratedFunding(response.data.generated_funding);

  } catch (error) {

    console.log(error);

  }

};

  const getPublicationTrends = async () => {

    try {

      const response = await axios.get(
        "http://127.0.0.1:8000/publication-trends"
      );
       console.log(response.data);
      setPublicationTrends(response.data.publication_trends);

    } catch (error) {

      console.log(error);

    }

  };

  const getInnovationScore = async () => {

  try {

    const response = await axios.get(
      "http://127.0.0.1:8000/innovation-score"
    );

    setInnovationScore(response.data.innovation_score);

  } catch (error) {

    console.log(error);

  }

};

const getPatents = async () => {

  try {

    const response = await axios.get(
      "http://127.0.0.1:8000/patents"
    );

    setPatents(response.data.patents);

  } catch (error) {

    console.log(error);

  }

};

   return (
  <div className="container">

    <Sidebar  activePage={activePage}
  setActivePage={setActivePage} />

    <div className="dashboard-box">

      <div className="dashboard-header">

        <div>

          <h1>🚀 Research Funding Platform</h1>
<p>AI Powered Research & Innovation Dashboard</p>

        </div>

        <button
          className="logout-btn"
          onClick={handleLogout}
        >
          Logout
        </button>

      </div>

      <div className="menu">

        <button onClick={() => setActivePage("dashboard")}>
          Dashboard
        </button>

        <button onClick={() => setActivePage("funding")}>
          Funding
        </button>

        <button onClick={() => setActivePage("publication")}>
          Publications
        </button>

        <button onClick={() => setActivePage("patent")}>
          Patents
        </button>

      </div>

      <hr />

      {activePage === "dashboard" && (

        <>

          <h2 className="section-title">
            Dashboard Summary
          </h2>

          <SummaryCards summary={summary} />

          <hr />

          <h2 className="section-title">
            Innovation Score
          </h2>

          <div className="funding-card">

            <h2>{innovationScore}</h2>

            <p>Overall Research Innovation Score</p>

          </div>

        </>

      )}

      {activePage === "funding" && (

        <>

          <h2 className="section-title">
            Funding Opportunities
          </h2>

          <input
            type="text"
            placeholder="Search Funding..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />

          {funding
            .filter(
              (item) =>
                item.funding_name
                  .toLowerCase()
                  .includes(search.toLowerCase()) ||
                item.domain
                  .toLowerCase()
                  .includes(search.toLowerCase())
            )
            .map((item) => (

              <div
                className="funding-card"
                key={item.id}
              >

                <h3>{item.funding_name}</h3>

                <p><b>Domain:</b> {item.domain}</p>

                <p><b>Amount:</b> ₹ {item.amount}</p>

                <p><b>Eligibility:</b> {item.eligibility}</p>

                <p><b>Deadline:</b> {item.deadline}</p>

              </div>

          ))}

          <hr />

          <h2 className="section-title">
            Generate Funding
          </h2>

          <input
            type="text"
            placeholder="Enter Domain"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
          />

          <button onClick={generateFunding}>
            Generate Funding
          </button>

          <p>
            Total Generated Funding :
            {generatedFunding.length}
          </p>

          {generatedFunding.map((item) => (

            <div
              className="funding-card"
              key={item.id}
            >

              <h3>{item.funding_name}</h3>

              <p><b>Domain:</b> {item.domain}</p>

              <p><b>Amount:</b> ₹ {item.amount}</p>

              <p><b>Eligibility:</b> {item.eligibility}</p>

              <p><b>Deadline:</b> {item.deadline}</p>

            </div>

          ))}

        </>

      )}

            {activePage === "publication" && (

        <>

          <h2 className="section-title">
            Publication Trends
          </h2>

          <table className="trend-table">

            <thead>

              <tr>

                <th>Year</th>

                <th>Total Publications</th>

              </tr>

            </thead>

            <tbody>

              {publicationTrends.map((item, index) => (

                <tr key={index}>

                  <td>{item.year}</td>

                  <td>{item.total_publications}</td>

                </tr>

              ))}

            </tbody>

          </table>

          <hr />

          <h2 className="section-title">
            Publication Analytics
          </h2>

          <PublicationChart data={publicationTrends} />

        </>

      )}

      {activePage === "patent" && (

        <>

          <h2 className="section-title">
            Patents
          </h2>

          {patents.map((item) => (

            <div className="funding-card" key={item.id}>

              <h3>{item.patent_title}</h3>

              <p><b>Patent Number:</b> {item.patent_number}</p>

              <p><b>Technology:</b> {item.technology_domain}</p>

              <p><b>Filing Date:</b> {item.filing_date}</p>

            </div>

          ))}

        </>

      )}


      {activePage === "analytics" && (

  <>

    <h2 className="section-title">
      Analytics
    </h2>

    <div className="funding-card">

      <h3>Innovation Score</h3>

      <h1>{innovationScore}</h1>

    </div>

    <br />

    <PublicationChart data={publicationTrends} />

  </>

)}

    </div>

  </div>

);

}

export default Dashboard;