import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();

    // Temporary Login Credentials
    if (email === "admin@researchx.com" && password === "admin123") {

      // Save Login Status
      localStorage.setItem("isLoggedIn", "true");

      // Redirect to Dashboard
      navigate("/dashboard");

    } else {
      alert("Invalid Email or Password");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950">

      <div className="bg-slate-900 border border-slate-700 rounded-2xl p-10 w-full max-w-md shadow-xl">

        <h1 className="text-4xl font-bold text-cyan-400 text-center">
          ResearchX
        </h1>

        <p className="text-slate-400 text-center mt-2 mb-8">
          Login to continue
        </p>

        <form onSubmit={handleLogin} className="space-y-5">

          {/* Email */}
          <div>
            <label className="text-slate-300">Email</label>

            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full mt-2 p-3 rounded-lg bg-slate-800 border border-slate-700 text-white outline-none"
              required
            />
          </div>

          {/* Password */}
          <div>
            <label className="text-slate-300">Password</label>

            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full mt-2 p-3 rounded-lg bg-slate-800 border border-slate-700 text-white outline-none"
              required
            />
          </div>

          {/* Login Button */}
          <button
            type="submit"
            className="w-full bg-cyan-500 hover:bg-cyan-600 text-black font-semibold py-3 rounded-lg transition"
          >
            Login
          </button>

        </form>

      </div>

    </div>
  );
}