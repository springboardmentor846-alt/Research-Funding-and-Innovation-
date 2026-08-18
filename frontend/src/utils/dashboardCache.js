/**
 * Session-storage backed cache for the Researcher Dashboard payload.
 *
 * Why sessionStorage (and not localStorage)?
 * ------------------------------------------
 * The dashboard tile shows the researcher's *current session* view.
 * sessionStorage scopes the cache to the browser tab and dies with it,
 * so logging out (or closing the tab) cannot leak the previous user's
 * numbers on the next login.  localStorage would persist across tabs
 * and across logout/login flows, which the spec explicitly forbids.
 *
 * Invalidation contract
 * ---------------------
 * The cache is invalidated by:
 *   - logout (AuthContext removes the user)
 *   - manual "Refresh Recommendations" click (Dashboard calls invalidate
 *     before triggering the network refresh so the cache only ever holds
 *     a payload that matches what the user just saw)
 *   - profile / interests update (call invalidate from those flows)
 *   - browser refresh (sessionStorage is cleared automatically by the
 *     browser when the tab closes; F5 in the same tab keeps the entry
 *     — that is the intended stale-while-revalidate behaviour)
 *
 * Storage shape
 * -------------
 *   key:   ``dashboard:<userId>``
 *   value: JSON ``{ ts: number, data: { overview, patents, fundingStats } }``
 *
 * ``ts`` is informational only — sessionStorage is the TTL.
 */
const PREFIX = "dashboard:";

/** @returns {string|null} */
function key(userId) {
  if (userId == null || userId === "") return null;
  return `${PREFIX}${userId}`;
}

/**
 * Read the cached dashboard payload for ``userId``.
 * Returns ``null`` when no cache entry exists or when storage is
 * unavailable (private mode, quota exceeded, etc.).
 *
 * @param {string|number} userId
 * @returns {{ ts: number, data: any } | null}
 */
export function getCachedDashboard(userId) {
  if (typeof window === "undefined") return null;
  try {
    const k = key(userId);
    if (!k) return null;
    const raw = window.sessionStorage.getItem(k);
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
 * Write the dashboard payload to sessionStorage.  ``data`` is the same
 * shape ``loadDashboard()`` produces:
 *     ``{ ...overview.data, patents: patents.data, fundingStats: fundingStats.data }``
 *
 * Errors are swallowed silently — losing the cache is non-fatal; the
 * next mount will simply refetch.
 *
 * @param {string|number} userId
 * @param {any} data
 */
export function setCachedDashboard(userId, data) {
  if (typeof window === "undefined") return;
  const k = key(userId);
  if (!k) return;
  try {
    window.sessionStorage.setItem(
      k,
      JSON.stringify({ ts: Date.now(), data })
    );
  } catch {
    // Quota exceeded, private mode, disabled storage — ignore.
  }
}

/**
 * Drop the cached payload for ``userId``.  Safe to call when no entry
 * exists.
 *
 * @param {string|number} userId
 */
export function invalidateDashboardCache(userId) {
  if (typeof window === "undefined") return;
  const k = key(userId);
  if (!k) return;
  try {
    window.sessionStorage.removeItem(k);
  } catch {
    // Storage disabled — nothing to do.
  }
}

/**
 * Drop every dashboard cache entry.  Used on logout so a subsequent
 * login as a different user does not briefly see the previous user's
 * numbers from a stale session-tab entry.
 */
export function clearAllDashboardCaches() {
  if (typeof window === "undefined") return;
  try {
    const toRemove = [];
    for (let i = 0; i < window.sessionStorage.length; i++) {
      const k = window.sessionStorage.key(i);
      if (k && k.startsWith(PREFIX)) toRemove.push(k);
    }
    toRemove.forEach((k) => window.sessionStorage.removeItem(k));
  } catch {
    // Storage disabled — nothing to do.
  }
}
