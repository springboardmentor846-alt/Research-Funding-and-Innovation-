import { useState, useEffect } from 'react'
import {
  FileText, Download, Printer, Sparkles, FileCheck,
  Coins, Lightbulb, Award, BookOpen, RefreshCw
} from 'lucide-react'
import { reportsNotificationsService } from '@/services/reportsNotificationsService'
import toast from 'react-hot-toast'

export default function ReportsPage() {
  const [reports, setReports] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isGenerating, setIsGenerating] = useState(false)

  const [reportType, setReportType] = useState('research_summary')
  const [reportTitle, setReportTitle] = useState('')
  const [reportFormat, setReportFormat] = useState('pdf')

  useEffect(() => {
    fetchUserReports()
  }, [])

  const fetchUserReports = async () => {
    try {
      setIsLoading(true)
      const data = await reportsNotificationsService.getUserReports()
      setReports(data)
    } catch (err) {
      toast.error('Failed to load user reports.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleGenerateReport = async (e) => {
    e.preventDefault()
    try {
      setIsGenerating(true)
      const res = await reportsNotificationsService.generateReport({
        report_type: reportType,
        title: reportTitle.trim() || undefined,
        format: reportFormat,
      })
      toast.success(`Report "${res.title}" generated successfully!`)
      fetchUserReports()
    } catch (err) {
      toast.error('Failed to generate report.')
      console.error(err)
    } finally {
      setIsGenerating(false)
    }
  }

  const handlePrintPdf = (report) => {
    const printWindow = window.open('', '_blank')
    printWindow.document.write(`
      <html>
        <head>
          <title>${report.title}</title>
          <style>
            body { font-family: sans-serif; padding: 40px; color: #111; line-height: 1.6; }
            h1 { color: #1e3a8a; border-bottom: 2px solid #3b82f6; padding-bottom: 10px; }
            .meta { color: #666; font-size: 14px; margin-bottom: 20px; }
            .box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-top: 20px; }
            pre { background: #0f172a; color: #38bdf8; padding: 15px; border-radius: 6px; overflow-x: auto; }
          </style>
        </head>
        <body>
          <h1>${report.title}</h1>
          <div class="meta">
            <p><strong>Report Type:</strong> ${report.report_type.toUpperCase()}</p>
            <p><strong>Generated On:</strong> ${new Date(report.created_at).toLocaleString()}</p>
          </div>
          <div class="box">
            <h3>Summary & Findings</h3>
            <p>${report.summary || 'No summary available.'}</p>
          </div>
          <h3>Report Dataset Payload</h3>
          <pre>${JSON.stringify(report.data_json, null, 2)}</pre>
          <script>window.onload = function() { window.print(); }</script>
        </body>
      </html>
    `)
    printWindow.document.close()
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* ── Header ── */}
      <div>
        <div className="flex items-center gap-2 text-amber-400 font-semibold text-xs tracking-wider uppercase mb-1">
          <FileText className="w-4 h-4" /> Export & Reports Generator
        </div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-white">Reports & Export Center</h1>
        <p className="text-surface-400 text-sm mt-1">
          Generate formatted PDF reports and export CSV spreadsheets for Research Summaries, Funding Grants, Patents, and Innovation Scores.
        </p>
      </div>

      {/* ── Quick CSV Direct Export Cards ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass p-5 rounded-2xl border border-white/10 flex items-center justify-between">
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Coins className="w-4 h-4 text-amber-400" /> Funding Opportunities CSV
            </h3>
            <p className="text-xs text-surface-400">Export 50+ grant opportunities</p>
          </div>
          <a
            href={reportsNotificationsService.exportCSVUrl('funding')}
            download
            className="btn-secondary text-xs py-2 px-3 flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5" /> CSV
          </a>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/10 flex items-center justify-between">
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-brand-400" /> Patent Database CSV
            </h3>
            <p className="text-xs text-surface-400">Export patent records & assignees</p>
          </div>
          <a
            href={reportsNotificationsService.exportCSVUrl('patent')}
            download
            className="btn-secondary text-xs py-2 px-3 flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5" /> CSV
          </a>
        </div>

        <div className="glass p-5 rounded-2xl border border-white/10 flex items-center justify-between">
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Award className="w-4 h-4 text-emerald-400" /> Technology Trends CSV
            </h3>
            <p className="text-xs text-surface-400">Export TRL levels & market growth</p>
          </div>
          <a
            href={reportsNotificationsService.exportCSVUrl('technology')}
            download
            className="btn-secondary text-xs py-2 px-3 flex items-center gap-1.5"
          >
            <Download className="w-3.5 h-3.5" /> CSV
          </a>
        </div>
      </div>

      {/* ── Generate Report Form ── */}
      <form onSubmit={handleGenerateReport} className="glass p-6 rounded-2xl border border-white/10 space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center gap-2 border-b border-white/5 pb-3">
          <Sparkles className="w-5 h-5 text-accent-400" /> Generate Customized Executive Report
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-surface-400 font-medium block mb-1">Report Module</label>
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
              className="w-full bg-surface-900 border border-white/10 rounded-xl px-3 py-2.5 text-xs text-white focus:border-brand-500 focus:outline-none"
            >
              <option value="research_summary">Research Summary Report</option>
              <option value="funding">Funding Intelligence Report</option>
              <option value="patent">Patent Portfolio Report</option>
              <option value="innovation_score">Technology Innovation Score Report</option>
            </select>
          </div>

          <div>
            <label className="text-xs text-surface-400 font-medium block mb-1">Custom Report Title (Optional)</label>
            <input
              type="text"
              value={reportTitle}
              onChange={(e) => setReportTitle(e.target.value)}
              placeholder="e.g. Q3 2025 AI Research & Patent Evaluation"
              className="w-full bg-surface-900 border border-white/10 rounded-xl px-3 py-2.5 text-xs text-white placeholder-surface-500 focus:border-brand-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="text-xs text-surface-400 font-medium block mb-1">Output Format</label>
            <select
              value={reportFormat}
              onChange={(e) => setReportFormat(e.target.value)}
              className="w-full bg-surface-900 border border-white/10 rounded-xl px-3 py-2.5 text-xs text-white focus:border-brand-500 focus:outline-none"
            >
              <option value="pdf">Printable PDF Document</option>
              <option value="csv">Structured CSV Dataset</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={isGenerating}
            className="btn-primary py-2.5 px-6 text-xs shadow-glow-brand flex items-center gap-2 disabled:opacity-50"
          >
            <FileCheck className="w-4 h-4" />
            {isGenerating ? 'Compiling Report...' : 'Generate Report'}
          </button>
        </div>
      </form>

      {/* ── Generated Reports History ── */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <FileText className="w-5 h-5 text-brand-400" /> Report History
        </h2>

        {isLoading ? (
          <div className="flex flex-col items-center justify-center min-h-[30vh] gap-3">
            <div className="w-10 h-10 rounded-full border-3 border-brand-500 border-t-transparent animate-spin" />
            <p className="text-surface-400 text-xs animate-pulse">Loading reports history...</p>
          </div>
        ) : reports.length === 0 ? (
          <div className="glass p-12 rounded-2xl border border-white/10 text-center space-y-3">
            <FileText className="w-12 h-12 text-surface-500 mx-auto" />
            <h3 className="text-lg font-bold text-white">No Reports Generated Yet</h3>
            <p className="text-surface-400 text-xs">Use the generator above to create your first report.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {reports.map((report) => (
              <div
                key={report.id}
                className="glass p-5 rounded-2xl border border-white/10 hover:border-brand-500/30 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-brand-300 px-2 py-0.5 rounded bg-brand-500/10 border border-brand-500/20">
                      {report.report_type.replace('_', ' ')}
                    </span>
                    <span className="text-xs text-surface-500 font-mono">
                      {new Date(report.created_at).toLocaleString()}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-white">{report.title}</h3>
                  <p className="text-xs text-surface-400 line-clamp-1">{report.summary}</p>
                </div>

                <div className="flex items-center gap-2 flex-shrink-0">
                  <button
                    onClick={() => handlePrintPdf(report)}
                    className="btn-primary text-xs py-2 px-3 flex items-center gap-1.5 shadow-glow-brand"
                  >
                    <Printer className="w-3.5 h-3.5" /> Print / Save PDF
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
