"use client";

import { useState } from "react";
import { apiRequest } from "@/lib/api";

type Funding = {
  opportunity_id: string;
  opportunity_number: string;
  title: string;
  agency: string;
  open_date?: string;
  close_date: string;
  funding_amount: string;
  status?: string;
};

type Bookmark = {
  id: number;
  opportunity_id: string;
  opportunity_number?: string;
  title: string;
  agency?: string;
  close_date?: string;
  created_at?: string;
};

type Analytics = {
  keyword: string;
  total_opportunities: number;
  agencies: Record<string, number>;
  open_opportunities: number;
  closed_opportunities: number;
  upcoming_deadlines?: number;
};

type Deadline = {
  opportunity_id: string;
  opportunity_number: string;
  title: string;
  agency: string;
  close_date: string;
  days_remaining: number;
  urgency: string;
};

type Recommendation = {
  opportunity_id: string;
  opportunity_number: string;
  title: string;
  agency: string;
  close_date: string;
  match_score: number;
  matching_keywords: string[];
};

type AIInsight = {
  opportunity_id: string;
  ai_insights?: string;
  error?: string;
};

type Proposal = {
  opportunity_id: string;
  project_title: string;
  organization_name: string;
  proposal?: string;
  error?: string;
};

export default function FundingIntelligencePage() {
  const [activeTab, setActiveTab] = useState("search");

  const [keyword, setKeyword] = useState("");
  const [size, setSize] = useState(10);

  const [fundingResults, setFundingResults] = useState<Funding[]>(
    []
  );

  const [selectedFunding, setSelectedFunding] =
    useState<Funding | null>(null);

  const [details, setDetails] = useState<any>(null);

  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);

  const [analytics, setAnalytics] =
    useState<Analytics | null>(null);

  const [deadlines, setDeadlines] =
    useState<Deadline[]>([]);

  const [recommendations, setRecommendations] =
    useState<Recommendation[]>([]);

  const [aiInsight, setAIInsight] =
    useState<AIInsight | null>(null);

  const [proposal, setProposal] =
    useState<Proposal | null>(null);

  const [projectTitle, setProjectTitle] = useState("");

  const [projectDescription, setProjectDescription] =
    useState("");

  const [organizationName, setOrganizationName] =
    useState("");

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [message, setMessage] = useState("");

  // ============================================================
  // HELPERS
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
  // SEARCH FUNDING
  // ============================================================

  async function searchFunding() {
    if (!keyword.trim()) {
      setError("Please enter a funding keyword.");
      return;
    }

    setLoading(true);
    clearMessages();

    try {
      const data = await apiRequest(
        "/funding/search",
        {
          method: "POST",
          body: JSON.stringify({
            keyword: keyword.trim(),
          }),
        }
      );

      setFundingResults(
        data.results || []
      );

      setActiveTab("search");

      if (!data.results?.length) {
        setMessage(
          "No funding opportunities found."
        );
      }
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // DETAILS
  // ============================================================

  async function loadDetails(
    funding: Funding
  ) {
    setLoading(true);
    clearMessages();

    try {
      const data = await apiRequest(
        "/funding/details",
        {
          method: "POST",
          body: JSON.stringify({
            opportunity_id:
              funding.opportunity_id,
          }),
        }
      );

      setSelectedFunding(funding);
      setDetails(data);
      setActiveTab("details");
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // BOOKMARK
  // ============================================================

  async function bookmarkFunding(
    funding: Funding
  ) {
    clearMessages();

    try {
      const data = await apiRequest(
        "/funding/bookmark",
        {
          method: "POST",
          body: JSON.stringify({
            opportunity_id:
              funding.opportunity_id,
            opportunity_number:
              funding.opportunity_number,
            title: funding.title,
            agency: funding.agency,
            close_date: funding.close_date,
          }),
        }
      );

      setMessage(
        data?.message ||
          "Funding opportunity bookmarked successfully."
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
        "/funding/bookmarks"
      );

      setBookmarks(
        data.bookmarks || []
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

  async function deleteBookmark(
    id: number
  ) {
    clearMessages();

    try {
      const data = await apiRequest(
        `/funding/bookmark/${id}`,
        {
          method: "DELETE",
        }
      );

      setMessage(
        data?.message ||
          "Bookmark deleted successfully."
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
    if (!keyword.trim()) {
      setError(
        "Enter a funding keyword first."
      );
      return;
    }

    setLoading(true);
    clearMessages();

    try {
      const data = await apiRequest(
        "/funding/analytics",
        {
          method: "POST",
          body: JSON.stringify({
            keyword: keyword.trim(),
            size,
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
  // DEADLINES
  // ============================================================

  async function loadDeadlines() {
    if (!keyword.trim()) {
      setError(
        "Enter a funding keyword first."
      );
      return;
    }

    setLoading(true);
    clearMessages();

    try {
      const data = await apiRequest(
        "/funding/deadlines",
        {
          method: "POST",
          body: JSON.stringify({
            keyword: keyword.trim(),
            size,
          }),
        }
      );

      setDeadlines(
        data.deadlines || []
      );

      setActiveTab("deadlines");
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // RECOMMENDATIONS
  // ============================================================

  async function loadRecommendations() {
    if (!projectTitle.trim()) {
      setError(
        "Enter your project title."
      );
      return;
    }

    if (!projectDescription.trim()) {
      setError(
        "Enter your project description."
      );
      return;
    }

    if (!keyword.trim()) {
      setError(
        "Enter a funding keyword."
      );
      return;
    }

    setLoading(true);
    clearMessages();

    try {
      const data = await apiRequest(
        "/funding/recommendations",
        {
          method: "POST",
          body: JSON.stringify({
            project_title:
              projectTitle,
            project_description:
              projectDescription,
            keyword: keyword.trim(),
            size,
          }),
        }
      );

      setRecommendations(
        data.recommendations || []
      );

      setActiveTab(
        "recommendations"
      );
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
    funding: Funding
  ) {
    setLoading(true);
    clearMessages();

    try {
      const data = await apiRequest(
        "/funding/ai-insights",
        {
          method: "POST",
          body: JSON.stringify({
            opportunity_id:
              funding.opportunity_id,
          }),
        }
      );

      setSelectedFunding(funding);
      setAIInsight(data);
      setActiveTab("ai");
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // PROPOSAL
  // ============================================================

  async function generateProposal() {
    if (!selectedFunding) {
      setError(
        "Select a funding opportunity first."
      );
      return;
    }

    if (!projectTitle.trim()) {
      setError(
        "Enter your project title."
      );
      return;
    }

    if (!projectDescription.trim()) {
      setError(
        "Enter your project description."
      );
      return;
    }

    if (!organizationName.trim()) {
      setError(
        "Enter your organization name."
      );
      return;
    }

    setLoading(true);
    clearMessages();

    try {
      const data = await apiRequest(
        "/funding/generate-proposal",
        {
          method: "POST",
          body: JSON.stringify({
            opportunity_id:
              selectedFunding.opportunity_id,
            project_title:
              projectTitle,
            project_description:
              projectDescription,
            organization_name:
              organizationName,
          }),
        }
      );

      setProposal(data);
      setActiveTab("proposal");
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }

  // ============================================================
  // FUNDING CARD
  // ============================================================

  function FundingCard({
    funding,
  }: {
    funding: Funding;
  }) {
    return (
      <div className="rounded-2xl border border-cyan-500/20 bg-slate-900/70 p-5 transition hover:border-cyan-400/50 hover:shadow-lg hover:shadow-cyan-500/5">
        <div className="flex flex-col gap-5">

          <div className="flex items-start justify-between gap-4">

            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
                {funding.opportunity_number ||
                  funding.opportunity_id}
              </div>

              <h3 className="mt-2 text-lg font-semibold text-white">
                {funding.title ||
                  "Untitled Funding Opportunity"}
              </h3>
            </div>

            {funding.status && (
              <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs text-emerald-300">
                {funding.status}
              </span>
            )}

          </div>

          <div className="grid gap-4 md:grid-cols-4">

            <InfoBox
              label="Agency"
              value={
                funding.agency ||
                "Not available"
              }
            />

            <InfoBox
              label="Funding Amount"
              value={
                funding.funding_amount ||
                "Not specified"
              }
            />

            <InfoBox
              label="Open Date"
              value={
                funding.open_date ||
                "Not available"
              }
            />

            <InfoBox
              label="Close Date"
              value={
                funding.close_date ||
                "Not available"
              }
            />

          </div>

          <div className="flex flex-wrap gap-2 border-t border-slate-800 pt-4">

            <button
              onClick={() =>
                loadDetails(funding)
              }
              className="rounded-lg bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-cyan-400"
            >
              View Details
            </button>

            <button
              onClick={() =>
                bookmarkFunding(funding)
              }
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-white hover:border-cyan-400"
            >
              ★ Bookmark
            </button>

            <button
              onClick={() =>
                loadAIInsights(funding)
              }
              className="rounded-lg border border-purple-500/40 px-4 py-2 text-sm text-purple-300 hover:bg-purple-500/10"
            >
              ✨ AI Insights
            </button>

            <button
              onClick={() => {
                setSelectedFunding(funding);
                setActiveTab("proposal");
              }}
              className="rounded-lg border border-blue-500/30 px-4 py-2 text-sm text-blue-300 hover:bg-blue-500/10"
            >
              📝 Proposal
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

      {/* HEADER */}

      <section className="border-b border-cyan-500/10 bg-slate-950/80">

        <div className="mx-auto max-w-7xl px-6 py-8">

          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">

            <div>

              <div className="mb-2 text-sm font-semibold uppercase tracking-[0.3em] text-cyan-400">
                InnoBridge-AI
              </div>

              <h1 className="text-3xl font-bold md:text-4xl">
                Funding Intelligence
              </h1>

              <p className="mt-2 max-w-2xl text-slate-400">
                Discover funding opportunities,
                analyze deadlines, find suitable
                programs and generate AI-assisted
                funding proposals.
              </p>

            </div>

            <div className="rounded-xl border border-cyan-500/20 bg-cyan-500/5 px-5 py-4">

              <div className="text-xs text-slate-500">
                Funding Source
              </div>

              <div className="mt-1 font-semibold text-cyan-300">
                Grants.gov
              </div>

            </div>

          </div>

        </div>

      </section>

      {/* SEARCH */}

      <section className="mx-auto max-w-7xl px-6 pt-8">

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">

          <div className="flex flex-col gap-3 md:flex-row">

            <input
              value={keyword}
              onChange={(e) =>
                setKeyword(e.target.value)
              }
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  searchFunding();
                }
              }}
              placeholder="Search funding... e.g. artificial intelligence"
              className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none placeholder:text-slate-600 focus:border-cyan-400"
            />

            <select
              value={size}
              onChange={(e) =>
                setSize(
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
              onClick={searchFunding}
              disabled={loading}
              className="rounded-xl bg-cyan-500 px-6 py-3 font-bold text-slate-950 hover:bg-cyan-400 disabled:opacity-50"
            >
              {loading
                ? "Searching..."
                : "🔎 Search"}
            </button>

          </div>

        </div>

      </section>

      {/* MESSAGES */}

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

      {/* NAVIGATION */}

      <section className="mx-auto max-w-7xl px-6 pt-6">

        <div className="flex gap-2 overflow-x-auto border-b border-slate-800 pb-2">

          {[
            ["search", "🔎 Search"],
            ["details", "📄 Details"],
            ["bookmarks", "★ Bookmarks"],
            ["analytics", "📊 Analytics"],
            ["deadlines", "📅 Deadlines"],
            [
              "recommendations",
              "🎯 Recommendations",
            ],
            ["ai", "✨ AI Insights"],
            ["proposal", "📝 Proposal"],
          ].map(([id, label]) => (

            <button
              key={id}
              onClick={() =>
                setActiveTab(id)
              }
              className={`whitespace-nowrap rounded-lg px-4 py-2 text-sm font-medium ${
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

      {/* CONTENT */}

      <section className="mx-auto max-w-7xl px-6 py-8">

        {/* SEARCH */}

        {activeTab === "search" && (

          <div className="space-y-4">

            {fundingResults.length === 0 ? (

              <EmptyState
                title="Search Funding Opportunities"
                text="Enter a keyword above to discover available funding programs."
              />

            ) : (

              <>
                <div className="flex items-center justify-between">

                  <h2 className="text-xl font-semibold">
                    Funding Opportunities
                  </h2>

                  <span className="text-sm text-slate-500">
                    {fundingResults.length} results
                  </span>

                </div>

                {fundingResults.map(
                  (funding) => (
                    <FundingCard
                      key={
                        funding.opportunity_id
                      }
                      funding={funding}
                    />
                  )
                )}

              </>

            )}

          </div>

        )}

        {/* DETAILS */}

        {activeTab === "details" && (

          !details ? (

            <EmptyState
              title="No Funding Opportunity Selected"
              text="Select View Details from a funding search result."
            />

          ) : (

            <div className="rounded-2xl border border-cyan-500/20 bg-slate-900/60 p-6">

              <div className="mb-6">

                <div className="text-xs text-cyan-400">
                  {selectedFunding?.opportunity_number ||
                    selectedFunding?.opportunity_id}
                </div>

                <h2 className="mt-2 text-2xl font-bold">
                  {selectedFunding?.title}
                </h2>

              </div>

              <pre className="max-h-[600px] overflow-auto rounded-xl border border-slate-800 bg-slate-950 p-5 text-sm leading-6 text-slate-300">
                {JSON.stringify(
                  details,
                  null,
                  2
                )}
              </pre>

            </div>

          )

        )}

        {/* BOOKMARKS */}

        {activeTab === "bookmarks" && (

          <div className="space-y-5">

            <div className="flex items-center justify-between">

              <h2 className="text-xl font-semibold">
                My Funding Bookmarks
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
                title="No Bookmarks"
                text="Bookmark funding opportunities from your search results."
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
                        {bookmark.opportunity_number ||
                          bookmark.opportunity_id}
                      </div>

                      <h3 className="mt-1 font-semibold">
                        {bookmark.title}
                      </h3>

                      <p className="mt-1 text-sm text-slate-500">
                        {bookmark.agency}
                      </p>

                      <p className="mt-1 text-xs text-slate-600">
                        Deadline:{" "}
                        {bookmark.close_date ||
                          "Not available"}
                      </p>

                    </div>

                    <button
                      onClick={() =>
                        deleteBookmark(
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

          !analytics ? (

            <EmptyState
              title="No Analytics"
              text="Search for a funding keyword and open Analytics."
            />

          ) : (

            <div className="space-y-6">

              <div className="grid gap-4 md:grid-cols-4">

                <StatCard
                  title="Total Opportunities"
                  value={
                    analytics.total_opportunities
                  }
                />

                <StatCard
                  title="Open"
                  value={
                    analytics.open_opportunities
                  }
                />

                <StatCard
                  title="Closed"
                  value={
                    analytics.closed_opportunities
                  }
                />

                <StatCard
                  title="Upcoming Deadlines"
                  value={
                    analytics.upcoming_deadlines ||
                    0
                  }
                />

              </div>

              <AnalyticsBox
                title="Funding Agencies"
                data={
                  analytics.agencies || {}
                }
              />

            </div>

          )

        )}

        {/* DEADLINES */}

        {activeTab === "deadlines" && (

          <div className="space-y-5">

            <div className="flex items-center justify-between">

              <div>

                <h2 className="text-xl font-semibold">
                  Funding Deadlines
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Upcoming opportunities requiring attention.
                </p>

              </div>

              <button
                onClick={loadDeadlines}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm hover:border-cyan-400"
              >
                Refresh
              </button>

            </div>

            {deadlines.length === 0 ? (

              <EmptyState
                title="No Upcoming Deadlines"
                text="Search for a funding keyword and load deadlines."
              />

            ) : (

              deadlines.map(
                (deadline) => (

                  <div
                    key={
                      deadline.opportunity_id
                    }
                    className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5"
                  >

                    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

                      <div>

                        <div className="text-xs text-cyan-400">
                          {deadline.opportunity_number}
                        </div>

                        <h3 className="mt-1 font-semibold">
                          {deadline.title}
                        </h3>

                        <p className="mt-1 text-sm text-slate-500">
                          {deadline.agency}
                        </p>

                      </div>

                      <div className="text-left md:text-right">

                        <span
                          className={`rounded-full px-3 py-1 text-xs font-semibold ${
                            deadline.urgency ===
                            "URGENT"
                              ? "bg-red-500/10 text-red-300"
                              : deadline.urgency ===
                                "UPCOMING"
                              ? "bg-yellow-500/10 text-yellow-300"
                              : "bg-cyan-500/10 text-cyan-300"
                          }`}
                        >
                          {deadline.urgency}
                        </span>

                        <p className="mt-2 text-sm text-slate-300">
                          {deadline.close_date}
                        </p>

                        <p className="mt-1 text-xs text-slate-500">
                          {deadline.days_remaining} days remaining
                        </p>

                      </div>

                    </div>

                  </div>

                )

              )

            )}

          </div>

        )}

        {/* RECOMMENDATIONS */}

        {activeTab === "recommendations" && (

          <div className="space-y-6">

            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">

              <h2 className="text-xl font-semibold">
                Find Suitable Funding
              </h2>

              <div className="mt-5 space-y-4">

                <input
                  value={projectTitle}
                  onChange={(e) =>
                    setProjectTitle(
                      e.target.value
                    )
                  }
                  placeholder="Project title"
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

                <textarea
                  value={projectDescription}
                  onChange={(e) =>
                    setProjectDescription(
                      e.target.value
                    )
                  }
                  placeholder="Describe your project..."
                  rows={5}
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

                <button
                  onClick={
                    loadRecommendations
                  }
                  disabled={loading}
                  className="rounded-xl bg-cyan-500 px-6 py-3 font-bold text-slate-950 hover:bg-cyan-400 disabled:opacity-50"
                >
                  {loading
                    ? "Finding..."
                    : "🎯 Find Funding"}
                </button>

              </div>

            </div>

            {recommendations.length > 0 && (

              <div className="space-y-4">

                {recommendations.map(
                  (recommendation) => (

                    <div
                      key={
                        recommendation.opportunity_id
                      }
                      className="rounded-2xl border border-cyan-500/20 bg-slate-900/60 p-5"
                    >

                      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

                        <div>

                          <div className="text-xs text-cyan-400">
                            {
                              recommendation.opportunity_number
                            }
                          </div>

                          <h3 className="mt-1 font-semibold">
                            {
                              recommendation.title
                            }
                          </h3>

                          <p className="mt-1 text-sm text-slate-500">
                            {
                              recommendation.agency
                            }
                          </p>

                        </div>

                        <div className="rounded-xl border border-cyan-500/20 bg-cyan-500/10 px-5 py-3 text-center">

                          <div className="text-xs text-slate-500">
                            Match Score
                          </div>

                          <div className="text-2xl font-bold text-cyan-300">
                            {
                              recommendation.match_score
                            }%
                          </div>

                        </div>

                      </div>

                      {recommendation
                        .matching_keywords
                        ?.length >
                        0 && (

                        <div className="mt-4 flex flex-wrap gap-2">

                          {recommendation.matching_keywords.map(
                            (word) => (

                              <span
                                key={word}
                                className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300"
                              >
                                {word}
                              </span>

                            )
                          )}

                        </div>

                      )}

                    </div>

                  )

                )}

              </div>

            )}

          </div>

        )}

        {/* AI INSIGHTS */}

        {activeTab === "ai" && (

          !aiInsight ? (

            <EmptyState
              title="No AI Insights"
              text="Select AI Insights from a funding opportunity."
            />

          ) : (

            <div className="rounded-2xl border border-purple-500/20 bg-purple-500/5 p-6">

              <div className="text-sm text-purple-300">
                AI Funding Intelligence
              </div>

              <h2 className="mt-2 text-2xl font-bold">
                {selectedFunding?.title}
              </h2>

              {aiInsight.error ? (

                <div className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-300">
                  {aiInsight.error}
                </div>

              ) : (

                <div className="mt-6 whitespace-pre-wrap rounded-xl border border-slate-800 bg-slate-950/70 p-6 leading-7 text-slate-300">
                  {aiInsight.ai_insights}
                </div>

              )}

            </div>

          )

        )}

        {/* PROPOSAL */}

        {activeTab === "proposal" && (

          <div className="space-y-6">

            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">

              <h2 className="text-xl font-semibold">
                AI Funding Proposal Generator
              </h2>

              {selectedFunding && (

                <div className="mt-4 rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-4">

                  <div className="text-xs text-cyan-400">
                    Selected Opportunity
                  </div>

                  <div className="mt-1 font-semibold">
                    {selectedFunding.title}
                  </div>

                </div>

              )}

              <div className="mt-5 space-y-4">

                <input
                  value={projectTitle}
                  onChange={(e) =>
                    setProjectTitle(
                      e.target.value
                    )
                  }
                  placeholder="Project title"
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

                <textarea
                  value={projectDescription}
                  onChange={(e) =>
                    setProjectDescription(
                      e.target.value
                    )
                  }
                  placeholder="Project description"
                  rows={6}
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

                <input
                  value={organizationName}
                  onChange={(e) =>
                    setOrganizationName(
                      e.target.value
                    )
                  }
                  placeholder="Organization name"
                  className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none focus:border-cyan-400"
                />

                <button
                  onClick={
                    generateProposal
                  }
                  disabled={loading}
                  className="rounded-xl bg-purple-500 px-6 py-3 font-bold text-white hover:bg-purple-400 disabled:opacity-50"
                >
                  {loading
                    ? "Generating..."
                    : "✨ Generate Proposal"}
                </button>

              </div>

            </div>

            {proposal && (

              <div className="rounded-2xl border border-purple-500/20 bg-slate-900/60 p-6">

                <h2 className="text-xl font-semibold text-purple-300">
                  Generated Proposal
                </h2>

                {proposal.error ? (

                  <div className="mt-5 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-300">
                    {proposal.error}
                  </div>

                ) : (

                  <div className="mt-5 whitespace-pre-wrap rounded-xl border border-slate-800 bg-slate-950/70 p-6 leading-7 text-slate-300">
                    {proposal.proposal}
                  </div>

                )}

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

      <div className="text-4xl">
        💰
      </div>

      <h2 className="mt-4 text-xl font-semibold">
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