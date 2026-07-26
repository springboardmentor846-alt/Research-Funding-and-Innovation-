import { useEffect, useState } from "react";
import { User, Save } from "lucide-react";
import Layout from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getMyProfile, createProfile, updateProfile } from "@/services/api";

export default function Profile() {
  const [form, setForm] = useState({
    organization: "", designation: "", research_domain: "", keywords: "", biography: "",
  });
  const [exists, setExists]   = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving]   = useState(false);
  const [msg, setMsg]         = useState("");

  useEffect(() => {
    getMyProfile()
      .then((r) => { setForm(r.data); setExists(true); })
      .catch(() => setExists(false))
      .finally(() => setLoading(false));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMsg("");
    try {
      if (exists) {
        await updateProfile(form);
        setMsg("Profile updated successfully.");
      } else {
        await createProfile(form);
        setExists(true);
        setMsg("Profile created successfully.");
      }
    } catch (err) {
      setMsg(err.response?.data?.detail || "Failed to save profile.");
    } finally {
      setSaving(false);
    }
  };

  const fields = [
    { key: "organization",    label: "Organization",    placeholder: "MIT, Stanford…" },
    { key: "designation",     label: "Designation",     placeholder: "Professor, PhD Researcher…" },
    { key: "research_domain", label: "Research Domain", placeholder: "AI, Biotech, Climate…" },
    { key: "keywords",        label: "Keywords (comma-separated)", placeholder: "machine learning, NLP, robotics" },
  ];

  return (
    <Layout>
      <div className="max-w-2xl mx-auto space-y-5">
        <div>
          <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            <User size={20} className="text-blue-600" /> Research Profile
          </h2>
          <p className="text-sm text-slate-500 mt-0.5">
            Your profile powers funding recommendations and eligibility matching
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>{exists ? "Update Profile" : "Create Profile"}</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-4">
                {[1,2,3,4,5].map(i => <div key={i} className="h-10 bg-slate-100 rounded-lg animate-pulse" />)}
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                {fields.map(({ key, label, placeholder }) => (
                  <div key={key}>
                    <Label>{label}</Label>
                    <Input
                      className="mt-1.5"
                      placeholder={placeholder}
                      value={form[key] || ""}
                      onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                      required
                    />
                  </div>
                ))}

                <div>
                  <Label>Biography</Label>
                  <textarea
                    className="mt-1.5 w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
                    rows={4}
                    placeholder="Brief description of your research background…"
                    value={form.biography || ""}
                    onChange={(e) => setForm({ ...form, biography: e.target.value })}
                    required
                  />
                </div>

                {msg && (
                  <div className={`p-3 rounded-lg text-sm ${
                    msg.includes("success")
                      ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                      : "bg-red-50 text-red-600 border border-red-200"
                  }`}>
                    {msg}
                  </div>
                )}

                <Button type="submit" disabled={saving} className="w-full">
                  <Save size={15} />
                  {saving ? "Saving…" : exists ? "Update Profile" : "Create Profile"}
                </Button>
              </form>
            )}
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}
