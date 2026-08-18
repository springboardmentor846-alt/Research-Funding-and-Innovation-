"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const router = useRouter();

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    role: "researcher",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/auth/register",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },

          // IMPORTANT:
          // Backend expects "full_name", not "name"
          body: JSON.stringify({
            full_name: formData.name,
            email: formData.email,
            password: formData.password,
            role: formData.role,
          }),
        }
      );

      const data = await response.json();

      // Handle FastAPI errors
      if (!response.ok) {
        if (Array.isArray(data.detail)) {
          setError(
            data.detail
              .map(
                (error: any) =>
                  `${error.loc?.join(".")}: ${error.msg}`
              )
              .join(", ")
          );
        } else {
          setError(
            typeof data.detail === "string"
              ? data.detail
              : "Registration failed"
          );
        }

        return;
      }

      // Success
      setSuccess(
        "Registration successful! Redirecting to login..."
      );

      setTimeout(() => {
        router.push("/login");
      }, 1500);
    } catch (err) {
      console.error("Registration error:", err);

      setError(
        "Cannot connect to backend. Make sure FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#06111f] text-white flex items-center justify-center px-6 py-16">

      <div className="w-full max-w-2xl">

        {/* Logo */}
        <div className="text-center mb-10">

          <button
            onClick={() => router.push("/")}
            className="text-3xl font-bold tracking-tight"
          >
            <span className="text-cyan-400">Inno</span>
            <span className="text-white">Bridge</span>
            <span className="text-indigo-400">-AI</span>
          </button>

          <h1 className="mt-8 text-4xl md:text-5xl font-bold tracking-tight">
            Create your account
          </h1>

          <p className="mt-4 text-lg md:text-xl text-slate-400">
            Join the InnoBridge-AI innovation platform
          </p>

        </div>

        {/* Registration Card */}
        <div className="rounded-3xl border border-slate-700 bg-[#0c1929] p-8 md:p-12 shadow-2xl">

          <form
            onSubmit={handleRegister}
            className="space-y-7"
          >

            {/* Full Name */}
            <div>

              <label className="block text-lg font-semibold mb-3">
                Full Name
              </label>

              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Enter your full name"
                required
                className="w-full h-14 rounded-xl bg-[#071321] border border-slate-600 px-5 text-lg text-white placeholder:text-slate-500 outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
              />

            </div>

            {/* Email */}
            <div>

              <label className="block text-lg font-semibold mb-3">
                Email Address
              </label>

              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="Enter your email address"
                required
                className="w-full h-14 rounded-xl bg-[#071321] border border-slate-600 px-5 text-lg text-white placeholder:text-slate-500 outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
              />

            </div>

            {/* Password */}
            <div>

              <label className="block text-lg font-semibold mb-3">
                Password
              </label>

              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Create a strong password"
                required
                className="w-full h-14 rounded-xl bg-[#071321] border border-slate-600 px-5 text-lg text-white placeholder:text-slate-500 outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
              />

            </div>

            {/* Account Type */}
            <div>

              <label className="block text-lg font-semibold mb-3">
                Account Type
              </label>

              <select
                name="role"
                value={formData.role}
                onChange={handleChange}
                className="w-full h-14 rounded-xl bg-[#071321] border border-slate-600 px-5 text-lg text-white outline-none transition focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
              >

               <option value="Researcher">Researcher</option>
<option value="Startup Founder">Startup Founder</option>
<option value="Investor">Investor</option>
<option value="University">University</option>
<option value="Funding Agency">Funding Agency</option>
<option value="Industry Partner">Industry Partner</option>
              </select>

            </div>

            {/* Error */}
            {error && (
              <div className="rounded-xl border border-red-500/40 bg-red-500/10 px-5 py-4 text-base text-red-400">
                {error}
              </div>
            )}

            {/* Success */}
            {success && (
              <div className="rounded-xl border border-green-500/40 bg-green-500/10 px-5 py-4 text-base text-green-400">
                {success}
              </div>
            )}

            {/* Register Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full h-14 rounded-xl bg-cyan-500 text-lg font-bold text-black transition hover:bg-cyan-400 hover:scale-[1.01] disabled:opacity-50 disabled:hover:scale-100"
            >
              {loading
                ? "Creating Account..."
                : "Create Account"}
            </button>

          </form>

          {/* Login */}
          <div className="mt-8 text-center text-lg text-slate-400">

            Already have an account?{" "}

            <button
              onClick={() => router.push("/login")}
              className="font-semibold text-cyan-400 hover:text-cyan-300"
            >
              Login
            </button>

          </div>

        </div>

        {/* Back */}
        <div className="mt-8 text-center">

          <button
            onClick={() => router.push("/")}
            className="text-base text-slate-500 hover:text-white transition"
          >
            ← Back to InnoBridge-AI
          </button>

        </div>

      </div>

    </main>
  );
}