"use client";

import { useState } from "react";
import { apiRequest } from "@/lib/api";

type Patent = {
  lens_id: string;
  title: string;
  applicant: string;
  inventor: string;
  publication_date: string;
  jurisdiction: string;
  legal_status: string;
};

type Bookmark = {
  id: number;
  user_id?: number;
  lens_id: string;
  title: string;
  applicant?: string;
  jurisdiction?: string;
  bookmarked_at?: string;
};

type Analytics = {
  total_patents: number;
  jurisdiction_distribution?: Record<string, number>;
  legal_status_distribution?: Record<string, number>;
  publication_year_distribution?: Record<string, number>;
  top_applicants?: Record<string, number>;
  top_inventors?: Record<string, number>;
};

type TimelineEvent = {
  event: string;
  date: string;
  description?: string;
};

type TimelineResponse = {
  lens_id: string;
  timeline: TimelineEvent[];
};

type AIInsights = {
  summary: string;
  technology_domain: string;
  innovation_score: number;
  novelty_analysis: string;
  commercialization_potential: string;
  market_opportunities: string[];
  recommended_industries: string[];
  key_innovations: string[];
};

export default function PatentIntelligencePage() {
  const [activeTab, setActiveTab] = useState("search");

  const [query, setQuery] = useState("");
  const [searchSize, setSearchSize] = useState(10);

  const [patents, setPatents] = useState<Patent[]>([]);
  const [selectedPatent, setSelectedPatent] =
    useState<Patent | null>(null);

  const [details, setDetails] = useState<any>(null);
  const [similarPatents, setSimilarPatents] =
    useState<Patent[]>([]);

  const [bookmarks, setBookmarks] =
    useState<Bookmark[]>([]);

  const [analytics, setAnalytics] =
    useState<Analytics | null>(null);

  const [compareId1, setCompareId1] =
    useState("");
  const [compareId2, setCompareId2] =
    useState("");

  const [comparison, setComparison] =
    useState<any>(null);

  const [timeline, setTimeline] =
    useState<TimelineResponse | null>(null);

  const [aiInsights, setAiInsights] =
    useState<AIInsights | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [message, setMessage] =
    useState("");

  // ============================================================
  // COMMON
  // ============================================================

  function clearMessages() {
    setError("");
    setMessage("");
  }

  function handleError(err: any) {
    console.error(err);

    setError(
      err?.message ||
        "Something went wrong. Please try again."
    );
  }

  // ============================================================
  // SEARCH
  // ============================================================

  async function searchPatents() {
    if (!query.trim()) {
      setError("Please enter a patent search keyword.");
      return;
    }

    setLoading(true);
    clearMessages();

    try {
      const data = await apiRequest(
        "/patents/search",
        {
          method: "POST",
          body: JSON.stringify({
            query: query.trim(),
            size: searchSize,
          }),
        }
      );

      setPatents(data.results || []);
      setActiveTab("search");

      if (!data.results?.length) {
        setMessage(
          "No patents found for this search."
        );
      }
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // PATENT DETAILS
  // ============================================================

  async function loadPatentDetails(
    patent: Patent
  ) {
    setLoading(true);
    clearMessages();

    try {
      const data = await apiRequest(
        `/patents/${encodeURIComponent(
          patent.lens_id
        )}`
      );

      setSelectedPatent(patent);
      setDetails(data);

      setActiveTab("details");
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // SIMILAR PATENTS
  // ============================================================

  async function loadSimilarPatents(
    patent: Patent
  ) {
    setLoading(true);
    clearMessages();

    try {
      const data = await apiRequest(
        `/patents/${encodeURIComponent(
          patent.lens_id
        )}/similar`
      );

      setSelectedPatent(patent);
      setSimilarPatents(
        data.results || []
      );

      setActiveTab("similar");
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // BOOKMARK
  // ============================================================

  async function bookmarkPatent(
    patent: Patent
  ) {
    clearMessages();

    try {
      const data = await apiRequest(
        "/patents/bookmark",
        {
          method: "POST",
          body: JSON.stringify({
            lens_id: patent.lens_id,
            title: patent.title,
            applicant: patent.applicant,
            jurisdiction: patent.jurisdiction,
          }),
        }
      );

      setMessage(
        data?.message ||
          "Patent bookmarked successfully."
      );
    } catch (err) {
      handleError(err);
    }
  }

  // ============================================================
  // GET BOOKMARKS
  // ============================================================

  async function loadBookmarks() {
    setLoading(true);
    clearMessages();

    try {
      const data = await apiRequest(
        "/patents/bookmarks"
      );

      setBookmarks(
        Array.isArray(data)
          ? data
          : data.bookmarks || []
      );

      setActiveTab("bookmarks");
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // DELETE BOOKMARK
  // ============================================================

  async function removeBookmark(
    bookmarkId: number
  ) {
    clearMessages();

    try {
      const data = await apiRequest(
        `/patents/bookmark/${bookmarkId}`,
        {
          method: "DELETE",
        }
      );

      setMessage(
        data?.message ||
          "Bookmark removed."
      );

      await loadBookmarks();
    } catch (err) {
      handleError(err);
    }
  }

  // ============================================================
  // ANALYTICS
  // ============================================================

  async function loadAnalytics() {
    if (!query.trim()) {
      setError(
        "Enter a search topic first for analytics."
      );
      return;
    }

    setLoading(true);
    clearMessages();

    try {
      const data = await apiRequest(
        "/patents/analytics",
        {
          method: "POST",
          body: JSON.stringify({
            query: query.trim(),
            size: searchSize,
          }),
        }
      );

      setAnalytics(data);
      setActiveTab("analytics");
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // COMPARE
  // ============================================================

  async function comparePatents() {
    if (!compareId1 || !compareId2) {
      setError(
        "Select two patents to compare."
      );
      return;
    }

    if (compareId1 === compareId2) {
      setError(
        "Please select two different patents."
      );
      return;
    }

    setLoading(true);
    clearMessages();

    try {
      const data = await apiRequest(
        "/patents/compare",
        {
          method: "POST",
          body: JSON.stringify({
            lens_id_1: compareId1,
            lens_id_2: compareId2,
          }),
        }
      );

      setComparison(data);
      setActiveTab("compare");
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // TIMELINE
  // ============================================================

  async function loadTimeline(
    patent: Patent
  ) {
    setLoading(true);
    clearMessages();

    try {
      const data = await apiRequest(
        `/patents/${encodeURIComponent(
          patent.lens_id
        )}/timeline`
      );

      setSelectedPatent(patent);
      setTimeline(data);

      setActiveTab("timeline");
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // AI INSIGHTS
  // ============================================================

  async function loadAIInsights(
    patent: Patent
  ) {
    setLoading(true);
    clearMessages();

    try {
      const data = await apiRequest(
        "/patents/ai-insights",
        {
          method: "POST",
          body: JSON.stringify({
            lens_id: patent.lens_id,
          }),
        }
      );

      setSelectedPatent(patent);
      setAiInsights(data);

      setActiveTab("ai");
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // SEARCH RESULT CARD
  // ============================================================

  function PatentCard({
    patent,
  }: {
    patent: Patent;
  }) {
    return (
      <div className="rounded-2xl border border-cyan-500/20 bg-slate-900/70 p-5 shadow-lg transition hover:border-cyan-400/50 hover:shadow-cyan-500/10">
        <div className="flex flex-col gap-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-cyan-400">
                {patent.lens_id}
              </div>

              <h3 className="text-lg font-semibold text-white">
                {patent.title ||
                  "Untitled Patent"}
              </h3>
            </div>

            <span className="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-300">
              {patent.legal_status ||
                "Unknown"}
            </span>
          </div>

          <div className="grid grid-cols-1 gap-3 text-sm text-slate-300 md:grid-cols-3">
            <div>
              <span className="text-slate-500">
                Applicant
              </span>
              <p className="mt-1 text-white">
                {patent.applicant ||
                  "Not available"}
              </p>
            </div>

            <div>
              <span className="text-slate-500">
                Inventor
              </span>
              <p className="mt-1 text-white">
                {patent.inventor ||
                  "Not available"}
              </p>
            </div>

            <div>
              <span className="text-slate-500">
                Jurisdiction
              </span>
              <p className="mt-1 text-white">
                {patent.jurisdiction ||
                  "Not available"}
              </p>
            </div>
          </div>

          <div className="text-sm text-slate-400">
            Publication date:{" "}
            <span className="text-slate-200">
              {patent.publication_date ||
                "Not available"}
            </span>
          </div>

          <div className="flex flex-wrap gap-2 border-t border-slate-800 pt-4">
            <button
              onClick={() =>
                loadPatentDetails(patent)
              }
              className="rounded-lg bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400"
            >
              View Details
            </button>

            <button
              onClick={() =>
                loadSimilarPatents(patent)
              }
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-white transition hover:border-cyan-400"
            >
              Similar
            </button>

            <button
              onClick={() =>
                bookmarkPatent(patent)
              }
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-white transition hover:border-cyan-400"
            >
              ★ Bookmark
            </button>

            <button
              onClick={() =>
                loadTimeline(patent)
              }
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-white transition hover:border-cyan-400"
            >
              Timeline
            </button>

            <button
              onClick={() =>
                loadAIInsights(patent)
              }
              className="rounded-lg border border-purple-500/40 px-4 py-2 text-sm text-purple-300 transition hover:bg-purple-500/10"
            >
              ✨ AI Insights
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ============================================================
  // PAGE
  // ============================================================

  return (
    <main className="min-h-screen bg-[#020617] text-white">
      {/* ======================================================
          HEADER
      ====================================================== */}

      <section className="border-b border-cyan-500/10 bg-slate-950/80">
        <div className="mx-auto max-w-7xl px-6 py-8">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <div className="mb-2 text-sm font-semibold uppercase tracking-[0.3em] text-cyan-400">
                InnoBridge-AI
              </div>

              <h1 className="text-3xl font-bold tracking-tight md:text-4xl">
                Patent Intelligence
              </h1>

              <p className="mt-2 max-w-2xl text-slate-400">
                Discover, analyze, compare and understand
                patents using intelligent patent analytics.
              </p>
            </div>

            <div className="rounded-xl border border-cyan-500/20 bg-cyan-500/5 px-4 py-3">
              <div className="text-xs text-slate-500">
                Data source
              </div>
              <div className="mt-1 font-semibold text-cyan-300">
                Development Patent Dataset
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ======================================================
          SEARCH
      ====================================================== */}

      <section className="mx-auto max-w-7xl px-6 pt-8">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
          <div className="flex flex-col gap-3 md:flex-row">
            <input
              value={query}
              onChange={(e) =>
                setQuery(e.target.value)
              }
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  searchPatents();
                }
              }}
              placeholder="Search patents... e.g. artificial intelligence"
              className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-400"
            />

            <select
              value={searchSize}
              onChange={(e) =>
                setSearchSize(
                  Number(e.target.value)
                )
              }
              className="rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none"
            >
              <option value={5}>
                5 results
              </option>
              <option value={10}>
                10 results
              </option>
              <option value={20}>
                20 results
              </option>
            </select>

            <button
              onClick={searchPatents}
              disabled={loading}
              className="rounded-xl bg-cyan-500 px-6 py-3 font-bold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading
                ? "Searching..."
                : "🔎 Search"}
            </button>
          </div>
        </div>
      </section>

      {/* ======================================================
          MESSAGES
      ====================================================== */}

      <section className="mx-auto max-w-7xl px-6 pt-4">
        {error && (
          <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

        {message && (
          <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300">
            {message}
          </div>
        )}
      </section>

      {/* ======================================================
          NAVIGATION
      ====================================================== */}

      <section className="mx-auto max-w-7xl px-6 pt-6">
        <div className="flex gap-2 overflow-x-auto border-b border-slate-800 pb-2">
          {[
            ["search", "🔎 Search"],
            ["details", "📄 Details"],
            ["similar", "🔗 Similar"],
            ["bookmarks", "★ Bookmarks"],
            ["analytics", "📊 Analytics"],
            ["compare", "⚖️ Compare"],
            ["timeline", "📅 Timeline"],
            ["ai", "✨ AI Insights"],
          ].map(([id, label]) => (
            <button
              key={id}
              onClick={() =>
                setActiveTab(id)
              }
              className={`whitespace-nowrap rounded-lg px-4 py-2 text-sm font-medium transition ${
                activeTab === id
                  ? "bg-cyan-500 text-slate-950"
                  : "bg-slate-900 text-slate-300 hover:bg-slate-800"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </section>

      {/* ======================================================
          CONTENT
      ====================================================== */}

      <section className="mx-auto max-w-7xl px-6 py-8">
        {/* SEARCH */}
        {activeTab === "search" && (
          <div className="space-y-4">
            {patents.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/40 p-12 text-center">
                <div className="text-4xl">
                  🔎
                </div>

                <h2 className="mt-4 text-xl font-semibold">
                  Search for patents
                </h2>

                <p className="mt-2 text-slate-500">
                  Enter a technology, invention or
                  research topic above.
                </p>
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold">
                    Search Results
                  </h2>

                  <span className="text-sm text-slate-500">
                    {patents.length} patents
                  </span>
                </div>

                {patents.map((patent) => (
                  <PatentCard
                    key={patent.lens_id}
                    patent={patent}
                  />
                ))}
              </>
            )}
          </div>
        )}

        {/* DETAILS */}
        {activeTab === "details" && (
          <div>
            {!details ? (
              <EmptyState
                title="No patent selected"
                text="Select a patent from search results."
              />
            ) : (
              <div className="rounded-2xl border border-cyan-500/20 bg-slate-900/60 p-6">
                <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                  <div>
                    <span className="text-xs text-cyan-400">
                      {details.lens_id}
                    </span>

                    <h2 className="mt-2 text-2xl font-bold">
                      {details.title}
                    </h2>
                  </div>

                  <span className="rounded-full bg-cyan-500/10 px-4 py-2 text-sm text-cyan-300">
                    {details.legal_status}
                  </span>
                </div>

                <div className="mt-8 grid gap-5 md:grid-cols-2">
                  <InfoBox
                    label="Applicant"
                    value={
                      details.applicant
                    }
                  />

                  <InfoBox
                    label="Inventor"
                    value={
                      details.inventor
                    }
                  />

                  <InfoBox
                    label="Jurisdiction"
                    value={
                      details.jurisdiction
                    }
                  />

                  <InfoBox
                    label="Publication Date"
                    value={
                      details.publication_date
                    }
                  />
                </div>

                <div className="mt-6 rounded-xl border border-slate-800 bg-slate-950/60 p-5">
                  <h3 className="font-semibold text-cyan-300">
                    Abstract
                  </h3>

                  <p className="mt-3 leading-7 text-slate-300">
                    {details.abstract ||
                      "No abstract available."}
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* SIMILAR */}
        {activeTab === "similar" && (
          <div className="space-y-4">
            {!selectedPatent ? (
              <EmptyState
                title="No patent selected"
                text="Choose Similar from a search result."
              />
            ) : (
              <>
                <h2 className="text-xl font-semibold">
                  Similar to
                </h2>

                <p className="text-slate-400">
                  {selectedPatent.title}
                </p>

                {similarPatents.map(
                  (patent) => (
                    <PatentCard
                      key={patent.lens_id}
                      patent={patent}
                    />
                  )
                )}
              </>
            )}
          </div>
        )}

        {/* BOOKMARKS */}
        {activeTab === "bookmarks" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">
                My Bookmarks
              </h2>

              <button
                onClick={loadBookmarks}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm hover:border-cyan-400"
              >
                Refresh
              </button>
            </div>

            {bookmarks.length === 0 ? (
              <EmptyState
                title="No bookmarks"
                text="Bookmark patents from your search results."
              />
            ) : (
              bookmarks.map(
                (bookmark) => (
                  <div
                    key={bookmark.id}
                    className="flex flex-col gap-4 rounded-xl border border-slate-800 bg-slate-900/60 p-5 md:flex-row md:items-center md:justify-between"
                  >
                    <div>
                      <div className="text-xs text-cyan-400">
                        {bookmark.lens_id}
                      </div>

                      <h3 className="mt-1 font-semibold">
                        {bookmark.title}
                      </h3>

                      <p className="mt-1 text-sm text-slate-500">
                        {bookmark.applicant}
                      </p>
                    </div>

                    <button
                      onClick={() =>
                        removeBookmark(
                          bookmark.id
                        )
                      }
                      className="rounded-lg border border-red-500/30 px-4 py-2 text-sm text-red-300 hover:bg-red-500/10"
                    >
                      Remove
                    </button>
                  </div>
                )
              )
            )}
          </div>
        )}

        {/* ANALYTICS */}
        {activeTab === "analytics" && (
          <div>
            {!analytics ? (
              <EmptyState
                title="No analytics yet"
                text="Search for a topic and open Analytics."
              />
            ) : (
              <div className="space-y-6">
                <div className="grid gap-4 md:grid-cols-4">
                  <StatCard
                    title="Total Patents"
                    value={
                      analytics.total_patents
                    }
                  />

                  <StatCard
                    title="Jurisdictions"
                    value={
                      Object.keys(
                        analytics.jurisdiction_distribution ||
                          {}
                      ).length
                    }
                  />

                  <StatCard
                    title="Legal Statuses"
                    value={
                      Object.keys(
                        analytics.legal_status_distribution ||
                          {}
                      ).length
                    }
                  />

                  <StatCard
                    title="Years"
                    value={
                      Object.keys(
                        analytics.publication_year_distribution ||
                          {}
                      ).length
                    }
                  />
                </div>

                <AnalyticsBox
                  title="Jurisdiction Distribution"
                  data={
                    analytics.jurisdiction_distribution ||
                    {}
                  }
                />

                <AnalyticsBox
                  title="Legal Status Distribution"
                  data={
                    analytics.legal_status_distribution ||
                    {}
                  }
                />

                <AnalyticsBox
                  title="Publication Years"
                  data={
                    analytics.publication_year_distribution ||
                    {}
                  }
                />

                <AnalyticsBox
                  title="Top Applicants"
                  data={
                    analytics.top_applicants ||
                    {}
                  }
                />

                <AnalyticsBox
                  title="Top Inventors"
                  data={
                    analytics.top_inventors ||
                    {}
                  }
                />
              </div>
            )}
          </div>
        )}

        {/* COMPARE */}
        {activeTab === "compare" && (
          <div className="space-y-6">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
              <h2 className="text-xl font-semibold">
                Compare Patents
              </h2>

              <p className="mt-2 text-sm text-slate-500">
                Select two patents from the search results.
              </p>

              <div className="mt-5 grid gap-4 md:grid-cols-2">
                <select
                  value={compareId1}
                  onChange={(e) =>
                    setCompareId1(
                      e.target.value
                    )
                  }
                  className="rounded-xl border border-slate-700 bg-slate-950 p-3 text-white"
                >
                  <option value="">
                    Select Patent 1
                  </option>

                  {patents.map((patent) => (
                    <option
                      key={patent.lens_id}
                      value={patent.lens_id}
                    >
                      {patent.lens_id} —{" "}
                      {patent.title}
                    </option>
                  ))}
                </select>

                <select
                  value={compareId2}
                  onChange={(e) =>
                    setCompareId2(
                      e.target.value
                    )
                  }
                  className="rounded-xl border border-slate-700 bg-slate-950 p-3 text-white"
                >
                  <option value="">
                    Select Patent 2
                  </option>

                  {patents.map((patent) => (
                    <option
                      key={patent.lens_id}
                      value={patent.lens_id}
                    >
                      {patent.lens_id} —{" "}
                      {patent.title}
                    </option>
                  ))}
                </select>
              </div>

              <button
                onClick={comparePatents}
                disabled={loading}
                className="mt-5 rounded-xl bg-cyan-500 px-6 py-3 font-bold text-slate-950 hover:bg-cyan-400 disabled:opacity-50"
              >
                {loading
                  ? "Comparing..."
                  : "Compare Patents"}
              </button>
            </div>

            {comparison && (
              <div className="grid gap-5 md:grid-cols-2">
                <ComparisonCard
                  title="Patent 1"
                  patent={
                    comparison.patent_1
                  }
                />

                <ComparisonCard
                  title="Patent 2"
                  patent={
                    comparison.patent_2
                  }
                />
              </div>
            )}
          </div>
        )}

        {/* TIMELINE */}
        {activeTab === "timeline" && (
          <div>
            {!timeline ? (
              <EmptyState
                title="No timeline"
                text="Select Timeline from a patent."
              />
            ) : (
              <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
                <h2 className="text-xl font-semibold">
                  Patent Timeline
                </h2>

                <p className="mt-2 text-sm text-cyan-400">
                  {timeline.lens_id}
                </p>

                <div className="mt-8 space-y-6">
                  {timeline.timeline?.map(
                    (event, index) => (
                      <div
                        key={index}
                        className="flex gap-4"
                      >
                        <div className="flex flex-col items-center">
                          <div className="h-4 w-4 rounded-full bg-cyan-400 shadow-lg shadow-cyan-400/30" />

                          {index <
                            timeline.timeline.length -
                              1 && (
                            <div className="h-full w-px bg-cyan-500/20" />
                          )}
                        </div>

                        <div className="pb-5">
                          <h3 className="font-semibold">
                            {event.event}
                          </h3>

                          <div className="mt-1 text-sm text-cyan-400">
                            {event.date ||
                              "Date unavailable"}
                          </div>

                          <p className="mt-2 text-sm text-slate-400">
                            {event.description ||
                              ""}
                          </p>
                        </div>
                      </div>
                    )
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* AI */}
        {activeTab === "ai" && (
          <div>
            {!aiInsights ? (
              <EmptyState
                title="No AI analysis"
                text="Select AI Insights from a patent."
              />
            ) : (
              <div className="space-y-5">
                <div className="rounded-2xl border border-purple-500/20 bg-purple-500/5 p-6">
                  <div className="text-sm text-purple-300">
                    AI Patent Intelligence
                  </div>

                  <h2 className="mt-2 text-2xl font-bold">
                    {selectedPatent?.title}
                  </h2>

                  <p className="mt-5 leading-7 text-slate-300">
                    {aiInsights.summary}
                  </p>
                </div>

                <div className="grid gap-5 md:grid-cols-3">
                  <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
                    <div className="text-sm text-slate-500">
                      Technology Domain
                    </div>

                    <div className="mt-2 font-semibold text-cyan-300">
                      {aiInsights.technology_domain}
                    </div>
                  </div>

                  <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
                    <div className="text-sm text-slate-500">
                      Innovation Score
                    </div>

                    <div className="mt-2 text-3xl font-bold text-purple-300">
                      {aiInsights.innovation_score}
                      <span className="text-lg text-slate-500">
                        /100
                      </span>
                    </div>
                  </div>

                  <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
                    <div className="text-sm text-slate-500">
                      Patent
                    </div>

                    <div className="mt-2 font-semibold text-white">
                      {selectedPatent?.lens_id}
                    </div>
                  </div>
                </div>

                <InsightBox
                  title="Novelty Analysis"
                  text={
                    aiInsights.novelty_analysis
                  }
                />

                <InsightBox
                  title="Commercialization Potential"
                  text={
                    aiInsights.commercialization_potential
                  }
                />

                <ListBox
                  title="Market Opportunities"
                  items={
                    aiInsights.market_opportunities
                  }
                />

                <ListBox
                  title="Recommended Industries"
                  items={
                    aiInsights.recommended_industries
                  }
                />

                <ListBox
                  title="Key Innovations"
                  items={
                    aiInsights.key_innovations
                  }
                />
              </div>
            )}
          </div>
        )}
      </section>
    </main>
  );
}


// ============================================================
// SMALL COMPONENTS
// ============================================================

function EmptyState({
  title,
  text,
}: {
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/40 p-12 text-center">
      <h2 className="text-xl font-semibold">
        {title}
      </h2>

      <p className="mt-2 text-slate-500">
        {text}
      </p>
    </div>
  );
}


function InfoBox({
  label,
  value,
}: {
  label: string;
  value?: string;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
      <div className="text-xs uppercase tracking-wider text-slate-500">
        {label}
      </div>

      <div className="mt-2 text-sm text-white">
        {value || "Not available"}
      </div>
    </div>
  );
}


function StatCard({
  title,
  value,
}: {
  title: string;
  value: string | number;
}) {
  return (
    <div className="rounded-2xl border border-cyan-500/20 bg-slate-900/60 p-5">
      <div className="text-sm text-slate-500">
        {title}
      </div>

      <div className="mt-2 text-3xl font-bold text-cyan-300">
        {value}
      </div>
    </div>
  );
}


function AnalyticsBox({
  title,
  data,
}: {
  title: string;
  data: Record<string, number>;
}) {
  const entries = Object.entries(data);

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
      <h3 className="text-lg font-semibold">
        {title}
      </h3>

      {entries.length === 0 ? (
        <p className="mt-4 text-sm text-slate-500">
          No data available.
        </p>
      ) : (
        <div className="mt-5 space-y-3">
          {entries.map(
            ([key, value]) => (
              <div
                key={key}
                className="flex items-center justify-between rounded-lg bg-slate-950/70 px-4 py-3"
              >
                <span className="text-sm text-slate-300">
                  {key}
                </span>

                <span className="font-semibold text-cyan-300">
                  {value}
                </span>
              </div>
            )
          )}
        </div>
      )}
    </div>
  );
}


function ComparisonCard({
  title,
  patent,
}: {
  title: string;
  patent: any;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
      <div className="text-sm font-semibold text-cyan-400">
        {title}
      </div>

      <h3 className="mt-2 text-xl font-bold">
        {patent?.title}
      </h3>

      <div className="mt-6 space-y-4">
        <InfoBox
          label="Lens ID"
          value={patent?.lens_id}
        />

        <InfoBox
          label="Applicant"
          value={patent?.applicant}
        />

        <InfoBox
          label="Inventor"
          value={patent?.inventor}
        />

        <InfoBox
          label="Jurisdiction"
          value={patent?.jurisdiction}
        />

        <InfoBox
          label="Publication Date"
          value={
            patent?.publication_date
          }
        />

        <InfoBox
          label="Legal Status"
          value={
            patent?.legal_status
          }
        />

        <div className="rounded-xl border border-slate-800 bg-slate-950/50 p-4">
          <div className="text-xs uppercase tracking-wider text-slate-500">
            Abstract
          </div>

          <p className="mt-2 text-sm leading-6 text-slate-300">
            {patent?.abstract ||
              "No abstract available."}
          </p>
        </div>
      </div>
    </div>
  );
}


function InsightBox({
  title,
  text,
}: {
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
      <h3 className="text-lg font-semibold text-purple-300">
        {title}
      </h3>

      <p className="mt-3 leading-7 text-slate-300">
        {text || "No information available."}
      </p>
    </div>
  );
}


function ListBox({
  title,
  items,
}: {
  title: string;
  items: string[];
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
      <h3 className="text-lg font-semibold text-cyan-300">
        {title}
      </h3>

      {items?.length ? (
        <ul className="mt-4 space-y-3">
          {items.map(
            (item, index) => (
              <li
                key={index}
                className="rounded-lg bg-slate-950/70 p-3 text-sm text-slate-300"
              >
                <span className="mr-2 text-cyan-400">
                  •
                </span>
                {item}
              </li>
            )
          )}
        </ul>
      ) : (
        <p className="mt-4 text-sm text-slate-500">
          No information available.
        </p>
      )}
    </div>
  );
}