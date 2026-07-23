import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import TopNavbar from "./Navbar";
import "./DashboardLayout.css";

export default function DashboardLayout() {
  return (
    <div className="dashboard-layout">
      <Sidebar />
      <main className="main-content">
        <TopNavbar />
        <Outlet />
      </main>
    </div>
  );
}
