import React, { useMemo, useState } from 'react';
import { useTheme } from '../context/ThemeContext';
import { Sparkles, MessageCircle, ShieldCheck, Award, Search, BookOpen } from 'lucide-react';
import seedData from '../data/seedData';

const createAssistantMessage = (question) => {
  const lower = question.toLowerCase();
  const topFunding = seedData.fundingOpportunities
    .slice()
    .sort((a, b) => b.matchScore - a.matchScore)
    .slice(0, 3)
    .map((grant) => `• ${grant.title} (${grant.agency}) - ${grant.awardSize}`)
    .join('\n');

  if (lower.includes('patent')) {
    return `Based on your portfolio, I recommend reviewing top patented innovations in AI, biotech, and clean energy. The platform currently tracks ${seedData.patents.length} patents. A strong approach is to prioritize patents with higher citation density, identify potential licensing partners, and monitor overall freedom-to-operate risk.`;
  }
  if (lower.includes('fund') || lower.includes('grant') || lower.includes('opportunity')) {
    return `I found ${seedData.fundingOpportunities.length} available funding opportunities. Here are three high-priority matches for ambitious research and commercialization efforts:\n${topFunding}\n
Use the Funding Opportunity Discovery page to save and track the applications that align with your team.`;
  }
  if (lower.includes('ai') || lower.includes('machine learning')) {
    return `Your AI strategy should combine applied research with commercialization-ready grant calls. Consider targeting grants in healthcare AI, climate intelligence, or quantum-safe computing. The platform can also help you identify patent-driven innovation themes and connect them to funding sources.`;
  }
  return `I am your AI research concierge. Ask me for funding recommendations, patent strategy, proposal writing tips, stakeholder mapping, or emerging technology signals. You can say things like "Recommend climate tech grants" or "What patents should I license for healthcare AI?"`;
};

export const AiAssistant = () => {
  const theme = useTheme();
  const [query, setQuery] = useState('');
  const [conversation, setConversation] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      text: 'Hello! I can help you build a stronger grant pipeline and turn patent insights into strategic innovation plans.',
    },
  ]);

  const historyCount = conversation.filter((msg) => msg.role === 'user').length;
  const quickPrompts = useMemo(
    () => [
      'Recommend top global funding opportunities for biotech',
      'Summarize the patent portfolio risk level',
      'Build a proposal timeline for an AI grant',
    ],
    []
  );

  const sendQuery = (incoming) => {
    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      text: incoming,
    };
    const assistantResponse = {
      id: `assistant-${Date.now()}`,
      role: 'assistant',
      text: createAssistantMessage(incoming),
    };
    setConversation((prev) => [...prev, userMessage, assistantResponse]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    sendQuery(query.trim());
    setQuery('');
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 style={{ color: theme.colors.text.primary }} className="text-3xl font-bold mb-2 flex items-center gap-3">
          <Sparkles className="w-8 h-8" style={{ color: theme.colors.accent }} />
          AI Research Concierge
        </h1>
        <p style={{ color: theme.colors.text.secondary }} className="text-sm max-w-2xl">
          An embedded AI assistant for funding strategy, patent insights, opportunity matching, and professional proposal planning.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div style={{ backgroundColor: theme.colors.bg.secondary, borderColor: theme.colors.border }} className="border rounded-2xl p-5">
          <div className="flex items-center gap-3">
            <Search className="w-5 h-5 text-purple-400" />
            <div>
              <p style={{ color: theme.colors.text.tertiary }} className="text-[11px] uppercase tracking-[0.18em]">Data Capacity</p>
              <p style={{ color: theme.colors.text.primary }} className="font-semibold text-lg">{seedData.fundingOpportunities.length} Grants</p>
            </div>
          </div>
        </div>
        <div style={{ backgroundColor: theme.colors.bg.secondary, borderColor: theme.colors.border }} className="border rounded-2xl p-5">
          <div className="flex items-center gap-3">
            <ShieldCheck className="w-5 h-5 text-purple-400" />
            <div>
              <p style={{ color: theme.colors.text.tertiary }} className="text-[11px] uppercase tracking-[0.18em]">Patent Signals</p>
              <p style={{ color: theme.colors.text.primary }} className="font-semibold text-lg">{seedData.patents.length} Records</p>
            </div>
          </div>
        </div>
        <div style={{ backgroundColor: theme.colors.bg.secondary, borderColor: theme.colors.border }} className="border rounded-2xl p-5">
          <div className="flex items-center gap-3">
            <Award className="w-5 h-5 text-purple-400" />
            <div>
              <p style={{ color: theme.colors.text.tertiary }} className="text-[11px] uppercase tracking-[0.18em]">Opportunity Focus</p>
              <p style={{ color: theme.colors.text.primary }} className="font-semibold text-lg">AI, Climate, Health</p>
            </div>
          </div>
        </div>
      </div>

      <div style={{ backgroundColor: theme.colors.bg.secondary, borderColor: theme.colors.border }} className="border rounded-3xl p-5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
          <div>
            <h2 style={{ color: theme.colors.text.primary }} className="text-xl font-semibold">Ask the Assistant</h2>
            <p style={{ color: theme.colors.text.secondary }} className="text-sm">Use natural language prompts to get funding strategy guidance, patent insights, and trend recommendations.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {quickPrompts.map((prompt) => (
              <button
                key={prompt}
                onClick={() => sendQuery(prompt)}
                className="rounded-full border px-4 py-2 text-xs font-semibold"
                style={{ borderColor: theme.colors.border, color: theme.colors.text.primary }}
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-3 sm:flex-row">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask about funding, patents, or proposal strategy..."
            className="flex-1 rounded-2xl border px-4 py-3 text-sm focus:outline-none"
            style={{ backgroundColor: theme.colors.bg.primary, borderColor: theme.colors.border, color: theme.colors.text.primary }}
          />
          <button
            type="submit"
            className="rounded-2xl bg-purple-500 px-5 py-3 text-sm font-semibold text-white hover:bg-purple-400"
          >
            Send
          </button>
        </form>
      </div>

      <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
        <div style={{ backgroundColor: theme.colors.bg.secondary, borderColor: theme.colors.border }} className="border rounded-3xl p-5 space-y-4">
          <div className="flex items-center gap-3">
            <MessageCircle className="w-5 h-5 text-purple-400" />
            <h3 style={{ color: theme.colors.text.primary }} className="text-lg font-semibold">Conversation History</h3>
          </div>
          <div className="space-y-3">
            {conversation.map((message) => (
              <div
                key={message.id}
                style={{ backgroundColor: message.role === 'assistant' ? theme.colors.bg.primary : theme.colors.accent + '12', borderColor: theme.colors.border }}
                className="rounded-3xl border p-4"
              >
                <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.2em]">
                  <span className="font-semibold" style={{ color: message.role === 'assistant' ? theme.colors.accent : theme.colors.text.primary }}>
                    {message.role === 'assistant' ? 'AI Assistant' : 'You'}
                  </span>
                </div>
                <p style={{ whiteSpace: 'pre-wrap', color: theme.colors.text.secondary }} className="text-sm leading-relaxed">{message.text}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <div style={{ backgroundColor: theme.colors.bg.secondary, borderColor: theme.colors.border }} className="border rounded-3xl p-5">
            <div className="flex items-center gap-3 mb-4">
              <BookOpen className="w-5 h-5 text-purple-400" />
              <h3 style={{ color: theme.colors.text.primary }} className="text-lg font-semibold">How to use the concierge</h3>
            </div>
            <ul className="space-y-3 text-sm" style={{ color: theme.colors.text.secondary }}>
              <li>• Ask for match summaries across grants and patents.</li>
              <li>• Request proposal outlines or milestones for your next application.</li>
              <li>• Use the saved funding page to organize and prioritize your best opportunities.</li>
            </ul>
          </div>

          <div style={{ backgroundColor: theme.colors.bg.secondary, borderColor: theme.colors.border }} className="border rounded-3xl p-5">
            <div className="flex items-center gap-3 mb-4">
              <ShieldCheck className="w-5 h-5 text-purple-400" />
              <h3 style={{ color: theme.colors.text.primary }} className="text-lg font-semibold">Assistant Insights</h3>
            </div>
            <div className="space-y-3 text-sm" style={{ color: theme.colors.text.secondary }}>
              <p>• High-priority grants are updated based on top match scores and strategic sectors.</p>
              <p>• Patent guidance focuses on citation impact, portfolio strength, and commercialization risk.</p>
              <p>• The AI Concierge can help you align research goals to funding cycles and licensing strategy.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
