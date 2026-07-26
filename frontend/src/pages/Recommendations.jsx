import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Star, DollarSign, Calendar, TrendingUp, ShieldCheck } from "lucide-react";
import Layout from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CardGridSkeleton } from "@/components/LoadingSkeleton";
import { getRecommendations } from "@/services/api";
import { useAuth } from "@/context/AuthContext";

const ELIGIBILITY_BADGE = {
  Eligible:             "bg-emerald-100 text-emerald-700",
  "Partially Eligible": "bg-amber-100 text-amber-700",
  "Not Eligible":       "bg-red-100 text-red-700",
};

export default function Recommendations() {
  const { user } = useAuth();
  const [recs, setRecs]     = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState("");

  useEffect(() => {
    if (!user?.id) { setLoading(false); return; }
    getRecommendations(user.id)
      .then((r) => setRecs(r.data.recommendations))
      .catch((e) => setError(e.response?.data?.detail || "Failed to load recommendations."))
      .finally(() => setLoading(false));
  }, [user]);

  return (
    <Layout>
      <div className="space-y-5">
        <div>
          <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            <Star size={20} className="text-amber-500" /> AI Funding Recommendations
          </h2>
          <p className="text-sm text-slate-500 mt-0.5">
            Top 10 funding opportunities matched to your research profile
          </p>
        </div>

        {error && (
          <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-sm text-amber-700">
            {error} — Make sure you have a research profile set up.
          </div>
        )}

        {loading ? (
          <CardGridSkeleton count={6} />
        ) : recs.length === 0 ? (
          <div className="text-center py-20 text-slate-400">
            <Star size={40} className="mx-auto mb-3 opacity-30" />
            <p>No recommendations yet. Complete your research profile to get started.</p>
            <Link to="/profile" className="mt-3 inline-block text-blue-600 text-sm hover:underline">
              Set up profile →
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {recs.map((rec, idx) => (
              <Card key={rec.funding_id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-5">
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="flex items-center gap-2">
                      <span className="w-6 h-6 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center font-bold shrink-0">
                        {idx + 1}
                      </span>
                      <h3 className="font-semibold text-slate-800 text-sm leading-snug line-clamp-2">
                        {rec.title}
                      </h3>
                    </div>
                    <span className={`shrink-0 text-xs font-medium px-2 py-0.5 rounded-full ${ELIGIBILITY_BADGE[rec.eligibility_status]}`}>
                      {rec.eligibility_status}
                    </span>
                  </div>

                  {/* Match bar */}
                  <div className="mb-3">
                    <div className="flex justify-between text-xs text-slate-500 mb-1">
                      <span className="flex items-center gap-1"><TrendingUp size={11} /> Match Score</span>
                      <span className="font-bold text-blue-600">{rec.recommendation_percentage}%</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-1.5">
                      <div
                        className="h-1.5 rounded-full bg-blue-500 transition-all"
                        style={{ width: `${rec.recommendation_percentage}%` }}
                      />
                    </div>
                  </div>

                  <p className="text-xs text-slate-500 mb-3 line-clamp-2 italic">"{rec.reason}"</p>

                  <div className="flex items-center justify-between text-xs text-slate-600">
                    <div className="flex items-center gap-1">
                      <DollarSign size={12} className="text-emerald-500" />
                      <span className="font-semibold text-emerald-600">
                        ${Number(rec.funding_amount).toLocaleString()}
                      </span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Calendar size={12} className="text-slate-400" /> {rec.deadline}
                    </div>
                  </div>

                  <Link
                    to={`/funding/${rec.funding_id}`}
                    className="mt-3 block text-center text-xs font-medium text-blue-600 border border-blue-200 rounded-lg py-1.5 hover:bg-blue-50 transition-colors"
                  >
                    View Opportunity
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
