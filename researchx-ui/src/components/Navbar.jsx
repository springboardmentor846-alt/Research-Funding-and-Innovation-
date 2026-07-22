import { NavLink, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();

  return (
    <nav className="flex justify-between items-center px-10 py-6 border-b border-slate-800 bg-slate-950">

      {/* Logo */}

      <div>
        <h1 className="text-3xl font-bold text-cyan-400">
          ResearchX
        </h1>

        <p className="text-slate-400 text-sm">
          AI Research Platform
        </p>
      </div>

      {/* Navigation */}

      <div className="flex items-center gap-8">

        <NavLink
          to="/"
          className="text-slate-300 hover:text-cyan-400 transition"
        >
          Home
        </NavLink>

        <button
          onClick={() => navigate("/login")}
          className="bg-cyan-500 hover:bg-cyan-600 text-black font-semibold px-6 py-2 rounded-lg transition"
        >
          Login
        </button>

      </div>

    </nav>
  );
}