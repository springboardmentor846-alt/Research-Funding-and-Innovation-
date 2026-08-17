import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

// Public
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";

// Shared
import ProtectedLayout from "./components/shared/ProtectedLayout";
import RoleProtectedRoute from "./components/shared/RoleProtectedRoute";

// Layouts
import ResearcherLayout from "./components/researcher/ResearcherLayout";
import StartupLayout from "./components/startup/StartupLayout";
import ManagerLayout from "./components/manager/ManagerLayout";

// ================= RESEARCHER =================

import Dashboard from "./pages/researcher/Dashboard";

import ResearchProfile from "./pages/researcher/ResearchProfile";
import ResearchDomains from "./pages/researcher/ResearchDomains";
import ResearchKeywords from "./pages/researcher/ResearchKeywords";
import TechnologyAreas from "./pages/researcher/TechnologyAreas";
import OrganizationInformation from "./pages/researcher/OrganizationInformation";

import Publications from "./pages/researcher/Publications";
import MyPublications from "./pages/researcher/MyPublications";
import ResearchLibrary from "./pages/researcher/ResearchLibrary";

import Patents from "./pages/researcher/Patents";

import Funding from "./pages/researcher/Funding";
import GrantPrediction from "./pages/researcher/GrantPrediction";

import PatentLandscape from "./pages/researcher/PatentLandscape";
import ResearchTrends from "./pages/researcher/ResearchTrends";

// ================= STARTUP =================

import StartupDashboard from "./pages/startup/StartupDashboard";
import StartupProfile from "./pages/startup/StartupProfile";

import FindResearchers from "./pages/startup/FindResearchers";
import FindStartups from "./pages/startup/FindStartups";
import CollaborationRequests from "./pages/startup/CollaborationRequests";
import StartupFunding from "./pages/startup/Funding";
import PredictSuccess from "./pages/startup/PredictSuccess";
import InnovationScore from "./pages/startup/InnovationScore";

// ================= MANAGER =================

import InnovationManagerDashboard from "./pages/manager/InnovationManagerDashboard";

function App() {

  const token = localStorage.getItem("access_token");
  const role = localStorage.getItem("role");

  const defaultRoute = () => {

    if (!token) return "/login";

    switch (role) {

      case "researcher":
        return "/dashboard";

      case "startup_founder":
        return "/startup/dashboard";

      case "innovation_manager":
        return "/manager/dashboard";

      default:
        return "/login";
    }
  };

  return (

    <BrowserRouter>

      <Routes>

        {/* ---------------- PUBLIC ---------------- */}

        <Route
          path="/"
          element={<Navigate to={defaultRoute()} replace />}
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />

        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />

        {/* =====================================================
                AUTHENTICATED
        ===================================================== */}

        <Route element={<ProtectedLayout />}>

          {/* =====================================================
                      RESEARCHER
          ===================================================== */}

          <Route
            element={
              <RoleProtectedRoute
                allowedRoles={["researcher"]}
              />
            }
          >

            <Route element={<ResearcherLayout />}>

              <Route
                path="/dashboard"
                element={<Dashboard />}
              />

              <Route
                path="/profile"
                element={<ResearchProfile />}
              />

              <Route
                path="/profile/domains"
                element={<ResearchDomains />}
              />

              <Route
                path="/profile/keywords"
                element={<ResearchKeywords />}
              />

              <Route
                path="/profile/technology-areas"
                element={<TechnologyAreas />}
              />

              <Route
                path="/profile/organization"
                element={<OrganizationInformation />}
              />

              <Route
                path="/profile/publications"
                element={<Publications />}
              />

              <Route
                path="/profile/publications/mine"
                element={<MyPublications />}
              />

              <Route
                path="/profile/publications/library"
                element={<ResearchLibrary />}
              />

              <Route
                path="/profile/patents"
                element={<Patents />}
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

            </Route>

          </Route>

{/* =====================================================
            STARTUP
===================================================== */}

{/* =====================================================
                    STARTUP
===================================================== */}

<Route
  element={
    <RoleProtectedRoute
      allowedRoles={["startup_founder"]}
    />
  }
>

  <Route element={<StartupLayout />}>

    <Route
      path="/startup/dashboard"
      element={<StartupDashboard />}
    />

    <Route
      path="/startup/profile"
      element={<StartupProfile />}
    />

    <Route
      path="/startup/researchers"
      element={<FindResearchers />}
    />

    <Route
      path="/startup/startups"
      element={<FindStartups />}
    />

    <Route
      path="/startup/requests"
      element={<CollaborationRequests />}
    />

    <Route
      path="/startup/funding"
      element={<StartupFunding />}
    />

    <Route
      path="/startup/predict-success"
      element={null}
    />

    <Route
      path="/startup/predict-success/:fundingId"
      element={<PredictSuccess />}
    />

    <Route
      path="/startup/innovation-score"
      element={<InnovationScore />}
    />

  </Route>

</Route>

          {/* =====================================================
                      MANAGER
          ===================================================== */}

          <Route
            element={
              <RoleProtectedRoute
                allowedRoles={["innovation_manager"]}
              />
            }
          >

            <Route element={<ManagerLayout />}>

              <Route
                path="/manager/dashboard"
                element={<InnovationManagerDashboard />}
              />

            </Route>

          </Route>

        </Route>

        {/* ---------------- UNKNOWN ---------------- */}

        <Route
          path="*"
          element={<Navigate to={defaultRoute()} replace />}
        />

      </Routes>

    </BrowserRouter>

  );
}

export default App;