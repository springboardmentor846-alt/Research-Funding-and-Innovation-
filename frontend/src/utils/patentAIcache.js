/**
 * localStorage-backed cache for the Patent Intelligence Dashboard.
 *
 * Why localStorage (and not sessionStorage)?
 * ------------------------------------------
 * A researcher's "current patent of interest" tends to survive across
 * page reloads and tab switches — they may close the laptop and reopen
 * the same patent hours later.  The dashboard payloads are also small
 * (a few KB each) so persisting them in localStorage is fine.  Unlike
 * the user-dashboard cache, the patent cache is keyed by patent_number,
 * not user, so the same dashboard survives a logout/login cycle.
 *
 * Invalidation contract
 * ---------------------
 * The cache is invalidated by:
 *   - explicit ``Explain Again`` button (drops the cached AI summary)
 *   - explicit ``Refresh`` action (drops everything for this patent)
 *   - patent_number change (different patent → different key)
 *
 * Storage shape
 * -------------
 *   key:   ``patent-dashboard:<patent_number>:<section>``
 *   value: JSON ``{ ts: number, data: <payload> }``
 *
 * ``ts`` is informational only — localStorage is the TTL.
 */
const PREFIX = "patent-dashboard:";

// Sections are keyed separately so we can refresh just the AI summary
// when the researcher clicks "Explain Again" without losing the overview.
const VALID_SECTIONS = new Set([
  "overview",
  "aiSummary",
  "innovationScores",
  "techGap",
  "commercialApplications",
  "recommendations",
  "relatedFunding",
  "relatedPublications",
  "similarPatents",
  "techTrend",
]);

function key(patentNumber, section) {
  if (!patentNumber || !section) return null;
  if (!VALID_SECTIONS.has(section)) return null;
  return `${PREFIX}${patentNumber}:${section}`;
}

/**
 * Read the cached payload for ``(patentNumber, section)``.
 * Returns ``null`` when no cache entry exists, when the key is invalid,
 * or when storage is unavailable (private mode, quota exceeded).
 *
 * @param {string} patentNumber
 * @param {string} section one of VALID_SECTIONS
 * @returns {{ ts: number, data: any } | null}
 */
export function getCachedSection(patentNumber, section) {
  if (typeof window === "undefined") return null;
  try {
    const k = key(patentNumber, section);
    if (!k) return null;
    const raw = window.localStorage.getItem(k);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object" || !parsed.data) return null;
    return { ts: parsed.ts || 0, data: parsed.data };
  } catch {
    // Malformed JSON, quota error, or storage disabled — treat as miss.
    return null;
  }
}

/**
 * Write a payload for ``(patentNumber, section)`` to localStorage.
 * Errors are swallowed silently — losing the cache is non-fatal; the
 * next render simply refetches.
 *
 * @param {string} patentNumber
 * @param {string} section
 * @param {any} data
 */
export function setCachedSection(patentNumber, section, data) {
  if (typeof window === "undefined") return;
  const k = key(patentNumber, section);
  if (!k) return;
  try {
    window.localStorage.setItem(
      k,
      JSON.stringify({ ts: Date.now(), data })
    );
  } catch {
    // Quota exceeded, private mode, disabled storage — ignore.
  }
}

/**
 * Drop a single cached section (used by "Explain Again" etc.).
 *
 * @param {string} patentNumber
 * @param {string} section
 */
export function invalidateSection(patentNumber, section) {
  if (typeof window === "undefined") return;
  const k = key(patentNumber, section);
  if (!k) return;
  try {
    window.localStorage.removeItem(k);
  } catch {
    // Storage disabled — nothing to do.
  }
}

/**
 * Drop every cached section for one patent.  Used by the "Refresh"
 * action — cheaper than iterating because we know the prefix.
 *
 * @param {string} patentNumber
 */
export function invalidatePatent(patentNumber) {
  if (typeof window === "undefined" || !patentNumber) return;
  const prefix = `${PREFIX}${patentNumber}:`;
  try {
    const toRemove = [];
    for (let i = 0; i < window.localStorage.length; i++) {
      const k = window.localStorage.key(i);
      if (k && k.startsWith(prefix)) toRemove.push(k);
    }
    toRemove.forEach((k) => window.localStorage.removeItem(k));
  } catch {
    // Storage disabled — nothing to do.
  }
}

/**
 * Drop every Patent Intelligence Dashboard cache entry.  Used on logout
 * so a different researcher logging in on the same browser does not see
 * the previous user's cached patent summaries.
 */
export function clearAllPatentCaches() {
  if (typeof window === "undefined") return;
  try {
    const toRemove = [];
    for (let i = 0; i < window.localStorage.length; i++) {
      const k = window.localStorage.key(i);
      if (k && k.startsWith(PREFIX)) toRemove.push(k);
    }
    toRemove.forEach((k) => window.localStorage.removeItem(k));
  } catch {
    // Storage disabled — nothing to do.
  }
}

/** Exposed for tests / debugging. */
export const __test = { PREFIX, VALID_SECTIONS };
