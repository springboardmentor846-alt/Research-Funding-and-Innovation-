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
import MyPublications from "./pages/MyPublications";
import ResearchLibrary from "./pages/ResearchLibrary";

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

        {/* =====================================================
            ROOT
        ===================================================== */}

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


        {/* =====================================================
            PUBLIC ROUTES
        ===================================================== */}

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />


        {/* =====================================================
            AUTHENTICATED ROUTES
        ===================================================== */}

        <Route element={<ProtectedLayout />}>

          {/* Dashboard */}

          <Route
            path="/dashboard"
            element={<Dashboard />}
          />


          {/* =================================================
              RESEARCHER ROUTES
          ================================================= */}

          <Route
            element={
              <RoleProtectedRoute
                allowedRoles={["researcher"]}
              />
            }
          >

            {/* ---------------- PROFILE ---------------- */}

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


            {/* ---------------- PUBLICATIONS ---------------- */}

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


            {/* ---------------- PATENTS ---------------- */}

            <Route
              path="/profile/patents"
              element={<Patents />}
            />


            {/* ---------------- FUNDING ---------------- */}

            <Route
              path="/funding"
              element={<Funding />}
            />

            <Route
              path="/grant-prediction/:fundingId"
              element={<GrantPrediction />}
            />


            {/* ---------------- ANALYTICS ---------------- */}

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
            UNKNOWN ROUTE
        ===================================================== */}

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

      </Routes>

    </BrowserRouter>
  );
}


export default App;