import React, { useEffect, useState } from "react";
import { alertPreferencesAPI } from "../services/api.js";

/**
 * Alert preferences editor.  Mounted inside Profile.jsx so a user can
 * control which categories fire in-app notifications and how many
 * days before a funding deadline the reminder arrives.
 *
 * Email is exposed as a read-only toggle: the platform does not ship
 * an email provider yet, so the switch stays OFF but is rendered so
 * the architecture is visibly in place for the future.
 */
export default function AlertPreferencesCard() {
  const [prefs, setPrefs] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const res = await alertPreferencesAPI.get();
        if (alive) setPrefs(res.data);
      } catch (err) {
        if (alive)
          setMessage(
            err.response?.data?.detail || "Failed to load preferences"
          );
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  async function save(patch) {
    setSaving(true);
    setMessage("");
    try {
      const res = await alertPreferencesAPI.update(patch);
      setPrefs(res.data);
      setMessage("Preferences saved");
    } catch (err) {
      setMessage(err.response?.data?.detail || "Failed to save preferences");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="card">
        <h3 className="font-semibold text-slate-800 mb-3">🔔 Alert Preferences</h3>
        <div className="text-sm text-slate-500">Loading…</div>
      </div>
    );
  }

  if (!prefs) {
    return (
      <div className="card">
        <h3 className="font-semibold text-slate-800 mb-3">🔔 Alert Preferences</h3>
        <div className="text-sm text-red-600">{message || "Unavailable"}</div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-slate-800">🔔 Alert Preferences</h3>
        {message && (
          <span className="text-xs text-slate-500">{message}</span>
        )}
      </div>

      <div className="grid sm:grid-cols-2 gap-3">
        <Toggle
          label="Funding Opportunities"
          checked={prefs.funding_alerts}
          onChange={(v) => {
            setPrefs({ ...prefs, funding_alerts: v });
            save({ funding_alerts: v });
          }}
          disabled={saving}
        />
        <Toggle
          label="Funding Deadlines"
          checked={prefs.funding_deadline_alerts}
          onChange={(v) => {
            setPrefs({ ...prefs, funding_deadline_alerts: v });
            save({ funding_deadline_alerts: v });
          }}
          disabled={saving}
        />
        <Toggle
          label="Recommendations"
          checked={prefs.recommendation_alerts}
          onChange={(v) => {
            setPrefs({ ...prefs, recommendation_alerts: v });
            save({ recommendation_alerts: v });
          }}
          disabled={saving}
        />
        <Toggle
          label="Patent Intelligence"
          checked={prefs.patent_alerts}
          onChange={(v) => {
            setPrefs({ ...prefs, patent_alerts: v });
            save({ patent_alerts: v });
          }}
          disabled={saving}
        />
        <Toggle
          label="Research Trends"
          checked={prefs.research_trend_alerts}
          onChange={(v) => {
            setPrefs({ ...prefs, research_trend_alerts: v });
            save({ research_trend_alerts: v });
          }}
          disabled={saving}
        />
        <Toggle
          label="System Alerts"
          checked={prefs.system_alerts}
          onChange={(v) => {
            setPrefs({ ...prefs, system_alerts: v });
            save({ system_alerts: v });
          }}
          disabled={saving}
        />
      </div>

      <div className="mt-5 border-t border-slate-100 pt-4">
        <div className="text-sm font-medium text-slate-700 mb-2">
          Notification Channels
        </div>
        <div className="grid sm:grid-cols-2 gap-3">
          <Toggle
            label="In-App Notifications"
            checked={prefs.in_app_enabled}
            onChange={(v) => {
              setPrefs({ ...prefs, in_app_enabled: v });
              save({ in_app_enabled: v });
            }}
            disabled={saving}
          />
          <Toggle
            label="Email Notifications (coming soon)"
            checked={prefs.email_enabled}
            onChange={() => {
              // Disabled — no email provider is wired in this build.
            }}
            disabled
          />
        </div>
      </div>

      <div className="mt-5 border-t border-slate-100 pt-4">
        <div className="text-sm font-medium text-slate-700 mb-2">
          Deadline Reminder
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-600">Notify me</span>
          <input
            type="number"
            min={1}
            max={90}
            value={prefs.deadline_days_before}
            onChange={(e) =>
              setPrefs({
                ...prefs,
                deadline_days_before: Math.max(
                  1,
                  Math.min(90, parseInt(e.target.value, 10) || 1)
                ),
              })
            }
            className="input w-20"
          />
          <span className="text-sm text-slate-600">
            days before a funding deadline
          </span>
          <button
            type="button"
            className="btn-primary text-xs ml-2"
            onClick={() => save({ deadline_days_before: prefs.deadline_days_before })}
            disabled={saving}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}

function Toggle({ label, checked, onChange, disabled }) {
  return (
    <label
      className={`flex items-center justify-between gap-3 p-3 border border-slate-200 rounded-lg ${
        disabled ? "opacity-60" : "hover:bg-slate-50 cursor-pointer"
      }`}
    >
      <span className="text-sm text-slate-700">{label}</span>
      <button
        type="button"
        role="switch"
        aria-checked={!!checked}
        disabled={disabled}
        onClick={() => !disabled && onChange(!checked)}
        className={`relative inline-flex h-6 w-11 flex-shrink-0 items-center rounded-full transition-colors ${
          checked ? "bg-primary-600" : "bg-slate-300"
        } ${disabled ? "cursor-not-allowed" : ""}`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            checked ? "translate-x-6" : "translate-x-1"
          }`}
        />
      </button>
    </label>
  );
}
