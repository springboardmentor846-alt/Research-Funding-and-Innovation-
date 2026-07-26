import { useEffect, useState } from "react";
import { BookOpen, Hash } from "lucide-react";
import Layout from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartSkeleton, CardGridSkeleton } from "@/components/LoadingSkeleton";
import Pagination from "@/components/Pagination";
import SearchBar from "@/components/SearchBar";
import DomainBarChart from "@/components/charts/DomainBarChart";
import PublicationLineChart from "@/components/charts/PublicationLineChart";
import {
  getPublications, getPublicationTrends,
  getDomainAnalysis, getTopKeywords,
} from "@/services/api";

export default function PublicationAnalytics() {
  const [pubs, setPubs]         = useState([]);
  const [total, setTotal]       = useState(0);
  const [trends, setTrends]     = useState([]);
  const [domains, setDomains]   = useState([]);
  const [keywords, setKeywords] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [chartsLoading, setChartsLoading] = useState(true);
  const [page, setPage]         = useState(1);
  const [search, setSearch]     = useState("");
  const LIMIT = 10;

  useEffect(() => {
    Promise.all([getPublicationTrends(), getDomainAnalysis(), getTopKeywords()])
      .then(([t, d, k]) => {
        setTrends(t.data);
        setDomains(d.data);
        setKeywords(k.data);
      })
      .catch(console.error)
      .finally(() => setChartsLoading(false));
  }, []);

  useEffect(() => {
    setLoading(true);
    getPublications({ skip: (page - 1) * LIMIT, limit: LIMIT })
      .then((r) => { setPubs(r.data.data); setTotal(r.data.total); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [page]);

  const filtered = search
    ? pubs.filter(
        (p) =>
          p.title.toLowerCase().includes(search.toLowerCase()) ||
          p.authors.toLowerCase().includes(search.toLowerCase())
      )
    : pubs;

  const totalPages = Math.ceil(total / LIMIT);

  return (
    <Layout>
      <div className="space-y-5">
        <div>
          <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            <BookOpen size={20} className="text-blue-600" /> Publication Analytics
          </h2>
          <p className="text-sm text-slate-500 mt-0.5">{total} publications indexed</p>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <Card>
            <CardHeader><CardTitle>Publication Trend by Year</CardTitle></CardHeader>
            <CardContent>
              {chartsLoading ? <ChartSkeleton /> : <PublicationLineChart data={trends} />}
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle>Publications by Domain</CardTitle></CardHeader>
            <CardContent>
              {chartsLoading ? <ChartSkeleton /> : <DomainBarChart data={domains} />}
            </CardContent>
          </Card>
        </div>

        {/* Top Keywords */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Hash size={16} /> Top Keywords</CardTitle>
          </CardHeader>
          <CardContent>
            {chartsLoading ? (
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
                    className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-medium border border-blue-100"
                  >
                    {k.keyword}
                    <span className="ml-1.5 text-blue-400">({k.count})</span>
                  </span>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Publications Table */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between gap-3 flex-wrap">
            <CardTitle>All Publications</CardTitle>
            <SearchBar
              value={search}
              onChange={setSearch}
              placeholder="Search title or author…"
              className="w-64"
            />
          </CardHeader>
          <CardContent>
            {loading ? (
              <CardGridSkeleton count={4} />
            ) : filtered.length === 0 ? (
              <p className="text-center py-10 text-slate-400">No publications found.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-100 text-left text-xs text-slate-500 uppercase tracking-wide">
                      <th className="pb-3 pr-4 font-medium">Title</th>
                      <th className="pb-3 pr-4 font-medium">Authors</th>
                      <th className="pb-3 pr-4 font-medium">Domain</th>
                      <th className="pb-3 pr-4 font-medium">Year</th>
                      <th className="pb-3 font-medium">Citations</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtered.map((p) => (
                      <tr key={p.id} className="border-b border-slate-50 hover:bg-slate-50 transition-colors">
                        <td className="py-3 pr-4 font-medium text-slate-800 max-w-xs">
                          <p className="line-clamp-2">{p.title}</p>
                        </td>
                        <td className="py-3 pr-4 text-slate-500 text-xs max-w-[140px] truncate">{p.authors}</td>
                        <td className="py-3 pr-4">
                          <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded-full text-xs">
                            {p.research_domain}
                          </span>
                        </td>
                        <td className="py-3 pr-4 text-slate-600">{p.year}</td>
                        <td className="py-3 text-slate-600 font-medium">{p.citation_count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}
