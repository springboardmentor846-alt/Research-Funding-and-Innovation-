import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BookOpen, DollarSign, Star, Layers, ArrowRight, TrendingUp } from "lucide-react";
import Layout from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartSkeleton, CardGridSkeleton } from "@/components/LoadingSkeleton";
import DomainBarChart from "@/components/charts/DomainBarChart";
import PublicationLineChart from "@/components/charts/PublicationLineChart";
import AgencyPieChart from "@/components/charts/AgencyPieChart";
import FundingAreaChart from "@/components/charts/FundingAreaChart";
import { getDashboardStats } from "@/services/api";

const StatCard = ({ icon: Icon, label, value, color, to }) => (
  <Link to={to}>
    <Card className="hover:shadow-md transition-shadow cursor-pointer">
      <CardContent className="p-5 flex items-center gap-4">
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
          <Icon size={22} className="text-white" />
        </div>
        <div>
          <p className="text-2xl font-bold text-slate-800">{value ?? "—"}</p>
          <p className="text-sm text-slate-500">{label}</p>
        </div>
      </CardContent>
    </Card>
  </Link>
);

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboardStats()
      .then((r) => setStats(r.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const s = stats?.stats;

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-bold text-slate-800">Research Intelligence Dashboard</h2>
          <p className="text-sm text-slate-500 mt-0.5">Overview of your research ecosystem</p>
        </div>

        {/* Stat Cards */}
        {loading ? (
          <CardGridSkeleton count={4} />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard icon={BookOpen}   label="Total Publications"       value={s?.total_publications}        color="bg-blue-500"   to="/publications" />
            <StatCard icon={DollarSign} label="Funding Opportunities"    value={s?.total_funding_opportunities} color="bg-emerald-500" to="/funding" />
            <StatCard icon={Star}       label="Open Grants"              value={s?.open_funding}              color="bg-amber-500"  to="/funding" />
            <StatCard icon={Layers}     label="Research Domains"         value={s?.research_domains}          color="bg-violet-500" to="/publications" />
          </div>
        )}

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <Card>
            <CardHeader><CardTitle>Publications by Domain</CardTitle></CardHeader>
            <CardContent>
              {loading ? <ChartSkeleton /> : <DomainBarChart data={stats?.top_domains} />}
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Publication Trend by Year</CardTitle></CardHeader>
            <CardContent>
              {loading ? <ChartSkeleton /> : <PublicationLineChart data={stats?.publication_growth} />}
            </CardContent>
          </Card>
        </div>

        {/* Charts Row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <Card>
            <CardHeader><CardTitle>Funding by Agency</CardTitle></CardHeader>
            <CardContent>
              {loading ? <ChartSkeleton /> : <AgencyPieChart data={stats?.funding_by_agency} />}
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Funding Amount Trend</CardTitle></CardHeader>
            <CardContent>
              {loading ? <ChartSkeleton /> : <FundingAreaChart data={stats?.funding_amount_trend} />}
            </CardContent>
          </Card>
        </div>

        {/* Recent Opportunities */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <TrendingUp size={16} /> Recent Funding Opportunities
            </CardTitle>
            <Link to="/funding" className="text-sm text-blue-600 flex items-center gap-1 hover:underline">
              View all <ArrowRight size={14} />
            </Link>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-3">
                {[1,2,3].map(i => <div key={i} className="h-12 bg-slate-100 rounded-lg animate-pulse" />)}
              </div>
            ) : (
              <div className="space-y-2">
                {stats?.recent_opportunities?.map((f) => (
                  <Link
                    key={f.id}
                    to={`/funding/${f.id}`}
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-50 border border-transparent hover:border-slate-200 transition-all"
                  >
                    <div>
                      <p className="text-sm font-medium text-slate-800">{f.title}</p>
                      <p className="text-xs text-slate-500">{f.agency} · {f.research_domain}</p>
                    </div>
                    <div className="text-right shrink-0 ml-4">
                      <p className="text-sm font-semibold text-emerald-600">
                        ${Number(f.funding_amount).toLocaleString()}
                      </p>
                      <p className="text-xs text-slate-400">Due {f.deadline}</p>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}
