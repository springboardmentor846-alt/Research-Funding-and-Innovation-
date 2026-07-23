import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Navbar.css";

const titles = {"/dashboard":"Dashboard","/profile":"Research profile","/publications":"Publications","/patents":"Patents","/funding":"Funding opportunities","/recommendations":"Recommendations","/grant-matching":"Grant matching"};

export default function TopNavbar() {
  const { user, logout } = useAuth(); const { pathname } = useLocation(); const navigate = useNavigate();
  const signOut = () => { logout(); navigate("/"); };
  return <header className="top-navbar">
    <div className="top-navbar__context"><p className="top-navbar__crumb">Workspace / {titles[pathname] || "Dashboard"}</p><h2>{titles[pathname] || "Dashboard"}</h2></div>
    <div className="top-navbar__actions">
      <label className="top-navbar__search"><i className="bi bi-search" /><input aria-label="Search workspace" placeholder="Search research assets…" /></label>
      <button className="top-navbar__icon-button" aria-label="Notifications"><i className="bi bi-bell" /><span /></button>
      <div className="top-navbar__user"><div className="top-navbar__avatar">{(user?.name || "R").charAt(0).toUpperCase()}</div><div><strong>{user?.name || "Researcher"}</strong><small>{user?.role || "Researcher"}</small></div></div>
      <button className="top-navbar__logout" onClick={signOut}><i className="bi bi-box-arrow-right" /><span>Log out</span></button>
    </div>
  </header>;
}
