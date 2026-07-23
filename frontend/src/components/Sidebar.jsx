import { NavLink } from "react-router-dom";
import "./Sidebar.css";

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <i className="bi bi-bezier2" />
        <span>
          Research<strong>Intel</strong>
        </span>
      </div>

      <nav className="sidebar-menu">
        <p>WORKSPACE</p>

        <NavLink to="/dashboard" className="menu-item">
          <i className="bi bi-grid-1x2" />
          Dashboard
        </NavLink>

        <NavLink to="/profile" className="menu-item">
          <i className="bi bi-person-vcard" />
          Research Profile
        </NavLink>

        <p>RESEARCH ASSETS</p>

        <NavLink to="/publications" className="menu-item">
          <i className="bi bi-journal-text" />
          Publications
        </NavLink>

        <NavLink to="/patents" className="menu-item">
          <i className="bi bi-lightbulb" />
          Patents
        </NavLink>

        <NavLink to="/funding" className="menu-item">
          <i className="bi bi-cash-coin" />
          Funding
        </NavLink>

        <p>INTELLIGENCE</p>

        <NavLink to="/recommendations" className="menu-item">
          <i className="bi bi-stars" />
          Recommendations
        </NavLink>

        <NavLink to="/grant-matching" className="menu-item">
          <i className="bi bi-diagram-3" />
          Grant Matching
        </NavLink>

        <NavLink to="/publication-trends" className="menu-item">
          <i className="bi bi-bar-chart-line" />
          Publication Trends
        </NavLink>
      </nav>

      <div className="sidebar-footer">
        <span>
          <i className="bi bi-shield-check" />
          Research Workspace
        </span>
      </div>
    </aside>
  );
}

export default Sidebar;