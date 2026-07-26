import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Mail, Lock, Eye, EyeOff, GraduationCap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { loginUser } from "@/services/api";
import { useAuth } from "@/context/AuthContext";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [form, setForm] = useState({ email: "", password: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await loginUser(form.email, form.password);
      login(res.data.access_token, {
        email: form.email,
        role: res.data.role,
      });
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Check credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 grid lg:grid-cols-2">
      {/* LEFT PANEL */}
      <div className="hidden lg:flex bg-gradient-to-br from-slate-900 via-blue-900 to-blue-700 text-white flex-col justify-center px-16">
        <GraduationCap size={70} />
        <h1 className="text-5xl font-bold mt-6">Research Funding Platform</h1>
        <p className="mt-6 text-lg text-slate-200 leading-8">
          Empowering researchers with AI-driven funding discovery,
          publication management, grant tracking and collaboration.
        </p>
        <div className="grid grid-cols-2 gap-5 mt-14">
          {[
            ["250+", "Funding Agencies"],
            ["1200+", "Researchers"],
            ["$50M", "Grants Awarded"],
            ["96%", "Recommendation Accuracy"],
          ].map(([val, label]) => (
            <Card key={label} className="bg-white/10 border-0 text-white">
              <CardContent className="p-6">
                <h2 className="text-3xl font-bold">{val}</h2>
                <p>{label}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* RIGHT PANEL */}
      <div className="flex justify-center items-center p-10">
        <Card className="w-full max-w-md shadow-2xl rounded-3xl">
          <CardContent className="p-10">
            <h2 className="text-3xl font-bold">Welcome Back</h2>
            <p className="text-slate-500 mt-2 mb-8">Sign in to continue</p>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <Label>Email</Label>
                <div className="relative mt-2">
                  <Mail className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                  <Input
                    className="pl-10"
                    placeholder="researcher@email.com"
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div>
                <Label>Password</Label>
                <div className="relative mt-2">
                  <Lock className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
                  <Input
                    type={showPassword ? "text" : "password"}
                    className="pl-10 pr-10"
                    placeholder="Enter password"
                    value={form.password}
                    onChange={(e) => setForm({ ...form, password: e.target.value })}
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-3"
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              <Button className="w-full mt-4" type="submit" disabled={loading}>
                {loading ? "Signing in…" : "Sign In"}
              </Button>

              <div className="flex justify-between text-sm">
                <a href="#" className="text-blue-600">Forgot Password?</a>
                <Link to="/register" className="text-blue-600">Create Account</Link>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
