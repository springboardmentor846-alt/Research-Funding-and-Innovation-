import { NavLink } from "react-router-dom";
import "./Sidebar.css";

function Sidebar() {
  return (
    <aside className="sidebar">

      <div className="sidebar-logo">
        <i className="bi bi-bezier2"></i>
        <span>
          Research<strong>Intel</strong>
        </span>
      </div>

      <nav className="sidebar-menu">

        <p>WORKSPACE</p>

        <NavLink to="/dashboard" className="menu-item">
          <i className="bi bi-grid-1x2"></i>
          Dashboard
        </NavLink>

        <NavLink to="/profile" className="menu-item">
          <i className="bi bi-person-vcard"></i>
          Research Profile
        </NavLink>

        <p>RESEARCH</p>

        <NavLink to="/publications" className="menu-item">
          <i className="bi bi-journal-text"></i>
          Publications
        </NavLink>

        <NavLink to="/patents" className="menu-item">
          <i className="bi bi-lightbulb"></i>
          Patents
        </NavLink>

        <NavLink to="/funding" className="menu-item">
          <i className="bi bi-cash-coin"></i>
          Funding
        </NavLink>

        <p>INTELLIGENCE</p>

        <NavLink to="/recommendations" className="menu-item">
          <i className="bi bi-stars"></i>
          Recommendations
        </NavLink>

        <NavLink to="/grant-matching" className="menu-item">
          <i className="bi bi-diagram-3"></i>
          Grant Matching
        </NavLink>

        <NavLink to="/publication-trends" className="menu-item">
          <i className="bi bi-bar-chart-line"></i>
          Publication Trends
        </NavLink>

        <NavLink to="/patent-intelligence" className="menu-item">
          <i className="bi bi-cpu"></i>
          Patent Intelligence
        </NavLink>

        <NavLink to="/technology-intelligence" className="menu-item">
          <i className="bi bi-diagram-2"></i>
          Technology Intelligence
        </NavLink>

        <NavLink to="/innovation-score" className="menu-item">
          <i className="bi bi-award"></i>
          Innovation Score
        </NavLink>

        <NavLink to="/commercialization" className="menu-item">
          <i className="bi bi-building"></i>
          Commercialization
        </NavLink>

        <NavLink to="/innovation-dashboard" className="menu-item">
          <i className="bi bi-speedometer2"></i>
          Innovation Dashboard
        </NavLink>

      </nav>

      <div className="sidebar-footer">
        <span>
          <i className="bi bi-shield-check"></i>
          Research Workspace
        </span>
      </div>

    </aside>
  );
}

export default Sidebar;