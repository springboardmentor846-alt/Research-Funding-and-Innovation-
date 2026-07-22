import { useEffect, useState } from "react";
import axios from "axios";
import {
  Brain,
  Target,
  TrendingUp,
  Building2,
  ShieldAlert,
  BadgeDollarSign,
} from "lucide-react";

export default function AIRecommendation() {
  const [data, setData] = useState(null);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/commercialization/recommendation")
      .then((res) => {
        setData(res.data);
      })
      .catch((err) => console.error(err));
  }, []);

  if (!data) {
    return (
      <div className="mt-8 bg-slate-900 border border-slate-700 rounded-2xl p-8 text-center text-slate-400">
        Loading AI Recommendation...
      </div>
    );
  }

  return (
    <div className="mt-8 bg-slate-900 border border-slate-700 rounded-2xl shadow-xl p-6">

      <div className="flex items-center gap-3 mb-8">
        <Brain className="text-cyan-400 w-8 h-8" />

        <div>
          <h2 className="text-2xl font-bold text-white">
            AI Research Summary
          </h2>

          <p className="text-slate-400">
            Intelligent commercialization insights
          </p>
        </div>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">

        <Card
          icon={<TrendingUp className="text-cyan-400" />}
          title="Innovation Score"
          value={data.innovation_score}
        />

        <Card
          icon={<Target className="text-green-400" />}
          title="Commercialization"
          value={data.commercialization_readiness}
        />

        <Card
          icon={<Building2 className="text-yellow-400" />}
          title="Target Industry"
          value={data.target_industry}
        />

        <Card
          icon={<BadgeDollarSign className="text-pink-400" />}
          title="Recommended Funding"
          value={data.recommended_funding}
        />

        <Card
          icon={<ShieldAlert className="text-red-400" />}
          title="Risk Level"
          value={data.risk_level}
        />

        <Card
          icon={<Brain className="text-purple-400" />}
          title="Startup Potential"
          value={data.startup_potential}
        />

      </div>
    </div>
  );
}

function Card({ icon, title, value }) {
  return (
    <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 hover:border-cyan-500 transition">

      <div className="mb-4">
        {icon}
      </div>

      <p className="text-slate-400 text-sm">
        {title}
      </p>

      <h3 className="text-white text-xl font-bold mt-2">
        {value}
      </h3>

    </div>
  );
}