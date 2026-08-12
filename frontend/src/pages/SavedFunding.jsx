import React, { useEffect, useMemo, useState } from 'react';
import { Bookmark, Clock, Globe2, ExternalLink, ArrowRight } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import seedData from '../data/seedData';

export const SavedFunding = ({ setActiveTab }) => {
  const theme = useTheme();
  const [savedIds, setSavedIds] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('savedFunding') || '[]');
    } catch {
      return [];
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem('savedFunding', JSON.stringify(savedIds));
    } catch (error) {
      console.error('Unable to persist saved grants', error);
    }
  }, [savedIds]);

  const savedGrants = useMemo(
    () => seedData.fundingOpportunities.filter((grant) => savedIds.includes(grant.id)),
    [savedIds]
  );

  const nextDeadline = useMemo(() => {
    const upcoming = savedGrants
      .filter((grant) => grant.deadline)
      .sort((a, b) => new Date(a.deadline) - new Date(b.deadline));
    return upcoming[0]?.deadline || null;
  }, [savedGrants]);

  const totalAward = savedGrants.reduce((sum, grant) => sum + (grant.fundingAmount || 0), 0);
  const recommended = useMemo(
    () => seedData.fundingOpportunities
      .filter((grant) => !savedIds.includes(grant.id))
      .sort((a, b) => b.matchScore - a.matchScore)
      .slice(0, 3),
    [savedIds]
  );

  const removeSavedGrant = (grantId) => {
    setSavedIds((current) => current.filter((id) => id !== grantId));
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 style={{ color: theme.colors.text.primary }} className="text-3xl font-bold mb-2 flex items-center gap-3">
          <Bookmark className="w-8 h-8" style={{ color: theme.colors.accent }} />
          Saved Funding Opportunities
        </h1>
        <p style={{ color: theme.colors.text.secondary }} className="text-sm max-w-2xl">
          Easily manage your priority opportunities and revisit targeted funding calls with detailed notes, next deadlines, and recommended follow-up actions.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div style={{ backgroundColor: theme.colors.bg.secondary, borderColor: theme.colors.border }} className="border rounded-xl p-5">
          <p style={{ color: theme.colors.text.tertiary }} className="text-[11px] uppercase tracking-[0.18em] mb-2">Saved Opportunities</p>
          <p style={{ color: theme.colors.text.primary }} className="text-3xl font-semibold">{savedGrants.length}</p>
        </div>
        <div style={{ backgroundColor: theme.colors.bg.secondary, borderColor: theme.colors.border }} className="border rounded-xl p-5">
          <p style={{ color: theme.colors.text.tertiary }} className="text-[11px] uppercase tracking-[0.18em] mb-2">Total Award Potential</p>
          <p style={{ color: theme.colors.text.primary }} className="text-3xl font-semibold">${Math.round(totalAward / 1000)}K</p>
        </div>
        <div style={{ backgroundColor: theme.colors.bg.secondary, borderColor: theme.colors.border }} className="border rounded-xl p-5">
          <p style={{ color: theme.colors.text.tertiary }} className="text-[11px] uppercase tracking-[0.18em] mb-2">Next Deadline</p>
          <p style={{ color: theme.colors.text.primary }} className="text-3xl font-semibold">{nextDeadline ? new Date(nextDeadline).toLocaleDateString() : 'No active deadline'}</p>
        </div>
      </div>

      {savedGrants.length === 0 ? (
        <div style={{ backgroundColor: theme.colors.bg.secondary, borderColor: theme.colors.border }} className="border rounded-xl p-6 text-center">
          <p style={{ color: theme.colors.text.primary }} className="font-semibold text-lg mb-2">No saved opportunities yet</p>
          <p style={{ color: theme.colors.text.secondary }} className="text-sm mb-4">
            Save the strongest matches from the Funding Opportunity Discovery section to build a professional funding pipeline.
          </p>
          <button
            onClick={() => setActiveTab && setActiveTab('funding')}
            className="inline-flex items-center gap-2 rounded-full px-4 py-2 border font-semibold"
            style={{ borderColor: theme.colors.accent, color: theme.colors.accent }}
          >
            <ArrowRight className="w-4 h-4" />
            Go to Funding Discovery
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {savedGrants.map((grant) => (
            <div key={grant.id} style={{ backgroundColor: theme.colors.bg.primary, borderColor: theme.colors.border }} className="border rounded-2xl p-5">
              <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                <div>
                  <p style={{ color: theme.colors.text.primary }} className="font-semibold text-lg">{grant.title}</p>
                  <p style={{ color: theme.colors.text.secondary }} className="text-sm mt-1">{grant.agency} • {grant.awardSize}</p>
                  <p style={{ color: theme.colors.text.secondary }} className="text-sm mt-2">{grant.description_full || grant.description}</p>
                </div>
                <div className="flex flex-wrap gap-2 items-center">
                  <div className="rounded-full bg-slate-800 px-3 py-2 text-xs" style={{ color: theme.colors.text.primary }}>{grant.status}</div>
                  <div className="rounded-full bg-purple-500/10 px-3 py-2 text-xs text-purple-300">Match {grant.matchScore}%</div>
                </div>
              </div>
              <div className="mt-4 grid gap-3 sm:grid-cols-3 text-sm" style={{ color: theme.colors.text.secondary }}>
                <div>
                  <p className="text-[11px] uppercase tracking-[0.18em] mb-1">Deadline</p>
                  <p style={{ color: theme.colors.text.primary }}>{new Date(grant.deadline).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-[11px] uppercase tracking-[0.18em] mb-1">Sector</p>
                  <p style={{ color: theme.colors.text.primary }}>{grant.sector}</p>
                </div>
                <div>
                  <p className="text-[11px] uppercase tracking-[0.18em] mb-1">Suggested Action</p>
                  <p style={{ color: theme.colors.text.primary }}>Prepare executive summary</p>
                </div>
              </div>
              <div className="mt-4 flex flex-wrap gap-3">
                <button
                  onClick={() => removeSavedGrant(grant.id)}
                  className="rounded-lg border px-4 py-2 text-sm font-medium"
                  style={{ borderColor: theme.colors.border, color: theme.colors.text.primary }}
                >
                  Remove
                </button>
                <a
                  href={grant.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 rounded-lg bg-purple-500 px-4 py-2 text-sm font-semibold text-white"
                >
                  <ExternalLink className="w-4 h-4" />
                  View Opportunity
                </a>
              </div>
            </div>
          ))}
        </div>
      )}

      <div style={{ backgroundColor: theme.colors.bg.secondary, borderColor: theme.colors.border }} className="border rounded-2xl p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 style={{ color: theme.colors.text.primary }} className="text-lg font-semibold">Recommended Next Opportunities</h2>
            <p style={{ color: theme.colors.text.secondary }} className="text-sm">Curated from your saved portfolio and current opportunity pipeline.</p>
          </div>
          <Globe2 className="w-5 h-5 text-purple-400" />
        </div>
        <div className="grid gap-4 lg:grid-cols-3">
          {recommended.map((grant) => (
            <div key={grant.id} style={{ backgroundColor: theme.colors.bg.primary, borderColor: theme.colors.border }} className="border rounded-2xl p-4">
              <p style={{ color: theme.colors.text.primary }} className="font-semibold">{grant.title}</p>
              <p style={{ color: theme.colors.text.secondary }} className="text-xs mt-2">{grant.agency}</p>
              <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400">
                <span>{grant.status}</span>
                <span>Match {grant.matchScore}%</span>
              </div>
              <div className="mt-4 flex items-center gap-2">
                <ArrowRight className="w-4 h-4 text-purple-400" />
                <span style={{ color: theme.colors.text.tertiary }} className="text-xs">Explore this opportunity in Funding Discovery.</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
