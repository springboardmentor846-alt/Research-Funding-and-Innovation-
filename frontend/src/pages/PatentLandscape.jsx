import React, { useMemo, useState } from 'react';
import { ShieldCheck, Search, Layers, FileText, ArrowRight } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import seedData from '../data/seedData';

export const PatentLandscape = () => {
  const theme = useTheme();
  const [search, setSearch] = useState('');
  const [patents, setPatents] = useState(seedData.patents);
  const [selectedPatent, setSelectedPatent] = useState(null);
  const [newPatent, setNewPatent] = useState({
    number: '',
    title: '',
    assignee: '',
    ipc: '',
    domain: '',
    filingDate: '',
    grantDate: '',
    citations: '',
    abstract: '',
    status: 'Pending',
    technology: '',
    field: '',
    inventors: '',
  });
  const [successMessage, setSuccessMessage] = useState('');

  const filteredPatents = patents.filter((p) => {
    const query = search.toLowerCase();
    return (
      (p.title || '').toLowerCase().includes(query) ||
      (p.number || '').toLowerCase().includes(query) ||
      (p.assignee || '').toLowerCase().includes(query) ||
      (p.ipc || '').toLowerCase().includes(query) ||
      (p.domain || '').toLowerCase().includes(query) ||
      (p.technology || '').toLowerCase().includes(query) ||
      (p.abstract || '').toLowerCase().includes(query)
    );
  });

  const portfolioSummary = useMemo(() => {
    const total = patents.length;
    const totalCitations = patents.reduce((sum, patent) => sum + (patent.citations || 0), 0);
    const assigneeCounts = patents.reduce((counts, patent) => {
      const assignee = patent.assignee || 'Unknown';
      counts[assignee] = (counts[assignee] || 0) + 1;
      return counts;
    }, {});
    const topAssignee = Object.entries(assigneeCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || 'Diverse Portfolio';
    const ipcCounts = patents.reduce((counts, patent) => {
      const ipc = patent.ipc || 'Unclassified';
      counts[ipc] = (counts[ipc] || 0) + 1;
      return counts;
    }, {});
    const topIpc = Object.entries(ipcCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A';

    return {
      total,
      averageCitations: total ? Math.round(totalCitations / total) : 0,
      topAssignee,
      topIpc,
      totalCitations,
      totalClusters: new Set(patents.map((p) => p.cluster || p.ipc || 'unknown')).size,
    };
  }, [patents]);

  const handleNewPatentChange = (field, value) => {
    setNewPatent((prev) => ({ ...prev, [field]: value }));
  };

  const handleAddPatent = (e) => {
    e.preventDefault();
    if (!newPatent.number || !newPatent.title || !newPatent.assignee || !newPatent.ipc) {
      alert('Please fill in the patent number, title, assignee, and IPC classification.');
      return;
    }

    const addedPatent = {
      ...newPatent,
      citations: Number(newPatent.citations) || 0,
      id: `pat-${Date.now()}`,
      status: newPatent.status || 'Pending',
      technology: newPatent.technology || 'Emerging Technology',
      field: newPatent.field || 'General',
      inventors: newPatent.inventors ? newPatent.inventors.split(',').map((name) => name.trim()) : ['Unknown'],
    };

    setPatents((prev) => [addedPatent, ...prev]);
    setSuccessMessage(`Patent ${addedPatent.number} added successfully.`);
    setNewPatent({
      number: '',
      title: '',
      assignee: '',
      ipc: '',
      domain: '',
      filingDate: '',
      grantDate: '',
      citations: '',
      abstract: '',
      status: 'Pending',
      technology: '',
      field: '',
      inventors: '',
    });
    setTimeout(() => setSuccessMessage(''), 5000);
  };

  const openPatentDetails = (patent) => {
    setSelectedPatent(patent);
  };

  const closePatentDetails = () => setSelectedPatent(null);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 style={{ color: theme.colors.text.primary }} className="text-2xl font-extrabold tracking-tight flex items-center space-x-2">
          <ShieldCheck className="w-6 h-6 text-purple-400" />
          <span>Patent Landscape & Intellectual Property Analytics</span>
        </h2>
        <p style={{ color: theme.colors.text.secondary }} className="text-xs mt-1">
          Patent cluster mapping, International Patent Classification (IPC) code distribution, competitor assignee tracking, and citation density analysis.
        </p>
      </div>

      {/* Analytics Overview Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl glass-panel space-y-2">
          <div style={{ color: theme.colors.text.tertiary }} className="text-[11px] font-semibold uppercase">Top Assignee Volume</div>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between" style={{ color: theme.colors.text.primary }}>
              <span>{portfolioSummary.topAssignee}</span>
              <span className="font-bold text-cyan-400">{patents.filter((p) => p.assignee === portfolioSummary.topAssignee).length} Patents</span>
            </div>
            <div className="flex justify-between" style={{ color: theme.colors.text.primary }}><span>Google LLC</span><span className="font-bold text-cyan-400">142 Patents</span></div>
            <div className="flex justify-between" style={{ color: theme.colors.text.primary }}><span>Stanford University</span><span className="font-bold text-cyan-400">89 Patents</span></div>
          </div>
        </div>

        <div className="p-4 rounded-xl glass-panel space-y-2">
          <div style={{ color: theme.colors.text.tertiary }} className="text-[11px] font-semibold uppercase">IPC Code Breakdown</div>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between" style={{ color: theme.colors.text.primary }}>
              <span>{portfolioSummary.topIpc} (Top Code)</span>
              <span className="font-bold text-purple-400">{Object.entries(patents.reduce((counts, patent) => { counts[patent.ipc] = (counts[patent.ipc] || 0) + 1; return counts; }, {})).sort((a, b) => b[1] - a[1])[0]?.[1] || 1} patents</span>
            </div>
            <div className="flex justify-between" style={{ color: theme.colors.text.primary }}><span>H01M (Energy Storage)</span><span className="font-bold text-purple-400">28.1%</span></div>
            <div className="flex justify-between" style={{ color: theme.colors.text.primary }}><span>C12N (Genomics / Biotech)</span><span className="font-bold text-purple-400">17.7%</span></div>
          </div>
        </div>

        <div className="p-4 rounded-xl glass-panel space-y-2">
          <div style={{ color: theme.colors.text.tertiary }} className="text-[11px] font-semibold uppercase">Cluster Density</div>
          <div className="text-2xl font-bold text-emerald-400">{portfolioSummary.totalClusters} Active Clusters</div>
          <p style={{ color: theme.colors.text.secondary }} className="text-[11px]">Low Freedom-To-Operate collision risk identified.</p>
        </div>

        <div className="p-4 rounded-xl glass-panel space-y-2">
          <div style={{ color: theme.colors.text.tertiary }} className="text-[11px] font-semibold uppercase">Patent Portfolio</div>
          <div className="text-2xl font-bold" style={{ color: theme.colors.text.primary }}>{portfolioSummary.total}</div>
          <p style={{ color: theme.colors.text.secondary }} className="text-[11px]">Avg. Citations: {portfolioSummary.averageCitations}</p>
        </div>
      </div>

      {/* Patent Search & Table */}
      <div className="grid gap-4 xl:grid-cols-[1.6fr_0.9fr]">
        <div className="p-5 rounded-2xl glass-panel space-y-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <h3 style={{ color: theme.colors.text.primary }} className="text-sm font-bold flex items-center space-x-2">
              <Layers className="w-4 h-4 text-purple-400" />
              <span>Harvested Patent Database</span>
            </h3>
            <div className="relative w-full md:w-80">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by patent #, title, assignee, or IPC..."
                className="w-full bg-slate-900 text-xs text-slate-200 pl-9 pr-4 py-2 rounded-lg border border-slate-800 focus:outline-none focus:border-purple-500"
              />
            </div>
          </div>

          <div className="space-y-3">
            {filteredPatents.length > 0 ? (
              filteredPatents.map((p) => (
                <div key={p.number} className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 font-mono text-[11px] font-bold border border-purple-500/30">{p.number}</span>
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] font-semibold">IPC: {p.ipc}</span>
                    </div>
                    <span className="text-xs text-purple-300 font-bold">{p.citations} Citations</span>
                  </div>

                  <h4 style={{ color: theme.colors.text.primary }} className="text-sm font-bold">{p.title}</h4>
                  <p style={{ color: theme.colors.text.secondary }} className="text-xs leading-relaxed">{p.abstract}</p>

                  <div className="flex flex-wrap gap-2">
                    <span className="rounded-full bg-purple-500/10 px-2 py-1 text-[10px] font-semibold text-purple-300">{p.technology || p.field}</span>
                    <span className="rounded-full bg-slate-800 px-2 py-1 text-[10px] text-slate-300">{p.status}</span>
                  </div>

                  <div className="pt-2 border-t border-slate-800/80 flex flex-col gap-2 text-[11px]" style={{ color: theme.colors.text.secondary }}>
                    <div>Assignee: <span className="font-semibold" style={{ color: theme.colors.text.primary }}>{p.assignee}</span></div>
                    <div>Filing: <span style={{ color: theme.colors.text.primary }}>{p.filingDate}</span> | Granted: <span className="text-emerald-400">{p.grantDate}</span></div>
                    <button
                      onClick={() => openPatentDetails(p)}
                      className="inline-flex items-center gap-1 rounded-lg border border-purple-500/20 bg-purple-500/10 px-3 py-2 text-xs font-semibold text-purple-200 hover:bg-purple-500/20"
                    >
                      <ArrowRight className="w-3.5 h-3.5" />
                      View Details
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-8 text-center">
                <p className="text-slate-400">No patents match your search criteria.</p>
                <p className="text-xs text-slate-500 mt-2">Try a broader search term or add a new patent.</p>
              </div>
            )}
          </div>
        </div>

        {selectedPatent && (
          <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
            <div
              style={{ backgroundColor: theme.colors.bg.secondary }}
              className="w-full max-w-2xl rounded-3xl border border-slate-700 p-6 overflow-y-auto max-h-[90vh]"
            >
              <div className="flex items-start justify-between gap-4 mb-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.18em] font-semibold text-purple-300">Patent Intelligence</p>
                  <h3 style={{ color: theme.colors.text.primary }} className="text-2xl font-bold mt-2">{selectedPatent.title}</h3>
                  <p style={{ color: theme.colors.text.secondary }} className="text-sm mt-1">{selectedPatent.number} • {selectedPatent.assignee}</p>
                </div>
                <button
                  onClick={closePatentDetails}
                  className="rounded-full border border-slate-600 px-3 py-2 text-sm font-semibold text-slate-200 hover:bg-slate-800"
                  style={{ color: theme.colors.text.primary }}
                >
                  Close
                </button>
              </div>

              <div className="grid gap-4 md:grid-cols-2 mb-4 text-sm" style={{ color: theme.colors.text.secondary }}>
                <div className="rounded-2xl bg-slate-900/80 p-4 border border-slate-700">
                  <p className="text-[11px] uppercase tracking-[0.18em] font-semibold mb-2" style={{ color: theme.colors.text.tertiary }}>IPC Classification</p>
                  <p style={{ color: theme.colors.text.primary }} className="font-semibold">{selectedPatent.ipc}</p>
                </div>
                <div className="rounded-2xl bg-slate-900/80 p-4 border border-slate-700">
                  <p className="text-[11px] uppercase tracking-[0.18em] font-semibold mb-2" style={{ color: theme.colors.text.tertiary }}>Status</p>
                  <p style={{ color: theme.colors.text.primary }} className="font-semibold">{selectedPatent.status}</p>
                </div>
                <div className="rounded-2xl bg-slate-900/80 p-4 border border-slate-700">
                  <p className="text-[11px] uppercase tracking-[0.18em] font-semibold mb-2" style={{ color: theme.colors.text.tertiary }}>Filed</p>
                  <p style={{ color: theme.colors.text.primary }} className="font-semibold">{selectedPatent.filingDate}</p>
                </div>
                <div className="rounded-2xl bg-slate-900/80 p-4 border border-slate-700">
                  <p className="text-[11px] uppercase tracking-[0.18em] font-semibold mb-2" style={{ color: theme.colors.text.tertiary }}>Granted</p>
                  <p style={{ color: theme.colors.text.primary }} className="font-semibold">{selectedPatent.grantDate}</p>
                </div>
              </div>

              <div className="rounded-3xl bg-slate-900/80 p-5 border border-slate-700">
                <p className="text-[11px] uppercase tracking-[0.18em] font-semibold mb-3" style={{ color: theme.colors.text.tertiary }}>Abstract & Analysis</p>
                <p style={{ color: theme.colors.text.secondary }} className="text-sm leading-relaxed">{selectedPatent.abstract}</p>
                <div className="mt-4 grid gap-3 md:grid-cols-3 text-xs" style={{ color: theme.colors.text.secondary }}>
                  <div className="rounded-2xl bg-slate-950/90 p-3 border border-slate-800">
                    <div className="text-[10px] uppercase text-slate-400">Citation Count</div>
                    <div style={{ color: theme.colors.text.primary }} className="font-semibold text-lg">{selectedPatent.citations}</div>
                  </div>
                  <div className="rounded-2xl bg-slate-950/90 p-3 border border-slate-800">
                    <div className="text-[10px] uppercase text-slate-400">Field</div>
                    <div style={{ color: theme.colors.text.primary }} className="font-semibold text-lg">{selectedPatent.field}</div>
                  </div>
                  <div className="rounded-2xl bg-slate-950/90 p-3 border border-slate-800">
                    <div className="text-[10px] uppercase text-slate-400">Innovation Risk</div>
                    <div style={{ color: theme.colors.text.primary }} className="font-semibold text-lg">{Math.min(100, 60 + Math.round((selectedPatent.citations || 0) / 20))}%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="space-y-4">
          <div className="p-5 rounded-2xl glass-panel space-y-4">
            <div className="flex items-center justify-between">
              <h3 style={{ color: theme.colors.text.primary }} className="text-sm font-bold">Add New Patent</h3>
              <FileText className="w-4 h-4 text-purple-400" />
            </div>
            {successMessage && (
              <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 text-sm text-emerald-200">
                {successMessage}
              </div>
            )}
            <form onSubmit={handleAddPatent} className="space-y-3">
              <div>
                <label className="text-xs text-slate-400 block mb-1">Patent Number</label>
                <input
                  type="text"
                  value={newPatent.number}
                  onChange={(e) => handleNewPatentChange('number', e.target.value)}
                  className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-slate-100"
                />
              </div>
              <div>
                <label className="text-xs text-slate-400 block mb-1">Title</label>
                <input
                  type="text"
                  value={newPatent.title}
                  onChange={(e) => handleNewPatentChange('title', e.target.value)}
                  className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-slate-100"
                />
              </div>
              <div>
                <label className="text-xs text-slate-400 block mb-1">Assignee</label>
                <input
                  type="text"
                  value={newPatent.assignee}
                  onChange={(e) => handleNewPatentChange('assignee', e.target.value)}
                  className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-slate-100"
                />
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <label className="text-xs text-slate-400 block mb-1">IPC Code</label>
                  <input
                    type="text"
                    value={newPatent.ipc}
                    onChange={(e) => handleNewPatentChange('ipc', e.target.value)}
                    className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-slate-100"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Domain</label>
                  <input
                    type="text"
                    value={newPatent.domain}
                    onChange={(e) => handleNewPatentChange('domain', e.target.value)}
                    className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-slate-100"
                  />
                </div>
              </div>
              <div className="grid gap-3 sm:grid-cols-3">
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Status</label>
                  <select
                    value={newPatent.status}
                    onChange={(e) => handleNewPatentChange('status', e.target.value)}
                    className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-slate-100"
                  >
                    <option value="Pending">Pending</option>
                    <option value="Granted">Granted</option>
                    <option value="Filed">Filed</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Technology</label>
                  <input
                    type="text"
                    value={newPatent.technology}
                    onChange={(e) => handleNewPatentChange('technology', e.target.value)}
                    className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-slate-100"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Field</label>
                  <input
                    type="text"
                    value={newPatent.field}
                    onChange={(e) => handleNewPatentChange('field', e.target.value)}
                    className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-slate-100"
                  />
                </div>
              </div>
              <div>
                <label className="text-xs text-slate-400 block mb-1">Inventors</label>
                <input
                  type="text"
                  value={newPatent.inventors}
                  onChange={(e) => handleNewPatentChange('inventors', e.target.value)}
                  placeholder="Comma-separated names"
                  className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-slate-100"
                />
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Filing Date</label>
                  <input
                    type="date"
                    value={newPatent.filingDate}
                    onChange={(e) => handleNewPatentChange('filingDate', e.target.value)}
                    className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-slate-100"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-400 block mb-1">Grant Date</label>
                  <input
                    type="date"
                    value={newPatent.grantDate}
                    onChange={(e) => handleNewPatentChange('grantDate', e.target.value)}
                    className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-slate-100"
                  />
                </div>
              </div>
              <div>
                <label className="text-xs text-slate-400 block mb-1">Citations</label>
                <input
                  type="number"
                  value={newPatent.citations}
                  onChange={(e) => handleNewPatentChange('citations', e.target.value)}
                  className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-slate-100"
                />
              </div>
              <div>
                <label className="text-xs text-slate-400 block mb-1">Abstract</label>
                <textarea
                  value={newPatent.abstract}
                  onChange={(e) => handleNewPatentChange('abstract', e.target.value)}
                  rows="4"
                  className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs text-slate-100"
                />
              </div>
              <button
                type="submit"
                className="w-full rounded-lg bg-purple-500 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-400"
              >
                Add Patent
              </button>
            </form>
          </div>

          <div className="p-5 rounded-2xl glass-panel space-y-4">
            <h3 style={{ color: theme.colors.text.primary }} className="text-sm font-bold">Portfolio Snapshot</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-xl bg-slate-900/80 p-3">
                <p className="text-xs text-slate-400">Total Patents</p>
                <p className="mt-2 text-2xl font-bold text-slate-100">{portfolioSummary.total}</p>
              </div>
              <div className="rounded-xl bg-slate-900/80 p-3">
                <p className="text-xs text-slate-400">Avg. Citations</p>
                <p className="mt-2 text-2xl font-bold text-slate-100">{portfolioSummary.averageCitations}</p>
              </div>
              <div className="rounded-xl bg-slate-900/80 p-3">
                <p className="text-xs text-slate-400">Top Assignee</p>
                <p className="mt-2 text-sm font-semibold text-slate-100">{portfolioSummary.topAssignee}</p>
              </div>
              <div className="rounded-xl bg-slate-900/80 p-3">
                <p className="text-xs text-slate-400">Top IPC</p>
                <p className="mt-2 text-sm font-semibold text-slate-100">{portfolioSummary.topIpc}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
