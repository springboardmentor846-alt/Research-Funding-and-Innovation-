import { useState } from "react";
import { ShieldCheck, Search, DollarSign, Building2 } from "lucide-react";
import Layout from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { checkEligibility } from "@/services/api";

const STATUS_STYLE = {
  Eligible:             { bar: "bg-emerald-500", badge: "bg-emerald-100 text-emerald-700 border-emerald-200" },
  "Partially Eligible": { bar: "bg-amber-500",   badge: "bg-amber-100 text-amber-700 border-amber-200" },
  "Not Eligible":       { bar: "bg-red-500",      badge: "bg-red-100 text-red-700 border-red-200" },
};

export default function GrantMatching() {
  const [fundingId, setFundingId] = useState("");
  const [result, setResult]       = useState(null);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState("");

  const handleCheck = async (e) => {
    e.preventDefault();
    if (!fundingId) return;
    setError("");
    setResult(null);
    setLoading(true);
    try {
      const res = await checkEligibility(fundingId);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to check eligibility. Ensure you have a profile.");
    } finally {
      setLoading(false);
    }
  };

  const style = result ? STATUS_STYLE[result.status] : null;

  return (
    <Layout>
      <div className="max-w-2xl mx-auto space-y-5">
        <div>
          <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            <ShieldCheck size={20} className="text-blue-600" /> Grant Eligibility Matching
          </h2>
          <p className="text-sm text-slate-500 mt-0.5">
            Enter a Funding ID to automatically check your eligibility
          </p>
        </div>

        {/* Input */}
        <Card>
          <CardContent className="p-6">
            <form onSubmit={handleCheck} className="space-y-4">
              <div>
                <Label>Funding Opportunity ID</Label>
                <div className="flex gap-2 mt-1.5">
                  <Input
                    type="number"
                    placeholder="e.g. 5"
                    value={fundingId}
                    onChange={(e) => setFundingId(e.target.value)}
                    className="flex-1"
                    min={1}
                  />
                  <Button type="submit" disabled={loading || !fundingId}>
                    <Search size={15} />
                    {loading ? "Checking…" : "Check Eligibility"}
                  </Button>
                </div>
                <p className="text-xs text-slate-400 mt-1.5">
                  You can find Funding IDs on the{" "}
                  <a href="/funding" className="text-blue-500 hover:underline">Funding page</a>.
                </p>
              </div>
            </form>

            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
                {error}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Result */}
        {result && style && (
          <Card className={`border ${style.badge}`}>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="text-base">{result.funding_title}</span>
                <span className={`text-sm font-bold px-3 py-1 rounded-full border ${style.badge}`}>
                  {result.status}
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              {/* Agency & Amount */}
              <div className="flex gap-6 text-sm">
                <div className="flex items-center gap-1.5 text-slate-600">
                  <Building2 size={14} className="text-slate-400" /> {result.agency}
                </div>
                <div className="flex items-center gap-1.5 text-emerald-600 font-semibold">
                  <DollarSign size={14} /> ${Number(result.funding_amount).toLocaleString()}
                </div>
              </div>

              {/* Match percentage bar */}
              <div>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="text-slate-600 font-medium">Overall Match</span>
                  <span className="font-bold text-slate-800">{result.match_percentage}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full transition-all ${style.bar}`}
                    style={{ width: `${result.match_percentage}%` }}
                  />
                </div>
              </div>

              {/* Criteria breakdown */}
              <div>
                <h4 className="text-sm font-semibold text-slate-700 mb-2">Criteria Breakdown</h4>
                <div className="space-y-2">
                  {result.criteria?.map((c, i) => (
                    <div
                      key={i}
                      className="flex items-start justify-between gap-3 p-3 rounded-lg bg-slate-50 border border-slate-100"
                    >
                      <div className="flex-1">
                        <p className="text-xs font-semibold text-slate-700">{c.criterion}</p>
                        <p className="text-xs text-slate-500 mt-0.5">
                          Your value: <span className="font-medium">{c.profile_value || "—"}</span>
                        </p>
                        <p className="text-xs text-slate-400">
                          Required: {c.required_value || "—"}
                        </p>
                      </div>
                      <span className={`shrink-0 text-xs font-bold px-2 py-0.5 rounded-full ${
                        c.matched ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-600"
                      }`}>
                        {c.matched ? "✓ Match" : "✗ No Match"}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </Layout>
  );
}
