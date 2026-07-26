import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import {
  ArrowLeft, Building2, Globe, Calendar, DollarSign,
  ExternalLink, ShieldCheck, Tag,
} from "lucide-react";
import Layout from "@/components/Layout";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/LoadingSkeleton";
import { getFundingById, checkEligibility } from "@/services/api";

const InfoRow = ({ icon: Icon, label, value, valueClass = "" }) => (
  <div className="flex items-start gap-3 py-3 border-b border-slate-100 last:border-0">
    <Icon size={16} className="text-slate-400 mt-0.5 shrink-0" />
    <div>
      <p className="text-xs text-slate-400">{label}</p>
      <p className={`text-sm font-medium text-slate-800 ${valueClass}`}>{value}</p>
    </div>
  </div>
);

const ELIGIBILITY_COLOR = {
  Eligible:           "bg-emerald-100 text-emerald-700 border-emerald-200",
  "Partially Eligible": "bg-amber-100 text-amber-700 border-amber-200",
  "Not Eligible":     "bg-red-100 text-red-700 border-red-200",
};

export default function FundingDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [funding, setFunding]         = useState(null);
  const [eligibility, setEligibility] = useState(null);
  const [loading, setLoading]         = useState(true);
  const [checkingElig, setCheckingElig] = useState(false);

  useEffect(() => {
    getFundingById(id)
      .then((r) => setFunding(r.data))
      .catch(() => navigate("/funding"))
      .finally(() => setLoading(false));
  }, [id, navigate]);

  const handleCheckEligibility = async () => {
    setCheckingElig(true);
    try {
      const res = await checkEligibility(id);
      setEligibility(res.data);
    } catch (err) {
      alert(err.response?.data?.detail || "Create a profile first to check eligibility.");
    } finally {
      setCheckingElig(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-5">
        <Link to="/funding" className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800">
          <ArrowLeft size={15} /> Back to Funding
        </Link>

        {loading ? (
          <div className="space-y-3">
            <Skeleton className="h-8 w-2/3" />
            <Skeleton className="h-4 w-1/3" />
            <Skeleton className="h-40 w-full" />
          </div>
        ) : funding ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {/* Main */}
            <div className="lg:col-span-2 space-y-5">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between gap-3 mb-4">
                    <h1 className="text-xl font-bold text-slate-800 leading-snug">{funding.title}</h1>
                    <span className={`shrink-0 text-xs font-medium px-2.5 py-1 rounded-full ${
                      funding.status === "Open" ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"
                    }`}>
                      {funding.status}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 leading-relaxed">{funding.description}</p>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <h3 className="font-semibold text-slate-700 mb-3 flex items-center gap-2">
                    <ShieldCheck size={16} /> Eligibility Criteria
                  </h3>
                  <p className="text-sm text-slate-600 leading-relaxed">{funding.eligibility}</p>
                </CardContent>
              </Card>

              {/* Eligibility Result */}
              {eligibility && (
                <Card className={`border ${ELIGIBILITY_COLOR[eligibility.status]}`}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold">Eligibility Result</h3>
                      <span className={`text-sm font-bold px-3 py-1 rounded-full border ${ELIGIBILITY_COLOR[eligibility.status]}`}>
                        {eligibility.status}
                      </span>
                    </div>
                    <div className="mb-4">
                      <div className="flex justify-between text-sm mb-1">
                        <span>Match Score</span>
                        <span className="font-bold">{eligibility.match_percentage}%</span>
                      </div>
                      <div className="w-full bg-slate-200 rounded-full h-2">
                        <div
                          className="h-2 rounded-full bg-blue-500 transition-all"
                          style={{ width: `${eligibility.match_percentage}%` }}
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      {eligibility.criteria?.map((c, i) => (
                        <div key={i} className="flex items-center justify-between text-xs py-1.5 border-b border-slate-100 last:border-0">
                          <span className="text-slate-600">{c.criterion}</span>
                          <span className={c.matched ? "text-emerald-600 font-medium" : "text-red-500 font-medium"}>
                            {c.matched ? "✓ Match" : "✗ No Match"}
                          </span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Sidebar */}
            <div className="space-y-4">
              <Card>
                <CardContent className="p-5">
                  <InfoRow icon={Building2}  label="Agency"          value={funding.agency} />
                  <InfoRow icon={Globe}      label="Country"         value={funding.country} />
                  <InfoRow icon={Tag}        label="Research Domain" value={funding.research_domain} />
                  <InfoRow icon={Calendar}   label="Deadline"        value={funding.deadline} />
                  <InfoRow
                    icon={DollarSign}
                    label="Funding Amount"
                    value={`$${Number(funding.funding_amount).toLocaleString()}`}
                    valueClass="text-emerald-600"
                  />
                </CardContent>
              </Card>

              <div className="space-y-2">
                <Button
                  className="w-full"
                  onClick={handleCheckEligibility}
                  disabled={checkingElig}
                >
                  <ShieldCheck size={15} />
                  {checkingElig ? "Checking…" : "Check My Eligibility"}
                </Button>
                {funding.application_link && (
                  <a href={funding.application_link} target="_blank" rel="noreferrer">
                    <Button variant="outline" className="w-full">
                      <ExternalLink size={15} /> Apply Now
                    </Button>
                  </a>
                )}
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </Layout>
  );
}
