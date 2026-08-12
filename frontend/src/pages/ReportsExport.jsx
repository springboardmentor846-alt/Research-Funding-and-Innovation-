import React, { useMemo, useState } from 'react';
import { FileSpreadsheet, Download, Printer, ExternalLink, Copy, Sparkles, RefreshCcw } from 'lucide-react';

const API_BASE_URL = (import.meta.env.VITE_API_URL ?? '').replace(/\/*$/, '');
const API_BASE_PATH = '/api/v1';

const normalizeApiPath = (path) => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return normalizedPath.startsWith(API_BASE_PATH) ? normalizedPath : `${API_BASE_PATH}${normalizedPath}`;
};

const makeApiUrl = (path) => {
  const apiPath = normalizeApiPath(path);
  if (!API_BASE_URL) {
    return apiPath;
  }

  const baseWithoutApi = API_BASE_URL.replace(new RegExp(`${API_BASE_PATH}$`), '');
  return `${baseWithoutApi}${apiPath}`;
};

const makeAbsoluteUrl = (path) => {
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  const url = makeApiUrl(path);
  return API_BASE_URL ? url : `${window.location.origin}${url}`;
};

const reportTemplates = [
  {
    id: 'funding-opportunities',
    apiType: 'funding',
    title: 'Funding Opportunity & Grant Discovery Report',
    description: 'Comprehensive export of active government grants, funding amounts, eligibility rules, and deadlines.',
    type: 'Funding Intelligence',
    lastUpdated: '2 days ago',
    tags: ['grants', 'eligibility', 'deadlines'],
    csvPath: '/reports/funding/export/csv',
    jsonPath: '/reports/funding/export/json',
    summaryPath: '/reports/html-summary?report_type=funding',
  },
  {
    id: 'patent-landscape',
    apiType: 'patent',
    title: 'Patent Landscape & IP Analytics Report',
    description: 'Complete breakdown of harvested patents, IPC classifications, assignee distributions, and cluster maps.',
    type: 'IP Analytics',
    lastUpdated: '5 days ago',
    tags: ['patent', 'assignees', 'classification'],
    csvPath: '/reports/patents/export/csv',
    jsonPath: '/reports/patents/export/json',
    summaryPath: '/reports/html-summary?report_type=patent',
  },
];

export const ReportsExport = () => {
  const reports = useMemo(
    () =>
      reportTemplates.map((report) => ({
        ...report,
        csvUrl: makeApiUrl(report.csvPath),
        jsonUrl: makeApiUrl(report.jsonPath),
        summaryUrl: makeApiUrl(report.summaryPath),
      })),
    []
  );

  const [searchQuery, setSearchQuery] = useState('');
  const [reportStatuses, setReportStatuses] = useState(() =>
    Object.fromEntries(reports.map((report) => [report.id, 'Ready']))
  );
  const [copiedUrl, setCopiedUrl] = useState('');
  const [generateStatus, setGenerateStatus] = useState({});
  const [generateMessages, setGenerateMessages] = useState({});
  const [generatedPreviewUrls, setGeneratedPreviewUrls] = useState({});

  const filteredReports = useMemo(
    () =>
      reports.filter((report) => {
        const query = searchQuery.toLowerCase();
        return (
          report.title.toLowerCase().includes(query) ||
          report.description.toLowerCase().includes(query) ||
          report.type.toLowerCase().includes(query) ||
          report.tags.some((tag) => tag.toLowerCase().includes(query))
        );
      }),
    [reports, searchQuery]
  );

  const handleOpenUrl = (url) => {
    window.open(makeAbsoluteUrl(url), '_blank', 'noopener,noreferrer');
  };

  const downloadFile = async (url, filename, accept) => {
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          Accept: accept,
        },
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(`Download failed: ${response.status} ${response.statusText} ${text}`);
      }

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = downloadUrl;
      anchor.download = filename;
      document.body.appendChild(anchor);
      anchor.click();
      document.body.removeChild(anchor);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error(error);
      alert('Unable to download the report. Please try again.');
    }
  };

  const handleCopyLink = async (url) => {
    try {
      const fullUrl = makeAbsoluteUrl(url);
      await navigator.clipboard.writeText(fullUrl);
      setCopiedUrl(fullUrl);
      setTimeout(() => setCopiedUrl(''), 1800);
    } catch (error) {
      console.error('Copy failed', error);
      alert('Unable to copy the summary link. Please try again.');
    }
  };

  const handleRefreshStatus = (id) => {
    setReportStatuses((prev) => ({ ...prev, [id]: 'Refreshing...' }));
    setTimeout(() => {
      setReportStatuses((prev) => ({ ...prev, [id]: 'Ready' }));
    }, 900);
  };

  const handleGenerateReport = async (report) => {
    setGenerateStatus((prev) => ({ ...prev, [report.id]: true }));
    setGenerateMessages((prev) => ({ ...prev, [report.id]: `Generating ${report.type} summary...` }));

    try {
      const response = await fetch(makeApiUrl(`/reports/generate?report_type=${report.apiType}`), {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || `Server error: ${response.status}`);
      }
      if (data.status !== 'generated') {
        throw new Error(data.message || 'Report generation did not complete successfully.');
      }

      setGeneratedPreviewUrls((prev) => ({ ...prev, [report.id]: makeAbsoluteUrl(data.previewUrl ?? report.summaryPath) }));
      setGenerateMessages((prev) => ({ ...prev, [report.id]: data.message || 'Report generated successfully.' }));
      setReportStatuses((prev) => ({ ...prev, [report.id]: 'Ready' }));
    } catch (error) {
      console.error(error);
      setGenerateMessages((prev) => ({ ...prev, [report.id]: `Unable to generate report. ${error?.message || ''}` }));
    } finally {
      setGenerateStatus((prev) => ({ ...prev, [report.id]: false }));
    }
  };

  const readyCount = Object.values(reportStatuses).filter((status) => status === 'Ready').length;

  return (
    <div className="space-y-6">
      <div className="space-y-3">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h2 className="text-2xl font-extrabold text-slate-100 tracking-tight flex items-center space-x-2">
              <FileSpreadsheet className="w-6 h-6 text-emerald-400" />
              <span>Reports & Intelligence Export Hub</span>
            </h2>
            <p className="text-sm text-slate-400 mt-1 max-w-2xl">
              Generate and manage intelligence briefs, export structured data, and preview summary reports on demand.
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-3 w-full sm:w-auto">
            <div className="rounded-2xl glass-panel border border-slate-800 p-4">
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500 font-semibold">Reports available</p>
              <p className="text-2xl font-bold text-slate-100 mt-2">{reports.length}</p>
            </div>
            <div className="rounded-2xl glass-panel border border-slate-800 p-4">
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500 font-semibold">Ready now</p>
              <p className="text-2xl font-bold text-slate-100 mt-2">{readyCount}</p>
            </div>
            <div className="rounded-2xl glass-panel border border-slate-800 p-4">
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500 font-semibold">Search reports</p>
              <p className="text-sm text-slate-400 mt-2">Use keywords, types, and tags.</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-[2fr,1fr] gap-4">
          <div className="rounded-2xl glass-panel border border-slate-800 p-4">
            <label className="block text-xs uppercase tracking-[0.24em] text-slate-500 font-semibold mb-2" htmlFor="report-search">
              Filter reports
            </label>
            <input
              id="report-search"
              type="search"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="Search by title, type, or tag"
              className="w-full rounded-xl border border-slate-700 bg-slate-950/80 px-4 py-3 text-sm text-slate-100 outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
            />
          </div>
          <div className="rounded-2xl glass-panel border border-slate-800 p-4 flex items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500 font-semibold">Latest export</p>
              <p className="text-sm text-slate-300 mt-2">{reports[0]?.lastUpdated}</p>
            </div>
            <button
              type="button"
              onClick={() => setSearchQuery('')}
              className="rounded-xl border border-cyan-500 bg-cyan-500/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-cyan-300 hover:bg-cyan-500/20 transition"
            >
              Clear filter
            </button>
          </div>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {filteredReports.map((report) => (
          <div key={report.id} className="rounded-3xl glass-panel glass-panel-hover border border-slate-800 p-6 space-y-5">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div className="space-y-2">
                <span className="inline-flex rounded-full bg-emerald-400/10 px-3 py-1 text-[10px] uppercase tracking-[0.3em] font-bold text-emerald-300">
                  {report.type}
                </span>
                <h3 className="text-xl font-semibold text-slate-100">{report.title}</h3>
                <p className="text-sm text-slate-400">{report.description}</p>
              </div>
              <div className="text-right text-xs text-slate-500">
                <p>Last Updated</p>
                <p className="text-slate-300 mt-1 font-semibold">{report.lastUpdated}</p>
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              {report.tags.map((tag) => (
                <span key={tag} className="rounded-full bg-slate-900/80 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-300">
                  {tag}
                </span>
              ))}
            </div>

            <div className="rounded-3xl border border-slate-800 bg-slate-950/80 p-4 text-sm text-slate-300">
              <div className="flex items-center justify-between gap-3">
                <span>Status</span>
                <span className="font-bold text-slate-100">{reportStatuses[report.id] ?? 'Ready'}</span>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              <button
                type="button"
                onClick={() => downloadFile(report.csvUrl, `${report.id}.csv`, 'text/csv')}
                className="inline-flex items-center justify-center gap-2 rounded-2xl bg-emerald-500 px-4 py-3 text-xs font-semibold uppercase tracking-[0.15em] text-slate-950 transition hover:bg-emerald-400"
              >
                <Download className="w-4 h-4" />
                Export CSV / Excel
              </button>
              <button
                type="button"
                onClick={() => handleOpenUrl(report.summaryUrl)}
                className="inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-xs font-semibold uppercase tracking-[0.15em] text-slate-100 transition hover:border-cyan-400 hover:text-cyan-300"
              >
                <Printer className="w-4 h-4" />
                Open Summary
              </button>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              <button
                type="button"
                onClick={() => handleCopyLink(report.summaryUrl)}
                className="inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-xs font-semibold uppercase tracking-[0.15em] text-slate-100 transition hover:border-emerald-400 hover:text-emerald-300"
              >
                <Copy className="w-4 h-4" />
                {copiedUrl === makeAbsoluteUrl(report.summaryUrl) ? 'Copied!' : 'Copy Summary Link'}
              </button>
              <button
                type="button"
                onClick={() => handleRefreshStatus(report.id)}
                className="inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-xs font-semibold uppercase tracking-[0.15em] text-slate-100 transition hover:border-cyan-400 hover:text-cyan-300"
              >
                <RefreshCcw className="w-4 h-4" />
                Refresh Status
              </button>
              <button
                type="button"
                onClick={() => downloadFile(report.jsonUrl, `${report.id}.json`, 'application/json')}
                className="inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-xs font-semibold uppercase tracking-[0.15em] text-slate-100 transition hover:border-slate-500 hover:text-cyan-300"
              >
                <Sparkles className="w-4 h-4" />
                Export JSON
              </button>
            </div>
            {generatedPreviewUrls[report.id] && (
              <div className="rounded-2xl border border-emerald-500 bg-slate-950/80 p-3 text-sm text-emerald-200">
                Preview ready: <a href={generatedPreviewUrls[report.id]} target="_blank" rel="noopener noreferrer" className="text-cyan-300 underline">Open report</a>
              </div>
            )}
            {generateMessages[report.id] && (
              <div className="rounded-2xl border border-cyan-500 bg-slate-950/80 p-3 text-sm text-cyan-200">
                {generateMessages[report.id]}
              </div>
            )}
          </div>
        ))}
      </div>

      {filteredReports.length === 0 && (
        <div className="rounded-3xl glass-panel border border-slate-800 p-8 text-center text-slate-400">
          <Sparkles className="mx-auto mb-3 h-10 w-10 text-emerald-400" />
          <p className="text-sm">No reports match your search. Try a different keyword or clear the filter.</p>
        </div>
      )}
    </div>
  );
};
