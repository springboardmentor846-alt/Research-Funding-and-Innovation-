import { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import { DollarSign, Calendar, Globe, Building2, ArrowUpDown, Filter } from "lucide-react";
import Layout from "@/components/Layout";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import SearchBar from "@/components/SearchBar";
import Pagination from "@/components/Pagination";
import { CardGridSkeleton } from "@/components/LoadingSkeleton";
import { getFunding } from "@/services/api";

const SORT_OPTIONS = [
  { value: "latest",        label: "Latest" },
  { value: "highest_amount", label: "Highest Amount" },
  { value: "deadline",      label: "Deadline" },
];

const STATUS_COLOR = {
  Open:   "bg-emerald-100 text-emerald-700",
  Closed: "bg-red-100 text-red-700",
};

export default function FundingDashboard() {
  const [data, setData]         = useState([]);
  const [total, setTotal]       = useState(0);
  const [loading, setLoading]   = useState(true);
  const [page, setPage]         = useState(1);
  const LIMIT = 12;

  const [filters, setFilters] = useState({
    research_domain: "",
    country: "",
    agency: "",
    sort_by: "latest",
  });
  const [search, setSearch] = useState("");

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const params = {
        skip: (page - 1) * LIMIT,
        limit: LIMIT,
        sort_by: filters.sort_by,
        ...(filters.research_domain && { research_domain: filters.research_domain }),
        ...(filters.country && { country: filters.country }),
        ...(filters.agency && { agency: filters.agency }),
      };
      const res = await getFunding(params);
      setData(res.data.data);
      setTotal(res.data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [page, filters]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const filtered = search
    ? data.filter(
        (f) =>
          f.title.toLowerCase().includes(search.toLowerCase()) ||
          f.agency.toLowerCase().includes(search.toLowerCase())
      )
    : data;

  const totalPages = Math.ceil(total / LIMIT);

  return (
    <Layout>
      <div className="space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h2 className="text-xl font-bold text-slate-800">Funding Opportunities</h2>
            <p className="text-sm text-slate-500">{total} opportunities available</p>
          </div>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-wrap gap-3 items-end">
              <SearchBar
                value={search}
                onChange={setSearch}
                placeholder="Search title or agency…"
                className="w-64"
              />
              <div className="flex flex-wrap gap-2">
                {["research_domain", "country", "agency"].map((key) => (
                  <input
                    key={key}
                    className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                    placeholder={key.replace("_", " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                    value={filters[key]}
                    onChange={(e) => {
                      setFilters((f) => ({ ...f, [key]: e.target.value }));
                      setPage(1);
                    }}
                  />
                ))}
                <div className="flex items-center gap-1 border border-slate-200 rounded-lg px-2">
                  <ArrowUpDown size={14} className="text-slate-400" />
                  <select
                    className="text-sm py-1.5 bg-transparent focus:outline-none"
                    value={filters.sort_by}
                    onChange={(e) => { setFilters((f) => ({ ...f, sort_by: e.target.value })); setPage(1); }}
                  >
                    {SORT_OPTIONS.map((o) => (
                      <option key={o.value} value={o.value}>{o.label}</option>
                    ))}
                  </select>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => { setFilters({ research_domain: "", country: "", agency: "", sort_by: "latest" }); setSearch(""); setPage(1); }}
                >
                  <Filter size={13} /> Clear
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Grid */}
        {loading ? (
          <CardGridSkeleton count={12} />
        ) : filtered.length === 0 ? (
          <div className="text-center py-20 text-slate-400">No funding opportunities found.</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((f) => (
              <Card key={f.id} className="hover:shadow-md transition-shadow flex flex-col">
                <CardContent className="p-5 flex flex-col flex-1">
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <div className="flex items-center gap-2">
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${STATUS_COLOR[f.status] || "bg-slate-100 text-slate-600"}`}>
                        {f.status}
                      </span>
                      <span className="text-xs text-slate-400 font-mono">#{f.id}</span>
                    </div>
                    <span className="text-xs text-slate-400 shrink-0">{f.research_domain}</span>
                  </div>
                  <h3 className="font-semibold text-slate-800 text-sm leading-snug mb-2 line-clamp-2">
                    {f.title}
                  </h3>
                  <p className="text-xs text-slate-500 line-clamp-2 mb-3 flex-1">{f.description}</p>
                  <div className="space-y-1.5 text-xs text-slate-600">
                    <div className="flex items-center gap-1.5">
                      <Building2 size={12} className="text-slate-400" /> {f.agency}
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Globe size={12} className="text-slate-400" /> {f.country}
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Calendar size={12} className="text-slate-400" /> Deadline: {f.deadline}
                    </div>
                    <div className="flex items-center gap-1.5">
                      <DollarSign size={12} className="text-emerald-500" />
                      <span className="font-semibold text-emerald-600">
                        ${Number(f.funding_amount).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <Link
                    to={`/funding/${f.id}`}
                    className="mt-4 block text-center text-xs font-medium text-blue-600 border border-blue-200 rounded-lg py-1.5 hover:bg-blue-50 transition-colors"
                  >
                    View Details
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
      </div>
    </Layout>
  );
}
