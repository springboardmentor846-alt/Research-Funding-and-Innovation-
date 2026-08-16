import React, { useState, useEffect } from 'react';
import { Navbar } from '../components/common/Navbar';
import { Sidebar } from '../components/common/Sidebar';
import { Footer } from '../components/common/Footer';
import { reportAPI } from '../services/api';
import { Loader } from '../components/common/Loader';
import { FileText, Download, Plus, FileSpreadsheet } from 'lucide-react';

export const ReportsPage = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const [newReport, setNewReport] = useState({
    title: 'Executive Funding & IP Intelligence Report 2026',
    report_type: 'Funding',
    format: 'CSV'
  });

  const fetchReports = async () => {
    try {
      const res = await reportAPI.getAll();
      setReports(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleGenerate = async (e) => {
    e.preventDefault();
    setGenerating(true);
    try {
      await reportAPI.generate(newReport);
      fetchReports();
    } catch (e) {
      console.error(e);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />
      <div className="flex-1 flex">
        <Sidebar />
        <main className="flex-1 p-8 space-y-8 overflow-y-auto">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight gradient-text">
              Platform Report Generator & Exports
            </h1>
            <p className="text-sm text-slate-400 mt-1">Export verified analytical summaries across funding opportunities, patents, publications, and innovation scores.</p>
          </div>

          <form onSubmit={handleGenerate} className="glass-card p-6 flex flex-col md:flex-row items-center gap-4">
            <input
              type="text"
              required
              value={newReport.title}
              onChange={(e) => setNewReport({...newReport, title: e.target.value})}
              className="flex-1 p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm"
              placeholder="Report Title..."
            />
            <select
              value={newReport.report_type}
              onChange={(e) => setNewReport({...newReport, report_type: e.target.value})}
              className="p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200"
            >
              <option value="Funding">Funding Grants Report</option>
              <option value="Patent">Patent Landscape Report</option>
              <option value="Research">Research Intelligence Digest</option>
              <option value="Technology">Technology Radar Report</option>
              <option value="Innovation">Innovation Scores Summary</option>
            </select>

            <button type="submit" disabled={generating} className="px-6 py-2.5 rounded-xl font-bold text-white gradient-bg-accent shadow-md text-sm whitespace-nowrap">
              {generating ? 'Generating...' : 'Generate Report'}
            </button>
          </form>

          {loading ? (
            <Loader message="Loading platform reports..." />
          ) : (
            <div className="space-y-4">
              <h3 className="text-xl font-bold">Generated Analytical Artifacts</h3>
              <div className="space-y-3">
                {reports.map((r) => (
                  <div key={r.id} className="glass-card p-4 flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="p-3 bg-blue-500/20 text-blue-400 rounded-xl">
                        <FileSpreadsheet className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="font-bold text-slate-100">{r.title}</div>
                        <div className="text-xs text-slate-400">Type: {r.report_type} • Format: {r.format} • Generated {new Date(r.created_at).toLocaleDateString()}</div>
                      </div>
                    </div>

                    <a
                      href={`http://localhost:8000/api/v1/reports/download/${r.report_type.toLowerCase()}-report.csv`}
                      target="_blank"
                      rel="noreferrer"
                      className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold rounded-xl text-xs flex items-center space-x-2 border border-slate-700"
                    >
                      <Download className="w-4 h-4" />
                      <span>Download CSV</span>
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}
        </main>
      </div>
      <Footer />
    </div>
  );
};
