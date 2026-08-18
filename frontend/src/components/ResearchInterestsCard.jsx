import React, { useEffect, useMemo, useRef, useState } from "react";
import { profileAPI } from "../services/api.js";

/**
 * Tag-based editor for the current user's research interests.
 *
 * Features:
 *   - typeahead autosuggest from a predefined domain list
 *   - press Enter or Comma to add a chip
 *   - press Backspace on empty input to remove the last chip
 *   - inline rename (click the chip text)
 *   - per-chip delete (×) button
 *   - case-insensitive dedupe against existing chips
 *   - 20-chip hard cap with an inline notice
 *   - autosuggestions close on outside click or Escape
 *
 * The card persists all changes through the backend (PUT /profile/research-interests
 * bulk, plus POST / PUT / DELETE for inline edits) and notifies the parent via
 * `onChange` so the user object can be refreshed.
 */
export default function ResearchInterestsCard({ interests: initialInterests, predefinedDomains, onChange }) {
  const [chips, setChips] = useState(() => (initialInterests || []).slice());
  const [draft, setDraft] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [editingDraft, setEditingDraft] = useState("");
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState(false);
  const [showSuggest, setShowSuggest] = useState(false);
  const inputRef = useRef(null);
  const wrapRef = useRef(null);

  const MAX = 20;
  const domains = useMemo(
    () => (predefinedDomains || []).map((d) => d).sort((a, b) => a.localeCompare(b)),
    [predefinedDomains]
  );

  // Keep local state in sync if the parent reloads interests (e.g. after
  // refreshUser on the Profile page).
  useEffect(() => {
    setChips(initialInterests || []);
  }, [initialInterests]);

  // Close suggestion popover on outside click
  useEffect(() => {
    function onDoc(e) {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) {
        setShowSuggest(false);
      }
    }
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  const existingNamesLower = useMemo(
    () => new Set(chips.map((c) => (c.name || "").toLowerCase())),
    [chips]
  );

  const suggestions = useMemo(() => {
    const q = draft.trim().toLowerCase();
    if (!q) return [];
    return domains
      .filter((d) => d.toLowerCase().includes(q) && !existingNamesLower.has(d.toLowerCase()))
      .slice(0, 6);
  }, [draft, domains, existingNamesLower]);

  function flash(text, kind = "info") {
    setMessage({ text, kind });
    setTimeout(() => setMessage(""), 2400);
  }

  function addChip(rawName) {
    const name = (rawName || "").trim();
    if (!name) return;
    if (chips.length >= MAX) {
      flash(`Maximum ${MAX} interests`, "error");
      return;
    }
    if (existingNamesLower.has(name.toLowerCase())) {
      flash(`"${name}" already added`, "error");
      return;
    }
    const isCustom = !domains.some((d) => d.toLowerCase() === name.toLowerCase());
    const chip = {
      id: `local-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
      name,
      is_custom: isCustom,
      source: isCustom ? "custom" : "predefined",
      _local: true,
    };
    setChips((cs) => [...cs, chip]);
    setDraft("");
    setShowSuggest(false);
  }

  function removeChip(id) {
    setChips((cs) => cs.filter((c) => c.id !== id));
  }

  function startEdit(chip) {
    setEditingId(chip.id);
    setEditingDraft(chip.name);
  }

  function commitEdit(id) {
    const newName = (editingDraft || "").trim();
    if (!newName) {
      cancelEdit();
      return;
    }
    setChips((cs) =>
      cs.map((c) => {
        if (c.id !== id) return c;
        const isCustom = !domains.some((d) => d.toLowerCase() === newName.toLowerCase());
        return { ...c, name: newName, is_custom: isCustom, source: isCustom ? "custom" : "predefined" };
      })
    );
    setEditingId(null);
    setEditingDraft("");
  }

  function cancelEdit() {
    setEditingId(null);
    setEditingDraft("");
  }

  function onKeyDown(e) {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addChip(draft);
    } else if (e.key === "Backspace" && draft === "" && chips.length > 0) {
      // pop last chip
      setChips((cs) => cs.slice(0, -1));
    } else if (e.key === "Escape") {
      setShowSuggest(false);
    }
  }

  async function persist() {
    setSaving(true);
    setMessage("");
    try {
      // Bulk replace is the simplest contract; backend dedupes + caps.
      const names = chips.map((c) => c.name);
      const res = await profileAPI.replaceResearchInterests(names);
      const fresh = res.data.items || [];
      setChips(fresh);
      flash("Research interests saved", "success");
      onChange && onChange(fresh);
    } catch (err) {
      flash(err.response?.data?.detail || "Failed to save", "error");
    } finally {
      setSaving(false);
    }
  }

  const atCap = chips.length >= MAX;
  const messageClasses = !message
    ? ""
    : message.kind === "error"
    ? "text-red-600 text-sm"
    : message.kind === "success"
    ? "text-green-700 text-sm"
    : "text-slate-600 text-sm";

  return (
    <div className="card">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div>
          <h3 className="font-semibold text-slate-800">🔬 Research Interests</h3>
          <p className="text-xs text-slate-500 mt-1">
            Pick from the predefined list or type your own. The AI recommender
            uses these together with your publications to score funding matches.
          </p>
        </div>
        <span className="text-xs text-slate-500 whitespace-nowrap">
          {chips.length} / {MAX}
        </span>
      </div>

      {/* Chip cloud */}
      <div className="flex flex-wrap gap-2 mb-3">
        {chips.length === 0 ? (
          <span className="text-sm text-slate-400 italic">No interests yet. Add one below.</span>
        ) : (
          chips.map((c) => {
            const isEditing = editingId === c.id;
            return (
              <span
                key={c.id}
                className={
                  c.is_custom
                    ? "badge-purple inline-flex items-center gap-1"
                    : "badge-primary inline-flex items-center gap-1"
                }
              >
                {isEditing ? (
                  <input
                    autoFocus
                    value={editingDraft}
                    onChange={(e) => setEditingDraft(e.target.value)}
                    onBlur={() => commitEdit(c.id)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") commitEdit(c.id);
                      else if (e.key === "Escape") cancelEdit();
                    }}
                    className="bg-transparent outline-none text-xs w-32"
                  />
                ) : (
                  <span
                    role="button"
                    tabIndex={0}
                    onClick={() => startEdit(c)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") startEdit(c);
                    }}
                    className="cursor-text"
                    title="Click to rename"
                  >
                    {c.name}
                  </span>
                )}
                <button
                  type="button"
                  onClick={() => removeChip(c.id)}
                  className="ml-1 text-xs opacity-70 hover:opacity-100"
                  aria-label={`Remove ${c.name}`}
                  title="Remove"
                >
                  ×
                </button>
              </span>
            );
          })
        )}
      </div>

      {/* Typeahead input */}
      <div className="relative" ref={wrapRef}>
        <input
          ref={inputRef}
          type="text"
          value={draft}
          onChange={(e) => {
            setDraft(e.target.value);
            setShowSuggest(true);
          }}
          onFocus={() => setShowSuggest(true)}
          onKeyDown={onKeyDown}
          placeholder={
            atCap
              ? `You have reached the ${MAX}-interest limit. Remove one to add another.`
              : "Type an interest, press Enter or ,"
          }
          disabled={atCap}
          className="input disabled:bg-slate-50 disabled:text-slate-400"
        />
        {showSuggest && suggestions.length > 0 && (
          <ul className="absolute z-10 mt-1 w-full max-h-56 overflow-auto bg-white border border-slate-200 rounded-lg shadow-lg">
            {suggestions.map((s) => (
              <li key={s}>
                <button
                  type="button"
                  onMouseDown={(e) => {
                    // prevent input blur
                    e.preventDefault();
                  }}
                  onClick={() => addChip(s)}
                  className="block w-full text-left px-3 py-2 text-sm hover:bg-slate-50"
                >
                  {s}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="flex items-center justify-between mt-3 gap-3 flex-wrap">
        <div className="text-xs text-slate-500">
          Tip: press <kbd className="px-1 border border-slate-200 rounded">Enter</kbd> or{" "}
          <kbd className="px-1 border border-slate-200 rounded">,</kbd> to add. Click a chip to rename.
        </div>
        <button
          onClick={persist}
          disabled={saving}
          className="btn-primary text-sm"
        >
          {saving ? "Saving..." : "Save Interests"}
        </button>
      </div>

      {message && <div className={`mt-2 ${messageClasses}`}>{message.text}</div>}
    </div>
  );
}