"use client";

import { useState } from "react";
import { apiRequest } from "@/lib/api";

type Mode =
  | "papers"
  | "authors"
  | "institutions"
  | "recommendations"
  | "ai";

type AITool =
  | "summary"
  | "innovation"
  | "gap"
  | "literature"
  | "trends"
  | "citation"
  | "chat"
  | "compare"
  | "proposal"
  | "novelty"
  | "questions"
  | "methodology";

interface Paper {
  id: string;
  title: string;
  publication_year?: number | null;
  doi?: string | null;
  cited_by_count: number;
  authors: {
    name: string;
  }[];
}

interface Author {
  id: string;
  name: string;
  orcid?: string | null;
  works_count: number;
  cited_by_count: number;
  h_index?: number | null;
  last_known_institution?: string | null;
}

interface Institution {
  id: string;
  name: string;
  country?: string | null;
  works_count: number;
  cited_by_count: number;
}

interface Recommendation {
  title: string;
  authors: string[];
  publication_year?: number | null;
  cited_by_count: number;
  doi?: string | null;
  url?: string | null;
}

export default function ResearchIntelligencePage() {
  const [mode, setMode] =
    useState<Mode>("papers");

  const [aiTool, setAITool] =
    useState<AITool>("summary");

  const [query, setQuery] =
    useState("");

  const [papers, setPapers] =
    useState<Paper[]>([]);

  const [authors, setAuthors] =
    useState<Author[]>([]);

  const [institutions, setInstitutions] =
    useState<Institution[]>([]);

  const [recommendations, setRecommendations] =
    useState<Recommendation[]>([]);

  const [count, setCount] =
    useState(0);

  const [title, setTitle] =
    useState("");

  const [abstract, setAbstract] =
    useState("");

  const [question, setQuestion] =
    useState("");

  const [title2, setTitle2] =
    useState("");

  const [abstract2, setAbstract2] =
    useState("");

  const [citationAuthors, setCitationAuthors] =
    useState("");

  const [journal, setJournal] =
    useState("");

  const [publicationYear, setPublicationYear] =
    useState("");

  const [doi, setDoi] =
    useState("");

  const [result, setResult] =
    useState<any>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [message, setMessage] =
    useState("");

  function clearMessages() {
    setError("");
    setMessage("");
  }

  async function searchPapers() {
    if (!query.trim()) {
      setError("Please enter a research topic.");
      return;
    }

    try {
      setLoading(true);
      clearMessages();

      const data = await apiRequest(
        `/research-intelligence/search-papers?query=${encodeURIComponent(
          query
        )}&page=1&per_page=10`
      );

      setPapers(data.results || []);
      setCount(data.count || 0);
      setMessage("Research papers loaded.");
    } catch (err: any) {
      setError(
        err?.message ||
          "Failed to search research papers."
      );
    } finally {
      setLoading(false);
    }
  }

  async function searchAuthors() {
    if (!query.trim()) {
      setError("Please enter an author name.");
      return;
    }

    try {
      setLoading(true);
      clearMessages();

      const data = await apiRequest(
        `/research-intelligence/search-authors?query=${encodeURIComponent(
          query
        )}&page=1&per_page=10`
      );

      setAuthors(data.results || []);
      setCount(data.count || 0);
      setMessage("Authors loaded.");
    } catch (err: any) {
      setError(
        err?.message ||
          "Failed to search authors."
      );
    } finally {
      setLoading(false);
    }
  }

  async function searchInstitutions() {
    if (!query.trim()) {
      setError("Please enter an institution name.");
      return;
    }

    try {
      setLoading(true);
      clearMessages();

      const data = await apiRequest(
        `/research-intelligence/search-institutions?query=${encodeURIComponent(
          query
        )}&page=1&per_page=10`
      );

      setInstitutions(data.results || []);
      setCount(data.count || 0);
      setMessage("Institutions loaded.");
    } catch (err: any) {
      setError(
        err?.message ||
          "Failed to search institutions."
      );
    } finally {
      setLoading(false);
    }
  }

  async function getRecommendations() {
    if (!query.trim()) {
      setError("Please enter a research topic.");
      return;
    }

    try {
      setLoading(true);
      clearMessages();

      const data = await apiRequest(
        `/research-intelligence/recommendations?query=${encodeURIComponent(
          query
        )}&limit=10`
      );

      setRecommendations(
        data.recommendations || []
      );

      setMessage(
        "Research recommendations loaded."
      );
    } catch (err: any) {
      setError(
        err?.message ||
          "Failed to load recommendations."
      );
    } finally {
      setLoading(false);
    }
  }

  async function runAI() {
    if (!title.trim()) {
      setError("Please enter a research title.");
      return;
    }

    if (
      aiTool !== "citation" &&
      !abstract.trim()
    ) {
      setError("Please enter the research abstract.");
      return;
    }

    if (
      aiTool === "chat" &&
      !question.trim()
    ) {
      setError("Please enter your question.");
      return;
    }

    if (
      aiTool === "compare" &&
      (!title2.trim() || !abstract2.trim())
    ) {
      setError(
        "Please enter both papers for comparison."
      );
      return;
    }

    try {
      setLoading(true);
      clearMessages();
      setResult(null);

      let endpoint = "";
      let body: any = {};

      switch (aiTool) {
        case "summary":
          endpoint =
            "/research-intelligence/summarize";

          body = {
            title,
            abstract,
          };
          break;

        case "innovation":
          endpoint =
            "/research-intelligence/generate-innovation";

          body = {
            title,
            abstract,
          };
          break;

        case "gap":
          endpoint =
            "/research-intelligence/research-gap-detector";

          body = {
            title,
            abstract,
          };
          break;

        case "literature":
          endpoint =
            "/research-intelligence/literature-review";

          body = {
            title,
            abstract,
          };
          break;

        case "trends":
          endpoint =
            "/research-intelligence/research-trends";

          body = {
            title,
            abstract,
          };
          break;

        case "citation":
          endpoint =
            "/research-intelligence/citation-intelligence";

          body = {
            title,
            authors: citationAuthors
              .split(",")
              .map((item) => item.trim())
              .filter(Boolean),
            journal:
              journal || null,
            publication_year:
              publicationYear
                ? Number(publicationYear)
                : null,
            doi: doi || null,
          };
          break;

        case "chat":
          endpoint =
            "/research-intelligence/research-chat";

          body = {
            title,
            abstract,
            question,
          };
          break;

        case "compare":
          endpoint =
            "/research-intelligence/paper-comparator";

          body = {
            title1: title,
            abstract1: abstract,
            title2,
            abstract2,
          };
          break;

        case "proposal":
          endpoint =
            "/research-intelligence/research-proposal";

          body = {
            title,
            abstract,
          };
          break;

        case "novelty":
          endpoint =
            "/research-intelligence/novelty-checker";

          body = {
            title,
            abstract,
          };
          break;

        case "questions":
          endpoint =
            "/research-intelligence/research-question-generator";

          body = {
            title,
            abstract,
          };
          break;

        case "methodology":
          endpoint =
            "/research-intelligence/methodology-recommender";

          body = {
            title,
            abstract,
          };
          break;
      }

      const data = await apiRequest(
        endpoint,
        {
          method: "POST",
          body: JSON.stringify(body),
        }
      );

      setResult(data);
      setMessage(
        "AI analysis completed successfully."
      );
    } catch (err: any) {
      setError(
        err?.message ||
          "AI analysis failed."
      );
    } finally {
      setLoading(false);
    }
  }

  function selectTool(tool: AITool) {
    setAITool(tool);
    setResult(null);
    clearMessages();
  }

  return (
    <main className="min-h-screen bg-[#06111f] px-6 py-10 text-white md:px-10">

      <div className="mx-auto max-w-7xl">

        {/* HEADER */}

        <div className="mb-8">

          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-cyan-400">
            InnoBridge-AI
          </p>

          <h1 className="mt-3 text-4xl font-bold md:text-5xl">
            Research Intelligence
          </h1>

          <p className="mt-3 max-w-3xl text-slate-400">
            Discover research, researchers and institutions,
            then use AI tools to analyze and develop research ideas.
          </p>

        </div>

        {/* ALERTS */}

        {message && (
          <div className="mb-5 rounded-xl border border-green-500/30 bg-green-500/10 p-4 text-green-400">
            {message}
          </div>
        )}

        {error && (
          <div className="mb-5 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-400">
            {error}
          </div>
        )}

        {/* MAIN TABS */}

        <div className="mb-8 flex flex-wrap gap-2 rounded-2xl border border-slate-800 bg-[#0b1a2b] p-2">

          <Tab
            active={mode === "papers"}
            onClick={() => setMode("papers")}
          >
            🔎 Papers
          </Tab>

          <Tab
            active={mode === "authors"}
            onClick={() => setMode("authors")}
          >
            👨‍🔬 Authors
          </Tab>

          <Tab
            active={mode === "institutions"}
            onClick={() =>
              setMode("institutions")
            }
          >
            🏛️ Institutions
          </Tab>

          <Tab
            active={mode === "recommendations"}
            onClick={() =>
              setMode("recommendations")
            }
          >
            ⭐ Recommendations
          </Tab>

          <Tab
            active={mode === "ai"}
            onClick={() => setMode("ai")}
          >
            🤖 AI Research Lab
          </Tab>

        </div>

        {/* =====================================================
            SEARCH
        ===================================================== */}

        {mode !== "ai" && (
          <section className="rounded-2xl border border-slate-700 bg-[#0b1a2b] p-6 md:p-8">

            <h2 className="text-2xl font-bold">
              {mode === "papers" &&
                "Search Research Papers"}

              {mode === "authors" &&
                "Search Researchers"}

              {mode === "institutions" &&
                "Search Institutions"}

              {mode === "recommendations" &&
                "Research Recommendations"}
            </h2>

            <p className="mt-2 text-slate-400">
              {mode === "papers" &&
                "Search research papers using OpenAlex."}

              {mode === "authors" &&
                "Find researchers and their publication impact."}

              {mode === "institutions" &&
                "Find universities and research institutions."}

              {mode === "recommendations" &&
                "Find research papers related to your topic."}
            </p>

            <div className="mt-6 flex flex-col gap-3 md:flex-row">

              <input
                value={query}
                onChange={(e) =>
                  setQuery(e.target.value)
                }
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    if (mode === "papers")
                      searchPapers();
                    else if (mode === "authors")
                      searchAuthors();
                    else if (mode === "institutions")
                      searchInstitutions();
                    else
                      getRecommendations();
                  }
                }}
                placeholder={
                  mode === "papers"
                    ? "Artificial Intelligence"
                    : mode === "authors"
                    ? "Author name"
                    : mode === "institutions"
                    ? "University or institution"
                    : "Research topic"
                }
                className="flex-1 rounded-xl border border-slate-700 bg-[#071525] px-5 py-3 text-white outline-none focus:border-cyan-400"
              />

              <button
                onClick={() => {
                  if (mode === "papers")
                    searchPapers();
                  else if (mode === "authors")
                    searchAuthors();
                  else if (mode === "institutions")
                    searchInstitutions();
                  else
                    getRecommendations();
                }}
                disabled={loading}
                className="rounded-xl bg-cyan-500 px-7 py-3 font-semibold text-black transition hover:bg-cyan-400 disabled:opacity-50"
              >
                {loading
                  ? "Searching..."
                  : "Search"}
              </button>

            </div>

            {/* PAPER RESULTS */}

            {mode === "papers" && (
              <div className="mt-8">

                {papers.length > 0 && (
                  <p className="mb-5 text-sm text-slate-500">
                    {count} results found
                  </p>
                )}

                <div className="space-y-4">

                  {papers.map((paper) => (
                    <div
                      key={paper.id}
                      className="rounded-xl border border-slate-700 bg-[#071525] p-5"
                    >

                      <h3 className="text-lg font-bold text-white">
                        {paper.title}
                      </h3>

                      <div className="mt-3 flex flex-wrap gap-3 text-sm text-slate-400">

                        <span>
                          📅{" "}
                          {paper.publication_year ||
                            "Year unavailable"}
                        </span>

                        <span>
                          📚{" "}
                          {paper.cited_by_count} citations
                        </span>

                        {paper.doi && (
                          <span className="break-all">
                            DOI: {paper.doi}
                          </span>
                        )}

                      </div>

                      <div className="mt-3">

                        <p className="text-xs uppercase tracking-wider text-slate-500">
                          Authors
                        </p>

                        <p className="mt-1 text-sm text-slate-300">
                          {paper.authors
                            .map(
                              (author) =>
                                author.name
                            )
                            .join(", ")}
                        </p>

                      </div>

                    </div>
                  ))}

                </div>

                {papers.length === 0 &&
                  !loading && (
                    <EmptyState text="Search for a research topic to see papers." />
                  )}

              </div>
            )}

            {/* AUTHOR RESULTS */}

            {mode === "authors" && (
              <div className="mt-8">

                {authors.length > 0 && (
                  <p className="mb-5 text-sm text-slate-500">
                    {count} authors found
                  </p>
                )}

                <div className="grid gap-4 md:grid-cols-2">

                  {authors.map((author) => (
                    <div
                      key={author.id}
                      className="rounded-xl border border-slate-700 bg-[#071525] p-5"
                    >

                      <h3 className="text-lg font-bold">
                        {author.name}
                      </h3>

                      <div className="mt-4 grid grid-cols-2 gap-3">

                        <Stat
                          label="Works"
                          value={
                            author.works_count
                          }
                        />

                        <Stat
                          label="Citations"
                          value={
                            author.cited_by_count
                          }
                        />

                        <Stat
                          label="H-Index"
                          value={
                            author.h_index ??
                            "N/A"
                          }
                        />

                      </div>

                      {author.last_known_institution && (
                        <p className="mt-4 text-sm text-slate-400">
                          🏛️{" "}
                          {author.last_known_institution}
                        </p>
                      )}

                      {author.orcid && (
                        <p className="mt-2 break-all text-xs text-slate-500">
                          ORCID: {author.orcid}
                        </p>
                      )}

                    </div>
                  ))}

                </div>

                {authors.length === 0 &&
                  !loading && (
                    <EmptyState text="Search for an author to see researchers." />
                  )}

              </div>
            )}

            {/* INSTITUTION RESULTS */}

            {mode === "institutions" && (
              <div className="mt-8">

                {institutions.length > 0 && (
                  <p className="mb-5 text-sm text-slate-500">
                    {count} institutions found
                  </p>
                )}

                <div className="grid gap-4 md:grid-cols-2">

                  {institutions.map(
                    (institution) => (
                      <div
                        key={institution.id}
                        className="rounded-xl border border-slate-700 bg-[#071525] p-5"
                      >

                        <h3 className="text-lg font-bold">
                          {institution.name}
                        </h3>

                        <p className="mt-2 text-sm text-slate-400">
                          🌍{" "}
                          {institution.country ||
                            "Country unavailable"}
                        </p>

                        <div className="mt-4 grid grid-cols-2 gap-3">

                          <Stat
                            label="Works"
                            value={
                              institution.works_count
                            }
                          />

                          <Stat
                            label="Citations"
                            value={
                              institution.cited_by_count
                            }
                          />

                        </div>

                      </div>
                    )
                  )}

                </div>

                {institutions.length === 0 &&
                  !loading && (
                    <EmptyState text="Search for an institution." />
                  )}

              </div>
            )}

            {/* RECOMMENDATIONS */}

            {mode === "recommendations" && (
              <div className="mt-8">

                <div className="space-y-4">

                  {recommendations.map(
                    (item, index) => (
                      <div
                        key={`${item.title}-${index}`}
                        className="rounded-xl border border-slate-700 bg-[#071525] p-5"
                      >

                        <div className="flex items-start gap-4">

                          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-cyan-400/10 text-cyan-400">
                            {index + 1}
                          </div>

                          <div className="flex-1">

                            <h3 className="font-bold">
                              {item.title}
                            </h3>

                            <p className="mt-2 text-sm text-slate-400">
                              {item.authors.join(
                                ", "
                              )}
                            </p>

                            <div className="mt-3 flex flex-wrap gap-4 text-xs text-slate-500">

                              <span>
                                Year:{" "}
                                {item.publication_year ??
                                  "N/A"}
                              </span>

                              <span>
                                Citations:{" "}
                                {
                                  item.cited_by_count
                                }
                              </span>

                            </div>

                            {item.url && (
                              <a
                                href={item.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="mt-4 inline-block text-sm text-cyan-400 hover:underline"
                              >
                                View Research →
                              </a>
                            )}

                          </div>

                        </div>

                      </div>
                    )
                  )}

                </div>

                {recommendations.length === 0 &&
                  !loading && (
                    <EmptyState text="Enter a research topic to get recommendations." />
                  )}

              </div>
            )}

          </section>
        )}

        {/* =====================================================
            AI RESEARCH LAB
        ===================================================== */}

        {mode === "ai" && (
          <section className="grid gap-6 lg:grid-cols-[280px_1fr]">

            {/* AI SIDEBAR */}

            <div className="rounded-2xl border border-slate-700 bg-[#0b1a2b] p-4">

              <p className="px-3 pb-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
                AI Research Tools
              </p>

              <div className="space-y-1">

                <AITab
                  active={aiTool === "summary"}
                  onClick={() =>
                    selectTool("summary")
                  }
                >
                  📝 Research Summary
                </AITab>

                <AITab
                  active={
                    aiTool === "innovation"
                  }
                  onClick={() =>
                    selectTool("innovation")
                  }
                >
                  💡 Innovation Generator
                </AITab>

                <AITab
                  active={aiTool === "gap"}
                  onClick={() =>
                    selectTool("gap")
                  }
                >
                  🔍 Research Gap
                </AITab>

                <AITab
                  active={
                    aiTool === "literature"
                  }
                  onClick={() =>
                    selectTool("literature")
                  }
                >
                  📚 Literature Review
                </AITab>

                <AITab
                  active={aiTool === "trends"}
                  onClick={() =>
                    selectTool("trends")
                  }
                >
                  📈 Research Trends
                </AITab>

                <AITab
                  active={
                    aiTool === "citation"
                  }
                  onClick={() =>
                    selectTool("citation")
                  }
                >
                  🔗 Citation Intelligence
                </AITab>

                <AITab
                  active={aiTool === "chat"}
                  onClick={() =>
                    selectTool("chat")
                  }
                >
                  💬 Research Chat
                </AITab>

                <AITab
                  active={
                    aiTool === "compare"
                  }
                  onClick={() =>
                    selectTool("compare")
                  }
                >
                  ⚖️ Paper Comparator
                </AITab>

                <AITab
                  active={
                    aiTool === "proposal"
                  }
                  onClick={() =>
                    selectTool("proposal")
                  }
                >
                  📋 Research Proposal
                </AITab>

                <AITab
                  active={
                    aiTool === "novelty"
                  }
                  onClick={() =>
                    selectTool("novelty")
                  }
                >
                  🧠 Novelty Checker
                </AITab>

                <AITab
                  active={
                    aiTool === "questions"
                  }
                  onClick={() =>
                    selectTool("questions")
                  }
                >
                  ❓ Research Questions
                </AITab>

                <AITab
                  active={
                    aiTool === "methodology"
                  }
                  onClick={() =>
                    selectTool("methodology")
                  }
                >
                  🧪 Methodology
                </AITab>

              </div>

            </div>

            {/* AI CONTENT */}

            <div className="rounded-2xl border border-slate-700 bg-[#0b1a2b] p-6 md:p-8">

              <h2 className="text-2xl font-bold">
                {getToolTitle(aiTool)}
              </h2>

              <p className="mt-2 text-slate-400">
                {getToolDescription(aiTool)}
              </p>

              <div className="mt-7 space-y-5">

                {/* TITLE */}

                <div>

                  <label className="mb-2 block text-sm font-semibold text-slate-400">
                    Research Title
                  </label>

                  <input
                    value={title}
                    onChange={(e) =>
                      setTitle(e.target.value)
                    }
                    placeholder="Enter research paper title"
                    className="w-full rounded-xl border border-slate-700 bg-[#071525] px-5 py-3 text-white outline-none focus:border-cyan-400"
                  />

                </div>

                {/* ABSTRACT */}

                {aiTool !== "citation" && (
                  <div>

                    <label className="mb-2 block text-sm font-semibold text-slate-400">
                      Abstract
                    </label>

                    <textarea
                      value={abstract}
                      onChange={(e) =>
                        setAbstract(
                          e.target.value
                        )
                      }
                      rows={7}
                      placeholder="Paste the research abstract here..."
                      className="w-full resize-none rounded-xl border border-slate-700 bg-[#071525] px-5 py-3 text-white outline-none focus:border-cyan-400"
                    />

                  </div>
                )}

                {/* CITATION FIELDS */}

                {aiTool === "citation" && (
                  <>
                    <div>

                      <label className="mb-2 block text-sm font-semibold text-slate-400">
                        Authors
                      </label>

                      <input
                        value={
                          citationAuthors
                        }
                        onChange={(e) =>
                          setCitationAuthors(
                            e.target.value
                          )
                        }
                        placeholder="John Smith, Jane Doe"
                        className="w-full rounded-xl border border-slate-700 bg-[#071525] px-5 py-3 text-white outline-none focus:border-cyan-400"
                      />

                      <p className="mt-1 text-xs text-slate-500">
                        Separate authors using commas.
                      </p>

                    </div>

                    <div className="grid gap-5 md:grid-cols-3">

                      <Input
                        label="Journal"
                        value={journal}
                        onChange={setJournal}
                        placeholder="Journal name"
                      />

                      <Input
                        label="Publication Year"
                        value={
                          publicationYear
                        }
                        onChange={
                          setPublicationYear
                        }
                        placeholder="2026"
                      />

                      <Input
                        label="DOI"
                        value={doi}
                        onChange={setDoi}
                        placeholder="10.xxxx/xxxxx"
                      />

                    </div>
                  </>
                )}

                {/* CHAT */}

                {aiTool === "chat" && (
                  <div>

                    <label className="mb-2 block text-sm font-semibold text-slate-400">
                      Your Question
                    </label>

                    <textarea
                      value={question}
                      onChange={(e) =>
                        setQuestion(
                          e.target.value
                        )
                      }
                      rows={4}
                      placeholder="Ask something about this research..."
                      className="w-full resize-none rounded-xl border border-slate-700 bg-[#071525] px-5 py-3 text-white outline-none focus:border-cyan-400"
                    />

                  </div>
                )}

                {/* COMPARATOR */}

                {aiTool === "compare" && (
                  <div className="space-y-5 border-t border-slate-700 pt-6">

                    <h3 className="font-bold text-cyan-400">
                      Paper 2
                    </h3>

                    <Input
                      label="Paper 2 Title"
                      value={title2}
                      onChange={setTitle2}
                      placeholder="Second paper title"
                    />

                    <div>

                      <label className="mb-2 block text-sm font-semibold text-slate-400">
                        Paper 2 Abstract
                      </label>

                      <textarea
                        value={abstract2}
                        onChange={(e) =>
                          setAbstract2(
                            e.target.value
                          )
                        }
                        rows={6}
                        placeholder="Paste second paper abstract..."
                        className="w-full resize-none rounded-xl border border-slate-700 bg-[#071525] px-5 py-3 text-white outline-none focus:border-cyan-400"
                      />

                    </div>

                  </div>
                )}

                <button
                  onClick={runAI}
                  disabled={loading}
                  className="rounded-xl bg-cyan-500 px-8 py-3 font-semibold text-black transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {loading
                    ? "AI Processing..."
                    : "Run AI Analysis"}
                </button>

              </div>

              {/* RESULT */}

              {result && (
                <div className="mt-10 border-t border-slate-700 pt-8">

                  <h3 className="mb-6 text-xl font-bold text-cyan-400">
                    AI Result
                  </h3>

                  <ResultRenderer
                    data={result}
                  />

                </div>
              )}

            </div>

          </section>
        )}

      </div>

    </main>
  );
}

/* =====================================================
   COMPONENTS
===================================================== */

function Tab({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded-xl px-5 py-3 text-sm font-semibold transition ${
        active
          ? "bg-cyan-400/10 text-cyan-400"
          : "text-slate-400 hover:bg-slate-800 hover:text-white"
      }`}
    >
      {children}
    </button>
  );
}

function AITab({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full rounded-lg px-3 py-3 text-left text-sm font-medium transition ${
        active
          ? "bg-cyan-400/10 text-cyan-400"
          : "text-slate-400 hover:bg-slate-800 hover:text-white"
      }`}
    >
      {children}
    </button>
  );
}

function Input({
  label,
  value,
  onChange,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
}) {
  return (
    <div>

      <label className="mb-2 block text-sm font-semibold text-slate-400">
        {label}
      </label>

      <input
        value={value}
        onChange={(e) =>
          onChange(e.target.value)
        }
        placeholder={placeholder}
        className="w-full rounded-xl border border-slate-700 bg-[#071525] px-5 py-3 text-white outline-none focus:border-cyan-400"
      />

    </div>
  );
}

function Stat({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="rounded-lg bg-slate-800/50 p-3">

      <p className="text-xs text-slate-500">
        {label}
      </p>

      <p className="mt-1 font-semibold text-white">
        {value}
      </p>

    </div>
  );
}

function EmptyState({
  text,
}: {
  text: string;
}) {
  return (
    <div className="rounded-xl border border-dashed border-slate-700 p-10 text-center">

      <div className="text-4xl">
        🔬
      </div>

      <p className="mt-3 text-slate-400">
        {text}
      </p>

    </div>
  );
}

/* =====================================================
   TOOL INFORMATION
===================================================== */

function getToolTitle(
  tool: AITool
) {
  const titles: Record<
    AITool,
    string
  > = {
    summary: "Research Summary",
    innovation: "Innovation Generator",
    gap: "Research Gap Detector",
    literature: "Literature Review Generator",
    trends: "Research Trend Analyzer",
    citation: "Citation Intelligence",
    chat: "Research Chat Assistant",
    compare: "Research Paper Comparator",
    proposal: "Research Proposal Generator",
    novelty: "Novelty Checker",
    questions: "Research Question Generator",
    methodology: "Methodology Recommender",
  };

  return titles[tool];
}

function getToolDescription(
  tool: AITool
) {
  const descriptions: Record<
    AITool,
    string
  > = {
    summary:
      "Generate a structured summary of a research paper.",
    innovation:
      "Generate startup, product, industry, patent and commercialization opportunities.",
    gap:
      "Identify limitations, research gaps and future opportunities.",
    literature:
      "Generate a structured literature review.",
    trends:
      "Analyze emerging topics, keywords and future research trends.",
    citation:
      "Generate APA, IEEE, MLA, Chicago, BibTeX and RIS citations.",
    chat:
      "Ask questions about a research paper.",
    compare:
      "Compare two research papers.",
    proposal:
      "Generate a structured research proposal.",
    novelty:
      "Evaluate research novelty and patent potential.",
    questions:
      "Generate research questions, objectives and hypotheses.",
    methodology:
      "Recommend methodology, algorithms, datasets and evaluation metrics.",
  };

  return descriptions[tool];
}

/* =====================================================
   RESULT RENDERER
===================================================== */

function ResultRenderer({
  data,
}: {
  data: any;
}) {
  if (!data) return null;

  return (
    <div className="space-y-5">

      {Object.entries(data).map(
        ([key, value]) => (
          <ResultBlock
            key={key}
            label={formatLabel(key)}
            value={value}
          />
        )
      )}

    </div>
  );
}

function ResultBlock({
  label,
  value,
}: {
  label: string;
  value: any;
}) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return null;
  }

  if (Array.isArray(value)) {
    return (
      <div className="rounded-xl border border-slate-700 bg-[#071525] p-5">

        <h4 className="mb-3 font-bold text-white">
          {label}
        </h4>

        <ul className="space-y-2">

          {value.map(
            (item, index) => (
              <li
                key={index}
                className="rounded-lg bg-slate-800/50 p-3 text-sm text-slate-300"
              >
                {typeof item === "object"
                  ? Object.entries(item)
                      .map(
                        ([key, value]) =>
                          `${formatLabel(
                            key
                          )}: ${String(
                            value
                          )}`
                      )
                      .join(" • ")
                  : String(item)}
              </li>
            )
          )}

        </ul>

      </div>
    );
  }

  if (
    typeof value === "object"
  ) {
    return (
      <div className="rounded-xl border border-slate-700 bg-[#071525] p-5">

        <h4 className="mb-3 font-bold text-white">
          {label}
        </h4>

        <div className="space-y-3">

          {Object.entries(value).map(
            ([key, item]) => (
              <div key={key}>

                <p className="text-xs uppercase tracking-wider text-slate-500">
                  {formatLabel(key)}
                </p>

                <p className="mt-1 whitespace-pre-wrap text-sm text-slate-300">
                  {String(item)}
                </p>

              </div>
            )
          )}

        </div>

      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-700 bg-[#071525] p-5">

      <h4 className="mb-2 font-bold text-white">
        {label}
      </h4>

      <p className="whitespace-pre-wrap text-sm leading-7 text-slate-300">
        {String(value)}
      </p>

    </div>
  );
}

function formatLabel(
  value: string
) {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase()
    );
}