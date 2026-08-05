import { Navigate, Outlet, useOutletContext } from "react-router-dom";

function RoleProtectedRoute({ allowedRoles }) {
  const { user } = useOutletContext();

  if (!user) {
    return null;
  }

  if (!allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet context={{ user }} />;
}

export default RoleProtectedRoute;