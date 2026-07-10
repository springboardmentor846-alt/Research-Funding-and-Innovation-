import { useEffect, useState } from "react";
import { Navigate, Outlet } from "react-router-dom";
import api from "../api/axios";
import DashboardLayout from "./DashboardLayout";

function ProtectedLayout() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(true);

  useEffect(() => {
    const fetchCurrentUser = async () => {
      try {
        const response = await api.get("/auth/me");
        setUser(response.data);
      } catch {
        localStorage.removeItem("access_token");
        setAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    fetchCurrentUser();
  }, []);

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center min-vh-100">
        <div className="text-center">
          <div
            className="spinner-border text-primary mb-3"
            role="status"
          />

          <p className="text-muted">
            Loading workspace...
          </p>
        </div>
      </div>
    );
  }

  if (!authenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <DashboardLayout user={user}>
      <Outlet context={{ user }} />
    </DashboardLayout>
  );
}

export default ProtectedLayout;