import { useEffect, useState } from "react";
import { CheckCircle2, Save, Trash2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import api from "../../api/axios";
import { createStartupProfile, getStartupProfile, updateStartupProfile } from "../../api/startup";

const initial = {
  startup_name: "", tagline: "", industry: "", stage: "Idea", founded_year: "", funding_stage: "Bootstrapped",
  startup_email: "", phone_number: "", website: "", linkedin_url: "", location: "", description: "",
  problem_statement: "", solution: "", technology_stack: "", research_interests: "", funding_needed: "",
  team_size: 1, pitch_deck_url: "", logo_url: "",
};

export default function StartupProfile() {
  const [form, setForm] = useState(initial);
  const [exists, setExists] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [deleting, setDeleting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    getStartupProfile().then((data) => { setForm({ ...initial, ...data }); setExists(true); }).catch(() => setExists(false)).finally(() => setLoading(false));
  }, []);

  function change(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: name === "team_size" || name === "founded_year" ? value : value }));
  }

  async function submit(event) {
    event.preventDefault();
    setSaving(true); setMessage("");
    try {
      const payload = { ...form, team_size: Number(form.team_size || 1), founded_year: Number(form.founded_year || new Date().getFullYear()) };
      const saved = exists ? await updateStartupProfile(payload) : await createStartupProfile(payload);
      setForm({ ...initial, ...saved }); setExists(true); setMessage("Startup profile saved successfully.");
    } catch (error) {
      setMessage(error.response?.data?.detail || "Unable to save startup profile.");
    } finally { setSaving(false); }
  }

  async function deleteAccount() {
    const confirmed = window.confirm(
      "Delete your account permanently? This will remove your account and associated startup data. This action cannot be undone."
    );

    if (!confirmed) return;

    try {
      setDeleting(true);
      await api.delete("/auth/account");
      localStorage.clear();
      navigate("/login", { replace: true });
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          error.message ||
          "Unable to delete your account."
      );
    } finally {
      setDeleting(false);
    }
  }

  if (loading) return <div className="startup-loading">Loading startup profile...</div>;

  return (
    <div className="startup-page">
      <div className="startup-page-header"><span className="startup-eyebrow">STARTUP MANAGEMENT</span><h1>Startup Profile</h1><p>Maintain the information used for researcher discovery, startup collaboration and funding matching.</p></div>
      {message && <div className="startup-success-alert"><CheckCircle2 size={17} /> {message}</div>}
      <form onSubmit={submit} className="startup-form-panel">
        <FormSection title="Startup Details" text="Basic information about your company and current stage.">
          <Field label="Startup Name" name="startup_name" value={form.startup_name} onChange={change} required />
          <Field label="Tagline" name="tagline" value={form.tagline} onChange={change} />
          <Field label="Industry" name="industry" value={form.industry} onChange={change} placeholder="AI, Healthcare, FinTech..." />
          <Select label="Startup Stage" name="stage" value={form.stage} onChange={change} options={["Idea", "Prototype", "MVP", "Seed", "Series A", "Growth"]} />
          <Field label="Founded Year" name="founded_year" type="number" value={form.founded_year} onChange={change} />
          <Select label="Funding Stage" name="funding_stage" value={form.funding_stage} onChange={change} options={["Bootstrapped", "Angel", "Seed", "Series A", "Series B", "Growth"]} />
        </FormSection>
        <FormSection title="Contact Information" text="Public contact details that can help potential collaborators reach you.">
          <Field label="Email" name="startup_email" type="email" value={form.startup_email} onChange={change} />
          <Field label="Phone" name="phone_number" value={form.phone_number} onChange={change} />
          <Field label="Website" name="website" value={form.website} onChange={change} />
          <Field label="LinkedIn" name="linkedin_url" value={form.linkedin_url} onChange={change} />
          <Field label="Location" name="location" value={form.location} onChange={change} />
        </FormSection>
        <FormSection title="Problem & Solution" text="Explain what problem your startup solves and how your solution works.">
          <TextArea label="Startup Description" name="description" value={form.description} onChange={change} full />
          <TextArea label="Problem Statement" name="problem_statement" value={form.problem_statement} onChange={change} full />
          <TextArea label="Solution" name="solution" value={form.solution} onChange={change} full />
        </FormSection>
        <FormSection title="Innovation & Funding" text="These fields improve matching with researchers and funding opportunities.">
          <TextArea label="Technology Stack" name="technology_stack" value={form.technology_stack} onChange={change} placeholder="Python, FastAPI, React, TensorFlow..." />
          <TextArea label="Research Interests" name="research_interests" value={form.research_interests} onChange={change} placeholder="Generative AI, computer vision, climate tech..." />
          <Field label="Funding Needed" name="funding_needed" value={form.funding_needed} onChange={change} placeholder="₹50 lakh" />
          <Field label="Team Size" name="team_size" type="number" min="1" value={form.team_size} onChange={change} />
          <Field label="Pitch Deck URL" name="pitch_deck_url" value={form.pitch_deck_url} onChange={change} />
          <Field label="Logo URL" name="logo_url" value={form.logo_url} onChange={change} />
        </FormSection>
        <div className="startup-form-footer"><span>{exists ? "Profile is already created. Changes will update it." : "Create your startup profile to unlock matching features."}</span><button className="startup-primary-button" disabled={saving}><Save size={17} /> {saving ? "Saving..." : "Save Changes"}</button></div>
      </form>

      <section className="account-danger-zone">
        <div>
          <span className="account-danger-eyebrow">ACCOUNT</span>
          <h2>Delete account</h2>
          <p>
            Permanently delete your account and associated startup data.
            This action cannot be undone.
          </p>
        </div>

        <button
          type="button"
          className="account-danger-button"
          onClick={deleteAccount}
          disabled={deleting}
        >
          <Trash2 size={16} />
          {deleting ? "Deleting..." : "Delete Account"}
        </button>
      </section>
    </div>
  );
}

function FormSection({ title, text, children }) { return <section className="startup-form-section"><div className="startup-form-section-heading"><h2>{title}</h2><p>{text}</p></div><div className="startup-form-grid">{children}</div></section>; }
function Field({ label, name, value, onChange, type = "text", placeholder = "", required = false, min }) { return <label className="startup-field"><span>{label}</span><input type={type} name={name} value={value ?? ""} onChange={onChange} placeholder={placeholder} required={required} min={min} /></label>; }
function TextArea({ label, name, value, onChange, placeholder = "", full = false }) { return <label className={`startup-field ${full ? "full" : ""}`}><span>{label}</span><textarea name={name} value={value ?? ""} onChange={onChange} placeholder={placeholder} rows={full ? 4 : 3} /></label>; }
function Select({ label, name, value, onChange, options }) { return <label className="startup-field"><span>{label}</span><select name={name} value={value} onChange={onChange}>{options.map((option) => <option key={option}>{option}</option>)}</select></label>; }
