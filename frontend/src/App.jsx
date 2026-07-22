import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import ResearchProfile from "./pages/ResearchProfile";
import ResearchDomains from "./pages/ResearchDomains";
import ResearchKeywords from "./pages/ResearchKeywords";
import TechnologyAreas from "./pages/TechnologyAreas";
import OrganizationInformation from "./pages/OrganizationInformation";
import Publications from "./pages/Publications";
import Patents from "./pages/Patents";
import Funding from "./pages/Funding";
import GrantPrediction from "./pages/GrantPrediction";
import PatentLandscape from "./pages/PatentLandscape";
import ResearchTrends from "./pages/ResearchTrends";



import ProtectedLayout from "./components/ProtectedLayout";
import RoleProtectedRoute from "./components/RoleProtectedRoute";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Root route */}
        <Route
          path="/"
          element={
            <Navigate
              to={
                localStorage.getItem("access_token")
                  ? "/dashboard"
                  : "/login"
              }
              replace
            />
          }
        />

        {/* Public routes */}
        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />

        {/* Authenticated routes */}
<Route element={<ProtectedLayout />}>
  <Route
    path="/dashboard"
    element={<Dashboard />}
  />

  <Route
    element={
      <RoleProtectedRoute
        allowedRoles={["researcher"]}
      />
    }
  >

    <Route path="/profile" element={<ResearchProfile />} />
    <Route path="/profile/domains" element={<ResearchDomains />} />
    <Route path="/profile/keywords" element={<ResearchKeywords />} />
    <Route path="/profile/technology-areas" element={<TechnologyAreas />} />
    <Route path="/profile/organization" element={<OrganizationInformation />} />
    <Route path="/profile/publications" element={<Publications />} />
    <Route path="/profile/patents" element={<Patents />} />

    {/* NEW ROUTES */}

    <Route
      path="/funding"
      element={<Funding />}
    />

    <Route
      path="/grant-prediction/:fundingId"
      element={<GrantPrediction />}
    />

    <Route
      path="/patent-landscape"
      element={<PatentLandscape />}
    />

    <Route
      path="/research-trends"
      element={<ResearchTrends />}
    />

  </Route>
</Route>

<Route
  path="*"
  element={
    <Navigate
      to={
        localStorage.getItem("access_token")
          ? "/dashboard"
          : "/login"
      }
      replace
    />
  }
/>

        {/* Unknown routes */}
        <Route
          path="*"
          element={
            <Navigate
              to={
                localStorage.getItem("access_token")
                  ? "/dashboard"
                  : "/login"
              }
              replace
            />
          }
        />

        <Route
    path="/funding"
    element={<Funding />}
/>

<Route
    path="/grant-prediction/:fundingId"
    element={<GrantPrediction />}
/>

<Route
    path="/patent-landscape"
    element={<PatentLandscape />}
/>

<Route
    path="/research-trends"
    element={<ResearchTrends />}
/>
      </Routes>
    </BrowserRouter>
  );
}

export default App;