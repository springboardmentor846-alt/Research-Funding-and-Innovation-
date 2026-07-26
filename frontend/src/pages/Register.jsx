import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { User, Mail, Lock, GraduationCap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { registerUser } from "@/services/api";

const ROLES = [
  { value: "researcher", label: "Researcher" },
  { value: "startup_founder", label: "Startup Founder" },
  { value: "innovation_manager", label: "Innovation Manager" },
  { value: "administrator", label: "Administrator" },
];

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ full_name: "", email: "", password: "", role: "researcher" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await registerUser(form);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <Card className="w-full max-w-md shadow-2xl rounded-3xl">
        <CardContent className="p-10">
          <div className="flex items-center gap-3 mb-6">
            <GraduationCap size={32} className="text-blue-600" />
            <div>
              <h2 className="text-2xl font-bold">Create Account</h2>
              <p className="text-slate-500 text-sm">Join the research platform</p>
            </div>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label>Full Name</Label>
              <div className="relative mt-1.5">
                <User className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                <Input
                  className="pl-9"
                  placeholder="Dr. John Smith"
                  value={form.full_name}
                  onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                  required
                />
              </div>
            </div>

            <div>
              <Label>Email</Label>
              <div className="relative mt-1.5">
                <Mail className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                <Input
                  className="pl-9"
                  placeholder="researcher@email.com"
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  required
                />
              </div>
            </div>

            <div>
              <Label>Password</Label>
              <div className="relative mt-1.5">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                <Input
                  className="pl-9"
                  type="password"
                  placeholder="Min. 6 characters"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  required
                />
              </div>
            </div>

            <div>
              <Label>Role</Label>
              <select
                className="mt-1.5 w-full border border-slate-200 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={form.role}
                onChange={(e) => setForm({ ...form, role: e.target.value })}
              >
                {ROLES.map((r) => (
                  <option key={r.value} value={r.value}>{r.label}</option>
                ))}
              </select>
            </div>

            <Button className="w-full mt-2" type="submit" disabled={loading}>
              {loading ? "Creating account…" : "Create Account"}
            </Button>

            <p className="text-center text-sm text-slate-500">
              Already have an account?{" "}
              <Link to="/" className="text-blue-600 font-medium">Sign In</Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
