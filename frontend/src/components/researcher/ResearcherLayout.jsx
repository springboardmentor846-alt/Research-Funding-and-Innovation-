import { useState } from "react";
import {
  NavLink,
  useNavigate,
  Outlet,
  useOutletContext,
} from "react-router-dom";
import {
  BarChart3,
  BookOpenText,
  Building2,
  FileText,
  FlaskConical,
  Globe2,
  Handshake,
  Lightbulb,
  LogOut,
  Mail,
  Menu,
  Target,
  Tags,
  TrendingUp,
  UserRound,
  WalletCards,
} from "lucide-react";

function ResearcherLayout() {
  const { user } = useOutletContext();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    navigate("/login");
  };

  const navItems = [
    {
      heading: "Workspace",
      items: [
        { path: "/dashboard", label: "Dashboard", icon: BarChart3 },
      ],
    },

    {
      heading: "Research",
      items: [
        { path: "/profile", label: "Research Profile", icon: UserRound },
        { path: "/profile/domains", label: "Research Domains", icon: FlaskConical },
        { path: "/profile/keywords", label: "Keywords", icon: Tags },
        { path: "/profile/technology-areas", label: "Technology Areas", icon: Lightbulb },
        { path: "/profile/organization", label: "Organization", icon: Building2 },
      ],
    },

    {
      heading: "Research Assets",
      items: [
        { path: "/profile/publications", label: "Publications", icon: BookOpenText },
        { path: "/profile/patents", label: "Patents", icon: FileText },
      ],
    },

    {
      heading: "Collaboration",
      items: [
        { path: "/startups", label: "Find Startups", icon: Handshake },
        { path: "/requests", label: "Collaboration Requests", icon: Mail },
      ],
    },

    {
      heading: "Funding",
      items: [
        { path: "/funding", label: "Funding Opportunities", icon: WalletCards },
        { path: "/grant-prediction/1", label: "Grant Prediction", icon: Target },
      ],
    },

    {
      heading: "Analytics",
      items: [
        { path: "/patent-landscape", label: "Patent Landscape", icon: Globe2 },
        { path: "/research-trends", label: "Research Trends", icon: TrendingUp },
      ],
    },
  ];

  return (
    <div
      className={`app-shell ${
        collapsed ? "sidebar-collapsed" : ""
      }`}
    >
      <aside className="app-sidebar">
        <div className="sidebar-brand">
          <div className="brand-mark">IF</div>

          {!collapsed && (
            <div className="brand-text">
              <h5>InnovFund</h5>
              <span>Research Intelligence</span>
            </div>
          )}
        </div>

        {!collapsed && (
          <div className="sidebar-section-label">
            WORKSPACE
          </div>
        )}

        <nav className="sidebar-nav">
          {navItems.map((group) => (
            <div key={group.heading}>
              {!collapsed && (
                <div className="sidebar-section-label">
                  {group.heading}
                </div>
              )}

              {group.items.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  end={
                    item.path === "/dashboard" ||
                    item.path === "/profile"
                  }
                  className={({ isActive }) =>
                    `sidebar-link ${isActive ? "active" : ""}`
                  }
                >
                  <span className="sidebar-icon">
                    <item.icon size={17} strokeWidth={1.9} />
                  </span>

                  {!collapsed && (
                    <span>{item.label}</span>
                  )}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-user">
          <div className="user-avatar">
            {user?.full_name?.charAt(0)?.toUpperCase() || "R"}
          </div>

          {!collapsed && (
            <div className="sidebar-user-info">
              <strong>
                {user?.full_name || "Researcher"}
              </strong>

              <span>
                {user?.role || "researcher"}
              </span>
            </div>
          )}

          {!collapsed && (
            <button
              className="logout-icon-btn"
              onClick={handleLogout}
              title="Logout"
              aria-label="Logout"
            >
              <LogOut size={19} strokeWidth={2} />
            </button>
          )}
        </div>
      </aside>

      <main className="app-main">
        <header className="app-topbar">
          <div className="d-flex align-items-center gap-3">
            <button
              className="sidebar-toggle-btn"
              onClick={() => setCollapsed(!collapsed)}
              aria-label="Toggle sidebar"
              title={
                collapsed
                  ? "Expand sidebar"
                  : "Collapse sidebar"
              }
            >
              <Menu size={20} />
            </button>

            <span className="topbar-label">
              RESEARCH FUNDING & INNOVATION PLATFORM
            </span>
          </div>

          <div className="topbar-status">
            <span className="status-dot"></span>
            System Online
          </div>
        </header>

        <div className="app-content">
          <Outlet context={{ user }} />
        </div>
      </main>
    </div>
  );
}

export default ResearcherLayout;





// import { useState } from "react";
// import {
//   NavLink,
//   useNavigate,
//   Outlet,
//   useOutletContext,
// } from "react-router-dom";
// import { LogOut } from "lucide-react";

// function ResearcherLayout() {
//   const { user } = useOutletContext();
//   const navigate = useNavigate();
//   const [collapsed, setCollapsed] = useState(false);

//   const handleLogout = () => {
//     localStorage.removeItem("access_token");
//     localStorage.removeItem("refresh_token");
//     navigate("/login");
//   };

//   const navItems = [
//     {
//       heading: "Workspace",
//       items: [
//         {
//           path: "/dashboard",
//           label: "Dashboard",
//           icon: "📊",
//         },
//       ],
//     },

//     {
//       heading: "Research",
//       items: [
//         {
//           path: "/profile",
//           label: "Research Profile",
//           icon: "👤",
//         },
//         {
//           path: "/profile/domains",
//           label: "Research Domains",
//           icon: "🧪",
//         },
//         {
//           path: "/profile/keywords",
//           label: "Keywords",
//           icon: "🏷️",
//         },
//         {
//           path: "/profile/technology-areas",
//           label: "Technology Areas",
//           icon: "💡",
//         },
//         {
//           path: "/profile/organization",
//           label: "Organization",
//           icon: "🏢",
//         },
//       ],
//     },

//     {
//       heading: "Research Assets",
//       items: [
//         {
//           path: "/profile/publications",
//           label: "Publications",
//           icon: "📚",
//         },
//         {
//           path: "/profile/patents",
//           label: "Patents",
//           icon: "📄",
//         },
//       ],
//     },

//     {
//       heading: "Collaboration",
//       items: [
//         {
//           path: "/startups",
//           label: "Find Startups",
//           icon: "🤝",
//         },
//         {
//           path: "/requests",
//           label: "Collaboration Requests",
//           icon: "📨",
//         },
//       ],
//     },

//     {
//       heading: "Funding",
//       items: [
//         {
//           path: "/funding",
//           label: "Funding Opportunities",
//           icon: "💰",
//         },
//         {
//           path: "/grant-prediction/1",
//           label: "Grant Prediction",
//           icon: "🎯",
//         },
//       ],
//     },

//     {
//       heading: "Analytics",
//       items: [
//         {
//           path: "/patent-landscape",
//           label: "Patent Landscape",
//           icon: "🌍",
//         },
//         {
//           path: "/research-trends",
//           label: "Research Trends",
//           icon: "📈",
//         },
//       ],
//     },
//   ];

//   return (
//     <div
//       className={`app-shell ${
//         collapsed ? "sidebar-collapsed" : ""
//       }`}
//     >
//       <aside className="app-sidebar">
//         <div className="sidebar-brand">
//           <div className="brand-mark">IF</div>

//           {!collapsed && (
//             <div className="brand-text">
//               <h5>InnovFund</h5>
//               <span>Research Intelligence</span>
//             </div>
//           )}
//         </div>

//         {!collapsed && (
//           <div className="sidebar-section-label">
//             WORKSPACE
//           </div>
//         )}

//         <nav className="sidebar-nav">
//           {navItems.map((group) => (
//             <div key={group.heading}>
//               {!collapsed && (
//                 <div className="sidebar-section-label">
//                   {group.heading}
//                 </div>
//               )}

//               {group.items.map((item) => (
//                 <NavLink
//                   key={item.path}
//                   to={item.path}
//                   end={
//                     item.path === "/dashboard" ||
//                     item.path === "/profile"
//                   }
//                   className={({ isActive }) =>
//                     `sidebar-link ${isActive ? "active" : ""}`
//                   }
//                 >
//                   <span className="sidebar-icon">
//                     {item.icon}
//                   </span>

//                   {!collapsed && (
//                     <span>{item.label}</span>
//                   )}
//                 </NavLink>
//               ))}
//             </div>
//           ))}
//         </nav>

//         <div className="sidebar-user">
//           <div className="user-avatar">
//             {user?.full_name?.charAt(0)?.toUpperCase() || "R"}
//           </div>

//           {!collapsed && (
//             <div className="sidebar-user-info">
//               <strong>
//                 {user?.full_name || "Researcher"}
//               </strong>

//               <span>
//                 {user?.role || "researcher"}
//               </span>
//             </div>
//           )}

//           {!collapsed && (
//             <button
//               className="logout-icon-btn"
//               onClick={handleLogout}
//               title="Logout"
//               aria-label="Logout"
//             >
//               <LogOut size={19} strokeWidth={2} />
//             </button>
//           )}
//         </div>
//       </aside>

//       <main className="app-main">
//         <header className="app-topbar">
//           <div className="d-flex align-items-center gap-3">
//             <button
//               className="sidebar-toggle-btn"
//               onClick={() => setCollapsed(!collapsed)}
//               aria-label="Toggle sidebar"
//               title={
//                 collapsed
//                   ? "Expand sidebar"
//                   : "Collapse sidebar"
//               }
//             >
//               ☰
//             </button>

//             <span className="topbar-label">
//               RESEARCH FUNDING & INNOVATION PLATFORM
//             </span>
//           </div>

//           <div className="topbar-status">
//             <span className="status-dot"></span>
//             System Online
//           </div>
//         </header>

//         <div className="app-content">
//           <Outlet context={{ user }} />
//         </div>
//       </main>
//     </div>
//   );
// }

// export default ResearcherLayout;