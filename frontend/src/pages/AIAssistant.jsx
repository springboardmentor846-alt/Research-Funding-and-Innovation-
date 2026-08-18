import React, { useState } from "react";
import { aiAPI } from "../services/api.js";

const tabs = [
  { key: "summarize", label: "Summarize Paper", icon: "📄" },
  { key: "explain-patent", label: "Explain Patent", icon: "🔬" },
  { key: "explain-concept", label: "Explain Concept", icon: "💡" },
  { key: "literature-review", label: "Literature Review", icon: "📚" },
  { key: "commercialization", label: "Commercialization", icon: "💼" },
  { key: "research-directions", label: "Research Directions", icon: "🧭" },
];

export default function AIAssistant() {
  const [tab, setTab] = useState("summarize");
  const [input, setInput] = useState("");
  const [output, setOutput] = useState("");
  const [outputList, setOutputList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function run() {
    if (!input.trim()) {
      setError("Please enter some text");
      return;
    }
    setLoading(true);
    setError("");
    setOutput("");
    setOutputList([]);
    try {
      if (tab === "summarize") {
        const r = await aiAPI.summarize(input, 200, 60);
        setOutput(r.data.summary);
      } else if (tab === "explain-patent") {
        const r = await aiAPI.explainPatent(input);
        setOutput(r.data.explanation);
      } else if (tab === "explain-concept") {
        const r = await aiAPI.explainConcept(input);
        setOutput(r.data.explanation);
      } else if (tab === "literature-review") {
        const r = await aiAPI.literatureReview(input);
        setOutput(r.data.review);
      } else if (tab === "commercialization") {
        const r = await aiAPI.commercialization(input);
        setOutputList(r.data.opportunities);
      } else if (tab === "research-directions") {
        const r = await aiAPI.researchDirections(input);
        setOutputList(r.data.directions);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "AI request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">🤖 AI Research Assistant</h1>
        <p className="text-slate-500 text-sm">
          Powered by Hugging Face Transformers, LangChain, and OpenAI
        </p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => { setTab(t.key); setInput(""); setOutput(""); setOutputList([]); setError(""); }}
            className={`p-3 rounded-lg text-sm font-medium transition border ${
              tab === t.key
                ? "bg-primary-600 text-white border-primary-600"
                : "bg-white text-slate-700 border-slate-200 hover:border-primary-300"
            }`}
          >
            <div className="text-xl mb-1">{t.icon}</div>
            {t.label}
          </button>
        ))}
      </div>

      <div className="card">
        <label className="label">
          {tab === "summarize" && "Paste a research paper abstract or section"}
          {tab === "explain-patent" && "Paste a patent abstract or claim text"}
          {tab === "explain-concept" && "Enter a technical concept to explain"}
          {tab === "literature-review" && "Enter a research topic"}
          {tab === "commercialization" && "Paste an abstract to identify commercialization opportunities"}
          {tab === "research-directions" && "Paste an abstract to suggest future research directions"}
        </label>
        <textarea
          className="input min-h-[180px]"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type or paste your content here..."
        />
        <button onClick={run} disabled={loading} className="btn-primary mt-3">
          {loading ? "Thinking..." : "Run AI"}
        </button>
      </div>

      {error && <div className="card bg-red-50 text-red-700">{error}</div>}

      {output && (
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-3">AI Response</h3>
          <div className="text-sm text-slate-700 whitespace-pre-wrap bg-slate-50 p-4 rounded-lg">
            {output}
          </div>
        </div>
      )}

      {outputList.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-slate-800 mb-3">AI Suggestions</h3>
          <ul className="space-y-2">
            {outputList.map((item, i) => (
              <li key={i} className="flex items-start gap-2 p-3 bg-slate-50 rounded-lg">
                <span className="text-primary-600 font-bold">{i + 1}.</span>
                <span className="text-sm text-slate-700">{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
