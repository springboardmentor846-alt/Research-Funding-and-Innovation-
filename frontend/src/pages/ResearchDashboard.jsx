import { useEffect, useState } from "react";
import { BarChart2, BookOpen, TrendingUp, Award, Hash } from "lucide-react";
import Layout from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartSkeleton } from "@/components/LoadingSkeleton";
import DomainBarChart from "@/components/charts/DomainBarChart";
import PublicationLineChart from "@/components/charts/PublicationLineChart";
import {
  getPublicationTrends,
  getDomainAnalysis,
  getTopKeywords,
  getYearAnalysis,
} from "@/services/api";

const StatCard = ({ icon: Icon, label, value, sub, color }) => (
  <Card>
    <CardContent className="p-5">
      <div className="flex items-center gap-4">
        <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${color}`}>
          <Icon size={20} className="text-white" />
        </div>
        <div>
          <p className="text-xl font-bold text-slate-800">{value ?? "—"}</p>
          <p className="text-xs text-slate-500">{label}</p>
          {sub && <p className="text-xs text-slate-400">{sub}</p>}
        </div>
      </div>
    </CardContent>
  </Card>
);

export default function ResearchDashboard() {
  const [trends, setTrends]     = useState([]);
  const [domains, setDomains]   = useState([]);
  const [keywords, setKeywords] = useState([]);
  const [yearData, setYearData] = useState([]);
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    Promise.all([
      getPublicationTrends(),
      getDomainAnalysis(),
      getTopKeywords(),
      getYearAnalysis(),
    ])
      .then(([t, d, k, y]) => {
        setTrends(t.data);
        setDomains(d.data);
        setKeywords(k.data);
        setYearData(y.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const totalPubs      = trends.reduce((s, t) => s + t.count, 0);
  const totalCitations = yearData.reduce((s, y) => s + y.total_citations, 0);
  const topDomain      = domains[0]?.domain ?? "—";
  const totalDomains   = domains.length;

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            <BarChart2 size={20} className="text-violet-600" /> Research Intelligence
          </h2>
          <p className="text-sm text-slate-500 mt-0.5">Deep analytics across publications and research domains</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard icon={BookOpen}   label="Total Publications"  value={totalPubs}      color="bg-blue-500" />
          <StatCard icon={Award}      label="Total Citations"     value={totalCitations} color="bg-emerald-500" />
          <StatCard icon={BarChart2}  label="Research Domains"    value={totalDomains}   color="bg-violet-500" />
          <StatCard icon={TrendingUp} label="Top Domain"          value={topDomain}      color="bg-amber-500" />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <Card>
            <CardHeader><CardTitle>Publication Growth by Year</CardTitle></CardHeader>
            <CardContent>
              {loading ? <ChartSkeleton /> : <PublicationLineChart data={trends} />}
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Publications by Domain</CardTitle></CardHeader>
            <CardContent>
              {loading ? <ChartSkeleton /> : <DomainBarChart data={domains} />}
            </CardContent>
          </Card>
        </div>

        {/* Citations per Domain */}
        <Card>
          <CardHeader><CardTitle>Citations per Domain</CardTitle></CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-2">
                {[1,2,3,4,5].map(i => <div key={i} className="h-8 bg-slate-100 rounded animate-pulse" />)}
              </div>
            ) : (
              <div className="space-y-3">
                {domains.map((d, i) => {
                  const max = Math.max(...domains.map(x => x.avg_citations), 1);
                  return (
                    <div key={d.domain} className="flex items-center gap-3">
                      <span className="text-xs text-slate-400 w-4">{i + 1}</span>
                      <span className="text-sm text-slate-700 w-44 truncate">{d.domain}</span>
                      <div className="flex-1 bg-slate-100 rounded-full h-2">
                        <div
                          className="h-2 rounded-full bg-violet-500"
                          style={{ width: `${(d.avg_citations / max) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs font-semibold text-slate-600 w-16 text-right">
                        {d.avg_citations} avg
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Year-wise breakdown */}
        <Card>
          <CardHeader><CardTitle>Year-wise Breakdown</CardTitle></CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-2">
                {[1,2,3].map(i => <div key={i} className="h-10 bg-slate-100 rounded animate-pulse" />)}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-100 text-left text-xs text-slate-500 uppercase tracking-wide">
                      <th className="pb-3 pr-4 font-medium">Year</th>
                      <th className="pb-3 pr-4 font-medium">Publications</th>
                      <th className="pb-3 pr-4 font-medium">Total Citations</th>
                      <th className="pb-3 font-medium">Top Keywords</th>
                    </tr>
                  </thead>
                  <tbody>
                    {yearData.map((y) => (
                      <tr key={y.year} className="border-b border-slate-50 hover:bg-slate-50 transition-colors">
                        <td className="py-3 pr-4 font-semibold text-slate-800">{y.year}</td>
                        <td className="py-3 pr-4 text-slate-600">{y.count}</td>
                        <td className="py-3 pr-4 text-slate-600">{y.total_citations}</td>
                        <td className="py-3">
                          <div className="flex flex-wrap gap-1">
                            {y.top_keywords.slice(0, 3).map((kw) => (
                              <span key={kw} className="px-2 py-0.5 bg-violet-50 text-violet-700 rounded-full text-xs">
                                {kw}
                              </span>
                            ))}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Top Keywords */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Hash size={16} /> Top Research Keywords</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex flex-wrap gap-2">
                {Array.from({ length: 15 }).map((_, i) => (
                  <div key={i} className="h-6 w-20 bg-slate-200 rounded-full animate-pulse" />
                ))}
              </div>
            ) : (
              <div className="flex flex-wrap gap-2">
                {keywords.map((k) => (
                  <span
                    key={k.keyword}
                    className="px-3 py-1 bg-violet-50 text-violet-700 rounded-full text-xs font-medium border border-violet-100"
                  >
                    {k.keyword}
                    <span className="ml-1.5 text-violet-400">({k.count})</span>
                  </span>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}
