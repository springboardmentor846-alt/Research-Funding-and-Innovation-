import React, { useEffect, useState } from "react";
import { adminAPI } from "../../services/api.js";
import {
  PageLoader,
  ErrorBanner,
  EmptyState,
  Badge,
  ConfirmDialog,
  useToasts,
  ToastStack,
  Field,
} from "../../components/admin/ui.jsx";

/**
 * System Settings — admin-only platform configuration.
 *
 * Sections:
 *   1. Platform Configuration  — name, support email, registration, maintenance
 *   2. Funding Categories        — add / remove categorical labels used by funding records
 *   3. Research Domains          — add / remove research domains used across the platform
 *   4. AI Recommendation Config  — top_k, similarity threshold, rule/similarity weights, enable
 *   5. Security / Session        — session timeout, max pagination size
 *
 * NOTE: This page is a *console* — it does NOT let the admin assign user roles,
 * it does NOT add publications/patents on behalf of researchers, and it does
 * NOT issue personalized AI recommendations to the admin.
 */

function TagInput({ items, onAdd, onRemove, placeholder, validate }) {
  const [draft, setDraft] = useState("");

  function submit(e) {
    e?.preventDefault();
    const value = draft.trim();
    if (!value) return;
    if (validate && !validate(value)) return;
    onAdd(value);
    setDraft("");
  }

  return (
    <form onSubmit={submit} className="space-y-2">
      <div className="flex flex-wrap gap-2">
        {items.length === 0 ? (
          <span className="text-xs text-slate-400">No items yet</span>
        ) : (
          items.map((it) => (
            <span
              key={it}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
            >
              {it}
              <button
                type="button"
                onClick={() => onRemove(it)}
                className="text-primary-700 hover:text-primary-900"
                aria-label={`Remove ${it}`}
              >
                ✕
              </button>
            </span>
          ))
        )}
      </div>
      <div className="flex gap-2">
        <input
          className="input flex-1"
          placeholder={placeholder}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
        />
        <button type="submit" className="btn-primary text-sm">
          + Add
        </button>
      </div>
    </form>
  );
}

function Section({ title, description, children, badge }) {
  return (
    <div className="card">
      <div className="flex items-start justify-between gap-3 mb-4">
        <div>
          <h3 className="font-semibold text-slate-800">{title}</h3>
          {description && (
            <p className="text-sm text-slate-500 mt-0.5">{description}</p>
          )}
        </div>
        {badge}
      </div>
      {children}
    </div>
  );
}

export default function SystemSettings() {
  const [settings, setSettings] = useState(null);
  const [draft, setDraft] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const [confirm, setConfirm] = useState(null);
  const { toasts, pushToast, dismissToast } = useToasts();

  /**
 * The backend stores the AI weights as `ai_config.recommender_weights` but the
 * form binds to top-level `ai_config.publication_weight` / `interest_weight`
 * (so the labels line up with the rest of the form). This helper moves the
 * nested values up onto `ai_config` so that every render can read them from
 * one place and the round-trip save/load works without the form going blank.
 *
 * It is a pure transformation — it does not mutate the original object.
 */
function normaliseAISettings(settingsObj) {
  if (!settingsObj) return settingsObj;
  const ai = { ...(settingsObj.ai_config || {}) };
  const rw = ai.recommender_weights || {};
  if (ai.publication_weight === undefined && rw.publication_similarity !== undefined) {
    ai.publication_weight = rw.publication_similarity;
  }
  if (ai.interest_weight === undefined && rw.user_interests !== undefined) {
    ai.interest_weight = rw.user_interests;
  }
  // Also lift the threshold/min down into the flat fields the form binds to,
  // so the inputs reflect the persisted values on a fresh load.
  if (ai.similarity_threshold === undefined && rw.similarity_threshold !== undefined) {
    ai.similarity_threshold = rw.similarity_threshold;
  }
  if (ai.min_final_score === undefined && rw.min_final_score !== undefined) {
    ai.min_final_score = rw.min_final_score;
  }
  return { ...settingsObj, ai_config: ai };
}

async function load() {
    setLoading(true);
    setError("");
    try {
      const res = await adminAPI.getSettings();
      const normalised = normaliseAISettings(res.data);
      setSettings(normalised);
      setDraft(normalised);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load settings");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function updateDraft(name, value) {
    setDraft((d) => ({ ...d, [name]: value }));
  }

  function updateAI(name, value) {
    setDraft((d) => ({ ...d, ai_config: { ...(d.ai_config || {}), [name]: value } }));
  }

  async function savePlatform(e) {
    e?.preventDefault();
    setSaving(true);
    try {
      const payload = {
        platform_name: draft.platform_name,
        support_email: draft.support_email,
        maintenance_mode: draft.maintenance_mode,
        allow_registration: draft.allow_registration,
        default_user_role: draft.default_user_role,
        session_timeout_minutes: Number(draft.session_timeout_minutes) || 60,
        max_pagination_size: Number(draft.max_pagination_size) || 200,
      };
      const res = await adminAPI.updateSettings(payload);
      const normalised = normaliseAISettings(res.data);
      setSettings(normalised);
      setDraft(normalised);
      pushToast("Platform settings saved", "success");
    } catch (err) {
      pushToast(err.response?.data?.detail || "Failed to save settings", "error");
    } finally {
      setSaving(false);
    }
  }

  async function saveAI(e) {
    e?.preventDefault();
    setSaving(true);
    try {
      const ac = draft.ai_config || {};
      // The two real signals (publication_similarity 60%, user_interests 40%)
      // are the only ones the v2 engine uses to combine the final score.
      // The other keys (rule_weight, similarity_weight, eligibility) are kept
      // here for transparency and admin tuning of the legacy view.
      const pubWeight = Number(ac.publication_weight) || 0.6;
      const intWeight = Number(ac.interest_weight) || 0.4;
      const topK = Math.max(5, Math.min(50, Number(ac.recommender_top_k) || 10));
      const payload = {
        ai_config: {
          recommender_top_k: topK,
          similarity_threshold:
            ac.similarity_threshold === "" || ac.similarity_threshold == null
              ? 0.08
              : Number(ac.similarity_threshold),
          min_final_score:
            ac.min_final_score === "" || ac.min_final_score == null
              ? 0.05
              : Number(ac.min_final_score),
          enabled: Boolean(ac.enabled),
          // Per-signal weights consumed by the recommender.
          recommender_weights: {
            publication_similarity: pubWeight,
            user_interests: intWeight,
            similarity_threshold:
              ac.similarity_threshold === "" || ac.similarity_threshold == null
                ? 0.08
                : Number(ac.similarity_threshold),
            min_final_score:
              ac.min_final_score === "" || ac.min_final_score == null
                ? 0.05
                : Number(ac.min_final_score),
          },
        },
      };
      const res = await adminAPI.updateSettings(payload);
      const normalised = normaliseAISettings(res.data);
      setSettings(normalised);
      setDraft(normalised);
      pushToast("AI configuration saved", "success");
    } catch (err) {
      pushToast(err.response?.data?.detail || "Failed to save AI config", "error");
    } finally {
      setSaving(false);
    }
  }

  async function addCategory(name) {
    try {
      const res = await adminAPI.addFundingCategory(name);
      const normalised = normaliseAISettings(res.data);
      setSettings(normalised);
      setDraft(normalised);
      pushToast(`Category "${name}" added`, "success");
    } catch (err) {
      pushToast(err.response?.data?.detail || "Failed to add category", "error");
    }
  }

  async function removeCategory(name) {
    try {
      const res = await adminAPI.removeFundingCategory(name);
      const normalised = normaliseAISettings(res.data);
      setSettings(normalised);
      setDraft(normalised);
      pushToast(`Category "${name}" removed`, "success");
    } catch (err) {
      pushToast(err.response?.data?.detail || "Failed to remove category", "error");
    }
  }

  async function addDomain(name) {
    try {
      const res = await adminAPI.addResearchDomain(name);
      const normalised = normaliseAISettings(res.data);
      setSettings(normalised);
      setDraft(normalised);
      pushToast(`Domain "${name}" added`, "success");
    } catch (err) {
      pushToast(err.response?.data?.detail || "Failed to add domain", "error");
    }
  }

  async function removeDomain(name) {
    try {
      const res = await adminAPI.removeResearchDomain(name);
      const normalised = normaliseAISettings(res.data);
      setSettings(normalised);
      setDraft(normalised);
      pushToast(`Domain "${name}" removed`, "success");
    } catch (err) {
      pushToast(err.response?.data?.detail || "Failed to remove domain", "error");
    }
  }

  if (loading && !settings) return <PageLoader label="Loading system settings..." />;
  if (error && !settings) return <ErrorBanner message={error} onRetry={load} />;
  if (!settings || !draft) return null;

  const ai = draft.ai_config || {};
  const isDirtyPlatform =
    JSON.stringify({
      platform_name: settings.platform_name,
      support_email: settings.support_email,
      maintenance_mode: settings.maintenance_mode,
      allow_registration: settings.allow_registration,
      default_user_role: settings.default_user_role,
      session_timeout_minutes: settings.session_timeout_minutes,
      max_pagination_size: settings.max_pagination_size,
    }) !==
    JSON.stringify({
      platform_name: draft.platform_name,
      support_email: draft.support_email,
      maintenance_mode: draft.maintenance_mode,
      allow_registration: draft.allow_registration,
      default_user_role: draft.default_user_role,
      session_timeout_minutes: Number(draft.session_timeout_minutes) || 60,
      max_pagination_size: Number(draft.max_pagination_size) || 200,
    });

  // Compare against `settings.ai_config` AFTER normalise — `normaliseAISettings`
  // copies the recommender_weights values into the flat form fields, so on a
  // clean read these match and isDirtyAI stays false. Otherwise, the form
  // would always claim to be dirty right after a fresh load.
  const savedAi = settings.ai_config || {};
  const isDirtyAI = (() => {
    const draftTopK = Math.max(5, Math.min(50, Number(ai.recommender_top_k) || 10));
    const savedTopK = Math.max(5, Math.min(50, Number(savedAi.recommender_top_k) || 10));
    const draftPub = Number(ai.publication_weight) || 0.6;
    const savedPub = Number(savedAi.publication_weight) || 0.6;
    const draftInt = Number(ai.interest_weight) || 0.4;
    const savedInt = Number(savedAi.interest_weight) || 0.4;
    const draftSim =
      ai.similarity_threshold === "" || ai.similarity_threshold == null
        ? 0.08
        : Number(ai.similarity_threshold);
    const savedSim =
      savedAi.similarity_threshold === "" || savedAi.similarity_threshold == null
        ? 0.08
        : Number(savedAi.similarity_threshold);
    const draftMin =
      ai.min_final_score === "" || ai.min_final_score == null
        ? 0.05
        : Number(ai.min_final_score);
    const savedMin =
      savedAi.min_final_score === "" || savedAi.min_final_score == null
        ? 0.05
        : Number(savedAi.min_final_score);
    return (
      draftTopK !== savedTopK ||
      draftPub !== savedPub ||
      draftInt !== savedInt ||
      draftSim !== savedSim ||
      draftMin !== savedMin ||
      Boolean(savedAi.enabled) !== Boolean(ai.enabled)
    );
  })();

  return (
    <div className="space-y-4">
      <ToastStack toasts={toasts} onDismiss={dismissToast} />

      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">System Settings</h1>
          <p className="text-slate-500 text-sm">
            Platform configuration, taxonomy, and AI engine parameters
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone="primary">v{settings.platform_version}</Badge>
          {settings.maintenance_mode ? (
            <Badge tone="danger">Maintenance Mode</Badge>
          ) : (
            <Badge tone="success">Operational</Badge>
          )}
          {settings.allow_registration ? (
            <Badge tone="blue">Registration Open</Badge>
          ) : (
            <Badge tone="warning">Registration Closed</Badge>
          )}
        </div>
      </div>

      <div className="card bg-slate-50 border-slate-200 text-slate-700 text-sm">
        ℹ Settings here are platform-wide. Admin cannot assign or change user roles — users
        choose their own role at registration. Admin does not receive personalized AI
        recommendations.
      </div>

      {error && <ErrorBanner message={error} onRetry={load} />}

      <div className="grid lg:grid-cols-2 gap-4">
        <Section
          title="Platform Configuration"
          description="Identity, registration policy, and session behaviour."
        >
          <form onSubmit={savePlatform} className="space-y-4">
            <Field label="Platform name" required>
              <input
                className="input"
                value={draft.platform_name || ""}
                onChange={(e) => updateDraft("platform_name", e.target.value)}
                maxLength={120}
              />
            </Field>
            <Field label="Support email">
              <input
                type="email"
                className="input"
                value={draft.support_email || ""}
                onChange={(e) => updateDraft("support_email", e.target.value)}
              />
            </Field>
            <div className="grid sm:grid-cols-2 gap-3">
              <Field
                label="Session timeout (minutes)"
                hint="How long an admin stays signed in without activity"
              >
                <input
                  type="number"
                  min={5}
                  max={1440}
                  className="input"
                  value={draft.session_timeout_minutes ?? 60}
                  onChange={(e) => updateDraft("session_timeout_minutes", e.target.value)}
                />
              </Field>
              <Field
                label="Max pagination size"
                hint="Upper bound for list endpoints"
              >
                <input
                  type="number"
                  min={10}
                  max={500}
                  className="input"
                  value={draft.max_pagination_size ?? 200}
                  onChange={(e) => updateDraft("max_pagination_size", e.target.value)}
                />
              </Field>
            </div>
            <Field label="Default user role" hint="Pre-selected role for new accounts (users can still choose at registration)">
              <select
                className="input"
                value={draft.default_user_role || "researcher"}
                onChange={(e) => updateDraft("default_user_role", e.target.value)}
              >
                <option value="researcher">Researcher</option>
                <option value="startup_founder">Startup Founder</option>
                <option value="innovation_manager">Innovation Manager</option>
                <option value="admin">Admin</option>
              </select>
            </Field>
            <div className="flex flex-wrap items-center gap-6 pt-1">
              <label className="inline-flex items-center gap-2 text-sm text-slate-700">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-slate-300 text-primary-600"
                  checked={Boolean(draft.allow_registration)}
                  onChange={(e) => updateDraft("allow_registration", e.target.checked)}
                />
                Allow new registrations
              </label>
              <label className="inline-flex items-center gap-2 text-sm text-slate-700">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-slate-300 text-red-600"
                  checked={Boolean(draft.maintenance_mode)}
                  onChange={(e) => updateDraft("maintenance_mode", e.target.checked)}
                />
                Maintenance mode
              </label>
            </div>
            <div className="flex justify-end pt-2">
              <button
                type="submit"
                className="btn-primary text-sm"
                disabled={saving || !isDirtyPlatform}
              >
                {saving ? "Saving..." : "Save Platform Settings"}
              </button>
            </div>
          </form>
        </Section>

        <Section
          title="AI Recommendation Engine"
          description="Tune the platform-wide recommendation algorithm."
          badge={
            <Badge tone={ai.enabled ? "success" : "warning"}>
              {ai.enabled ? "Enabled" : "Disabled"}
            </Badge>
          }
        >
          <form onSubmit={saveAI} className="space-y-4">
            <label className="inline-flex items-center gap-2 text-sm text-slate-700">
              <input
                type="checkbox"
                className="h-4 w-4 rounded border-slate-300 text-primary-600"
                checked={Boolean(ai.enabled)}
                onChange={(e) => updateAI("enabled", e.target.checked)}
              />
              Enable AI recommendations
            </label>
            <div className="grid sm:grid-cols-2 gap-3">
              <Field
                label="Top K recommendations"
                hint="How many to surface per user"
              >
                <select
                  className="input"
                  value={String(ai.recommender_top_k ?? 10)}
                  onChange={(e) => updateAI("recommender_top_k", Number(e.target.value))}
                >
                  <option value="5">Top 5</option>
                  <option value="10">Top 10</option>
                  <option value="20">Top 20</option>
                  <option value="30">Top 30</option>
                  <option value="40">Top 40</option>
                  <option value="50">Top 50</option>
                </select>
              </Field>
              <Field
                label="Similarity threshold"
                hint="Min cosine similarity to keep a candidate (0.0 – 1.0)"
              >
                <input
                  type="number"
                  min={0}
                  max={1}
                  step={0.01}
                  className="input"
                  value={ai.similarity_threshold ?? 0.08}
                  onChange={(e) => updateAI("similarity_threshold", e.target.value)}
                />
              </Field>
              <Field
                label="Minimum match score"
                hint="Drop results below this final score (0.0 – 1.0)"
              >
                <input
                  type="number"
                  min={0}
                  max={1}
                  step={0.01}
                  className="input"
                  value={ai.min_final_score ?? 0.05}
                  onChange={(e) => updateAI("min_final_score", e.target.value)}
                />
              </Field>
              <Field
                label="Publication similarity weight"
                hint="Default 0.60 — must sum to 1.0 with the interest weight"
              >
                <input
                  type="number"
                  min={0}
                  max={1}
                  step={0.05}
                  className="input"
                  value={ai.publication_weight ?? 0.6}
                  onChange={(e) => updateAI("publication_weight", e.target.value)}
                />
              </Field>
              <Field
                label="Research interest weight"
                hint="Default 0.40 — must sum to 1.0 with the publication weight"
              >
                <input
                  type="number"
                  min={0}
                  max={1}
                  step={0.05}
                  className="input"
                  value={ai.interest_weight ?? 0.4}
                  onChange={(e) => updateAI("interest_weight", e.target.value)}
                />
              </Field>
            </div>
            <div className="flex justify-end pt-2">
              <button
                type="submit"
                className="btn-primary text-sm"
                disabled={saving || !isDirtyAI}
              >
                {saving ? "Saving..." : "Save AI Configuration"}
              </button>
            </div>
            <p className="text-xs text-slate-500">
              Changes apply on the next recommendation refresh — the server
              does not need to restart. Existing cached recommendations are
              invalidated automatically when this form is saved.
            </p>
          </form>
        </Section>
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <Section
          title="Funding Categories"
          description="Taxonomy of funding opportunity types. Used to filter and label funding records."
        >
          <TagInput
            items={settings.funding_categories || []}
            onAdd={addCategory}
            onRemove={(it) => setConfirm({ kind: "category", item: it })}
            placeholder="e.g. grant, fellowship, accelerator…"
          />
        </Section>

        <Section
          title="Research Domains"
          description="Allowed research domains used across publications, funding, and recommendations."
        >
          <TagInput
            items={settings.research_domains || []}
            onAdd={addDomain}
            onRemove={(it) => setConfirm({ kind: "domain", item: it })}
            placeholder="e.g. Artificial Intelligence…"
          />
        </Section>
      </div>

      <ConfirmDialog
        open={!!confirm}
        title={`Remove ${confirm?.kind === "domain" ? "research domain" : "funding category"}`}
        description={
          confirm
            ? `This will remove "${confirm.item}" from the platform taxonomy. Existing records tagged with it are not modified.`
            : ""
        }
        confirmText="Remove"
        onConfirm={async () => {
          if (!confirm) return;
          if (confirm.kind === "domain") await removeDomain(confirm.item);
          else await removeCategory(confirm.item);
          setConfirm(null);
        }}
        onCancel={() => setConfirm(null)}
      />
    </div>
  );
}
