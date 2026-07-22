import {
  FaHome,
  FaMoneyBill,
  FaBook,
  FaLightbulb,
  FaFileAlt
} from "react-icons/fa";

function Sidebar({ activePage, setActivePage }) {

  return (

    <div className="sidebar">

      <h2>RFP</h2>

      <button
        className={activePage === "dashboard" ? "active" : ""}
        onClick={() => setActivePage("dashboard")}
      >
        <FaHome /> Dashboard
      </button>

      <button
        className={activePage === "funding" ? "active" : ""}
        onClick={() => setActivePage("funding")}
      >
        <FaMoneyBill /> Funding
      </button>

      <button
        className={activePage === "publication" ? "active" : ""}
        onClick={() => setActivePage("publication")}
      >
        <FaBook /> Publications
      </button>

      <button
        className={activePage === "patent" ? "active" : ""}
        onClick={() => setActivePage("patent")}
      >
        <FaFileAlt /> Patents
      </button>

      <button
        className={activePage === "analytics" ? "active" : ""}
        onClick={() => setActivePage("analytics")}
      >
        <FaLightbulb /> Analytics
      </button>

      <button>TEST BUTTON</button>

    </div>

  );
}

export default Sidebar;