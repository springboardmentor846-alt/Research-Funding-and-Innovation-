import React, { useEffect, useState } from 'react';
import { useTheme } from '../context/ThemeContext';
import { Search, Calendar, ExternalLink, Bookmark, CheckCircle2, AlertCircle, Sparkles, Building, Send } from 'lucide-react';
import seedData from '../data/seedData';

export const FundingDiscovery = () => {
  const theme = useTheme();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAgency, setSelectedAgency] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [minAmount, setMinAmount] = useState(0);
  const [savedGrants, setSavedGrants] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('savedFunding') || '[]');
    } catch {
      return [];
    }
  });
  const [selectedGrant, setSelectedGrant] = useState(null);
  const [showApplicationForm, setShowApplicationForm] = useState(false);
  const [applicationData, setApplicationData] = useState({
    projectTitle: '',
    description: '',
    budget: '',
    timeline: '',
  });
  const [applications, setApplications] = useState([]);
  const [successMessage, setSuccessMessage] = useState('');

  const grants = seedData.fundingOpportunities;
  const savedGrantObjects = grants.filter((grant) => savedGrants.includes(grant.id));
  const statusOptions = ['ALL', ...new Set(grants.map((g) => g.status))];
  const fundingPool = grants.reduce((sum, grant) => sum + (grant.maxAmount || 0), 0);
  const topSector = Object.entries(
    grants.reduce((counts, grant) => {
      counts[grant.sector] = (counts[grant.sector] || 0) + 1;
      return counts;
    }, {})
  ).sort((a, b) => b[1] - a[1])[0]?.[0] || 'Diverse';
  const nextDeadline = [...grants]
    .sort((a, b) => new Date(a.deadline) - new Date(b.deadline))[0]?.deadline || '';

  // Filter grants
  const filteredGrants = grants.filter(grant => {
    const matchesSearch =
      grant.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      grant.agency.toLowerCase().includes(searchQuery.toLowerCase()) ||
      grant.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesAgency = selectedAgency === 'ALL' || grant.agency === selectedAgency;
    const matchesStatus = selectedStatus === 'ALL' || grant.status === selectedStatus;
    const matchesAmount = grant.fundingAmount >= minAmount;
    return matchesSearch && matchesAgency && matchesStatus && matchesAmount;
  });

  const toggleSaveGrant = (grantId) => {
    setSavedGrants(prev =>
      prev.includes(grantId) ? prev.filter(id => id !== grantId) : [...prev, grantId]
    );
  };

  useEffect(() => {
    try {
      localStorage.setItem('savedFunding', JSON.stringify(savedGrants));
    } catch (error) {
      console.error('Unable to persist saved grants', error);
    }
  }, [savedGrants]);

  const handleApplyClick = (grant) => {
    setSelectedGrant(grant);
    setShowApplicationForm(true);
  };

  const handleSubmitApplication = (e) => {
    e.preventDefault();

    if (!applicationData.projectTitle || !applicationData.description) {
      alert('Please fill in all required fields');
      return;
    }

    // Create application record
    const newApplication = {
      id: `app-${Date.now()}`,
      grantId: selectedGrant.id,
      grantTitle: selectedGrant.title,
      agency: selectedGrant.agency,
      submittedDate: new Date().toLocaleDateString(),
      status: 'SUBMITTED',
      projectTitle: applicationData.projectTitle,
      description: applicationData.description,
      budget: applicationData.budget,
      timeline: applicationData.timeline,
    };

    setApplications(prev => [newApplication, ...prev]);
    setSuccessMessage(`✓ Application submitted successfully to ${selectedGrant.agency}!`);
    
    // Reset form
    setApplicationData({ projectTitle: '', description: '', budget: '', timeline: '' });
    setShowApplicationForm(false);
    setSelectedGrant(null);

    // Clear success message after 5 seconds
    setTimeout(() => setSuccessMessage(''), 5000);
  };

  const agencies = ['ALL', ...new Set(grants.map(g => g.agency))];
  const statuses = statusOptions;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 style={{ color: theme.colors.text.primary }} className="text-3xl font-bold mb-2 flex items-center gap-2">
          <Sparkles className="w-8 h-8" style={{ color: theme.colors.accent }} />
          Funding Opportunity Discovery
        </h1>
        <p style={{ color: theme.colors.text.secondary }} className="text-sm">
          Discover and match with {grants.length} premium funding opportunities personalized to your research profile
        </p>
      </div>
 
      {/* Funding Insights */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div style={{ backgroundColor: theme.colors.bg.secondary, borderColor: theme.colors.border }} className="border rounded-lg p-4">
          <p style={{ color: theme.colors.text.tertiary }} className="text-xs uppercase tracking-[0.2em] mb-2">Total Opportunities</p>
          <p style={{ color: theme.colors.text.primary }} className="text-2xl font-bold">{grants.length}</p>
        </div>
        <div style={{ backgroundColor: theme.colors.bg.secondary, borderColor: theme.colors.border }} className="border rounded-lg p-4">
          <p style={{ color: theme.colors.text.tertiary }} className="text-xs uppercase tracking-[0.2em] mb-2">Total Award Pool</p>
          <p style={{ color: theme.colors.text.primary }} className="text-2xl font-bold">${Math.round(fundingPool / 1000000)}M+</p>
        </div>
        <div style={{ backgroundColor: theme.colors.bg.secondary, borderColor: theme.colors.border }} className="border rounded-lg p-4">
          <p style={{ color: theme.colors.text.tertiary }} className="text-xs uppercase tracking-[0.2em] mb-2">Top Sector</p>
          <p style={{ color: theme.colors.text.primary }} className="text-2xl font-bold">{topSector}</p>
        </div>
        <div style={{ backgroundColor: theme.colors.bg.secondary, borderColor: theme.colors.border }} className="border rounded-lg p-4">
          <p style={{ color: theme.colors.text.tertiary }} className="text-xs uppercase tracking-[0.2em] mb-2">Next Deadline</p>
          <p style={{ color: theme.colors.text.primary }} className="text-2xl font-bold">{nextDeadline ? new Date(nextDeadline).toLocaleDateString() : 'N/A'}</p>
        </div>
      </div>
 
      {/* Success Message */}
      {successMessage && (
        <div
          style={{
            backgroundColor: theme.isDark ? '#064e3b' : '#ecfdf5',
            borderColor: theme.isDark ? '#10b981' : '#a7f3d0',
            color: theme.isDark ? '#a7f3d0' : '#065f46',
          }}
          className="p-4 rounded-lg border flex items-start gap-3 animate-pulse"
        >
          <CheckCircle2 className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-sm">{successMessage}</p>
            <p className="text-xs mt-1">Your application has been submitted and saved to your profile.</p>
          </div>
        </div>
      )}

      {/* Search & Filters */}
      <div
        style={{
          backgroundColor: theme.colors.bg.secondary,
          borderColor: theme.colors.border,
        }}
        className="border rounded-lg p-4 space-y-4"
      >
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-3 w-5 h-5" style={{ color: theme.colors.text.tertiary }} />
          <input
            type="text"
            placeholder="Search by title, agency, keywords..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              backgroundColor: theme.colors.bg.primary,
              borderColor: theme.colors.border,
              color: theme.colors.text.primary,
            }}
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2"
          />
        </div>

        {/* Filters */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Agency Filter */}
          <div>
            <label style={{ color: theme.colors.text.secondary }} className="text-sm font-medium block mb-2">
              Funding Agency
            </label>
            <select
              value={selectedAgency}
              onChange={(e) => setSelectedAgency(e.target.value)}
              style={{
                backgroundColor: theme.colors.bg.primary,
                borderColor: theme.colors.border,
                color: theme.colors.text.primary,
              }}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2"
            >
              {agencies.map((agency) => (
                <option key={agency} value={agency}>
                  {agency === 'ALL' ? 'All Agencies' : agency}
                </option>
              ))}
            </select>
          </div>
 
          {/* Status Filter */}
          <div>
            <label style={{ color: theme.colors.text.secondary }} className="text-sm font-medium block mb-2">
              Application Status
            </label>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              style={{
                backgroundColor: theme.colors.bg.primary,
                borderColor: theme.colors.border,
                color: theme.colors.text.primary,
              }}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2"
            >
              {statuses.map((status) => (
                <option key={status} value={status}>
                  {status === 'ALL' ? 'All Statuses' : status.replace('_', ' ')}
                </option>
              ))}
            </select>
          </div>
 
          {/* Amount Filter */}
          <div>
            <label style={{ color: theme.colors.text.secondary }} className="text-sm font-medium block mb-2">
              Min Amount: ${(minAmount / 1000).toFixed(0)}K
            </label>
            <input
              type="range"
              min="0"
              max="5000000"
              step="100000"
              value={minAmount}
              onChange={(e) => setMinAmount(Number(e.target.value))}
              style={{ accentColor: theme.colors.accent }}
              className="w-full"
            />
          </div>
 
          {/* Stats */}
          <div style={{ backgroundColor: theme.colors.bg.primary }} className="rounded-lg p-3 flex items-center justify-between">
            <div>
              <p style={{ color: theme.colors.text.tertiary }} className="text-xs">Matching Opportunities</p>
              <p style={{ color: theme.colors.text.primary }} className="text-2xl font-bold">
                {filteredGrants.length}
              </p>
            </div>
            <Sparkles style={{ color: theme.colors.accent }} className="w-8 h-8 opacity-50" />
          </div>
        </div>
      </div>
 
      {/* Saved Grants */}
      {savedGrantObjects.length > 0 && (
        <div
          style={{
            backgroundColor: theme.colors.bg.secondary,
            borderColor: theme.colors.border,
          }}
          className="border rounded-lg p-4"
        >
          <h2 style={{ color: theme.colors.text.primary }} className="font-semibold mb-3 flex items-center gap-2">
            <Bookmark className="w-5 h-5" style={{ color: theme.colors.accent }} />
            Saved Grants ({savedGrantObjects.length})
          </h2>
          <div className="grid gap-3 md:grid-cols-2">
            {savedGrantObjects.map((grant) => (
              <div
                key={grant.id}
                style={{ backgroundColor: theme.colors.bg.primary, borderColor: theme.colors.border }}
                className="p-3 rounded border"
              >
                <p style={{ color: theme.colors.text.primary }} className="font-semibold text-sm">
                  {grant.title}
                </p>
                <p style={{ color: theme.colors.text.tertiary }} className="text-xs mt-1">
                  {grant.agency} • {(grant.awardSize || '').toString()}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
 
      {/* Active Applications */}
      {applications.length > 0 && (
        <div
          style={{
            backgroundColor: theme.colors.bg.secondary,
            borderColor: theme.colors.border,
          }}
          className="border rounded-lg p-4"
        >
          <h2 style={{ color: theme.colors.text.primary }} className="font-semibold mb-3 flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5" style={{ color: theme.colors.success }} />
            Your Applications ({applications.length})
          </h2>
          <div className="space-y-2">
            {applications.map(app => (
              <div
                key={app.id}
                style={{
                  backgroundColor: theme.colors.bg.primary,
                  borderColor: theme.colors.accent,
                  borderLeftWidth: '4px',
                }}
                className="p-3 rounded border"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p style={{ color: theme.colors.text.primary }} className="font-medium text-sm">
                      {app.projectTitle}
                    </p>
                    <p style={{ color: theme.colors.text.tertiary }} className="text-xs mt-1">
                      {app.agency} • Submitted {app.submittedDate}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 px-3 py-1 rounded-full" style={{ backgroundColor: theme.colors.success + '20' }}>
                    <CheckCircle2 className="w-3 h-3" style={{ color: theme.colors.success }} />
                    <span style={{ color: theme.colors.success }} className="text-xs font-medium">{app.status}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Funding Opportunities List */}
      <div className="space-y-3">
        {filteredGrants.length > 0 ? (
          filteredGrants.map(grant => (
            <div
              key={grant.id}
              style={{
                backgroundColor: theme.colors.bg.secondary,
                borderColor: theme.colors.border,
              }}
              className="border rounded-lg p-4 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-start gap-2 mb-2">
                    <Building style={{ color: theme.colors.accent }} className="w-5 h-5 flex-shrink-0 mt-0.5" />
                    <div>
                      <h3 style={{ color: theme.colors.text.primary }} className="font-bold text-lg">
                        {grant.title}
                      </h3>
                      <p style={{ color: theme.colors.text.tertiary }} className="text-sm">
                        {grant.agency}
                      </p>
                    </div>
                  </div>
                  <p style={{ color: theme.colors.text.secondary }} className="text-sm mb-3">
                    {grant.description_full || grant.description}
                  </p>
                </div>

                {/* Match Score Badge */}
                <div
                  style={{
                    backgroundColor: grant.matchScore > 85 ? '#10b98120' : '#f59e0b20',
                    color: grant.matchScore > 85 ? '#10b981' : '#f59e0b',
                  }}
                  className="px-3 py-1 rounded-full text-center whitespace-nowrap"
                >
                  <p className="font-bold text-sm">{grant.matchScore}%</p>
                  <p className="text-xs">Match</p>
                </div>
              </div>

              {/* Grant Details */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                <div>
                  <p style={{ color: theme.colors.text.tertiary }} className="text-xs mb-1">Funding Amount</p>
                  <p style={{ color: theme.colors.text.primary }} className="font-bold text-sm">
                    ${(grant.fundingAmount / 1000).toFixed(0)}K
                  </p>
                </div>
                <div>
                  <p style={{ color: theme.colors.text.tertiary }} className="text-xs mb-1">Deadline</p>
                  <p style={{ color: theme.colors.text.primary }} className="font-bold text-sm flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {new Date(grant.deadline).toLocaleDateString()}
                  </p>
                </div>
                <div>
                  <p style={{ color: theme.colors.text.tertiary }} className="text-xs mb-1">Duration</p>
                  <p style={{ color: theme.colors.text.primary }} className="font-bold text-sm">
                    {grant.duration}
                  </p>
                </div>
                <div>
                  <p style={{ color: theme.colors.text.tertiary }} className="text-xs mb-1">Status</p>
                  <div className="flex items-center gap-1">
                    <div
                      style={{
                        backgroundColor: grant.status === 'CLOSING_SOON' ? '#ef4444' : '#10b981',
                      }}
                      className="w-2 h-2 rounded-full"
                    />
                    <p style={{ color: theme.colors.text.primary }} className="font-bold text-sm">
                      {grant.status}
                    </p>
                  </div>
                </div>
              </div>

              {/* Keywords & Domains */}
              <div className="mb-4">
                <p style={{ color: theme.colors.text.tertiary }} className="text-xs mb-2">Keywords & Domains:</p>
                <div className="flex flex-wrap gap-2">
                  {[...grant.domains, ...grant.keywords.slice(0, 2)].map((tag, idx) => (
                    <span
                      key={idx}
                      style={{
                        backgroundColor: theme.colors.accent + '20',
                        color: theme.colors.accent,
                      }}
                      className="text-xs px-2 py-1 rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2 pt-3" style={{ borderTopColor: theme.colors.border, borderTopWidth: '1px' }}>
                <button
                  onClick={() => handleApplyClick(grant)}
                  style={{
                    backgroundColor: theme.colors.accent,
                    color: 'white',
                  }}
                  className="flex-1 px-4 py-2 rounded-lg font-semibold flex items-center justify-center gap-2 hover:opacity-90 transition-opacity"
                >
                  <Send className="w-4 h-4" />
                  Apply Now
                </button>
                <button
                  onClick={() => toggleSaveGrant(grant.id)}
                  style={{
                    backgroundColor: savedGrants.includes(grant.id) ? theme.colors.accent + '20' : theme.colors.bg.primary,
                    color: savedGrants.includes(grant.id) ? theme.colors.accent : theme.colors.text.tertiary,
                    borderColor: theme.colors.border,
                  }}
                  className="px-4 py-2 rounded-lg border flex items-center gap-2 hover:opacity-80 transition-opacity"
                >
                  <Bookmark className="w-4 h-4" fill={savedGrants.includes(grant.id) ? 'currentColor' : 'none'} />
                </button>
                <a
                  href={grant.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    backgroundColor: theme.colors.bg.primary,
                    borderColor: theme.colors.border,
                    color: theme.colors.accent,
                  }}
                  className="px-4 py-2 rounded-lg border flex items-center gap-2 hover:opacity-80 transition-opacity"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>
          ))
        ) : (
          <div style={{ backgroundColor: theme.colors.bg.secondary, borderColor: theme.colors.border }} className="border rounded-lg p-8 text-center">
            <AlertCircle style={{ color: theme.colors.text.tertiary }} className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p style={{ color: theme.colors.text.secondary }}>No opportunities match your criteria.</p>
            <p style={{ color: theme.colors.text.tertiary }} className="text-sm mt-2">Try adjusting your filters.</p>
          </div>
        )}
      </div>

      {/* Application Form Modal */}
      {showApplicationForm && selectedGrant && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div
            style={{
              backgroundColor: theme.colors.bg.secondary,
              maxHeight: '90vh',
            }}
            className="rounded-lg p-6 w-full max-w-2xl overflow-y-auto"
          >
            <h2 style={{ color: theme.colors.text.primary }} className="text-2xl font-bold mb-2">
              Submit Application
            </h2>
            <p style={{ color: theme.colors.text.secondary }} className="text-sm mb-6">
              Applying to: <strong>{selectedGrant.title}</strong>
            </p>

            <form onSubmit={handleSubmitApplication} className="space-y-4">
              {/* Project Title */}
              <div>
                <label style={{ color: theme.colors.text.secondary }} className="block text-sm font-medium mb-2">
                  Project Title *
                </label>
                <input
                  type="text"
                  value={applicationData.projectTitle}
                  onChange={(e) => setApplicationData(prev => ({ ...prev, projectTitle: e.target.value }))}
                  placeholder="Enter your project title"
                  style={{
                    backgroundColor: theme.colors.bg.primary,
                    borderColor: theme.colors.border,
                    color: theme.colors.text.primary,
                  }}
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2"
                />
              </div>

              {/* Description */}
              <div>
                <label style={{ color: theme.colors.text.secondary }} className="block text-sm font-medium mb-2">
                  Project Description *
                </label>
                <textarea
                  value={applicationData.description}
                  onChange={(e) => setApplicationData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Describe your research project in detail..."
                  rows="5"
                  style={{
                    backgroundColor: theme.colors.bg.primary,
                    borderColor: theme.colors.border,
                    color: theme.colors.text.primary,
                  }}
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 resize-none"
                />
              </div>

              {/* Budget */}
              <div>
                <label style={{ color: theme.colors.text.secondary }} className="block text-sm font-medium mb-2">
                  Requested Budget (USD)
                </label>
                <input
                  type="number"
                  value={applicationData.budget}
                  onChange={(e) => setApplicationData(prev => ({ ...prev, budget: e.target.value }))}
                  placeholder="Enter budget in USD"
                  style={{
                    backgroundColor: theme.colors.bg.primary,
                    borderColor: theme.colors.border,
                    color: theme.colors.text.primary,
                  }}
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2"
                />
              </div>

              {/* Timeline */}
              <div>
                <label style={{ color: theme.colors.text.secondary }} className="block text-sm font-medium mb-2">
                  Project Timeline
                </label>
                <input
                  type="text"
                  value={applicationData.timeline}
                  onChange={(e) => setApplicationData(prev => ({ ...prev, timeline: e.target.value }))}
                  placeholder="e.g., 24 months"
                  style={{
                    backgroundColor: theme.colors.bg.primary,
                    borderColor: theme.colors.border,
                    color: theme.colors.text.primary,
                  }}
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2"
                />
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-6" style={{ borderTopColor: theme.colors.border, borderTopWidth: '1px' }}>
                <button
                  type="button"
                  onClick={() => {
                    setShowApplicationForm(false);
                    setSelectedGrant(null);
                    setApplicationData({ projectTitle: '', description: '', budget: '', timeline: '' });
                  }}
                  style={{
                    backgroundColor: theme.colors.bg.primary,
                    borderColor: theme.colors.border,
                    color: theme.colors.text.primary,
                  }}
                  className="flex-1 px-4 py-2 border rounded-lg font-semibold hover:opacity-80"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    backgroundColor: theme.colors.accent,
                    color: 'white',
                  }}
                  className="flex-1 px-4 py-2 rounded-lg font-semibold hover:opacity-90"
                >
                  Submit Application
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
