import { Routes, Route, Navigate } from "react-router-dom";

import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import ResearchProfile from "./pages/ResearchProfile";
import Funding from "./pages/Funding";
import Papers from "./pages/Papers";
import Collaboration from "./pages/Collaboration";
import TechnologyAI from "./pages/TechnologyAI";
import Patent from "./pages/Patent";
import Commercialization from "./pages/Commercialization";

function App() {
    return (
        <Routes>

            <Route
                path="/"
                element={<Landing />}
            />

            <Route
                path="/login"
                element={<Login />}
            />

            <Route
                path="/register"
                element={<Register />}
            />

            <Route
                path="/dashboard"
                element={<Dashboard />}
            />

            <Route
                path="/research-profile"
                element={<ResearchProfile />}
            />

            <Route
                path="/funding"
                element={<Funding />}
            />

            <Route
                path="/papers"
                element={<Papers />}
            />

            <Route
                path="/collaboration"
                element={<Collaboration />}
            />

            <Route
                path="/technology-ai"
                element={<TechnologyAI />}
            />

            <Route
                path="/patents"
                element={<Patent />}
            />

            <Route
                path="/commercialization"
                element={<Commercialization />}
            />

        </Routes>
    );
}

export default App;