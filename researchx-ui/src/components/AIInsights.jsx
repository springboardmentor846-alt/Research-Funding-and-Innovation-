import { Sparkles, TrendingUp, Rocket } from "lucide-react";

export default function AIInsights() {
  return (
    <div className="mt-8 bg-gradient-to-r from-cyan-600 to-blue-700 rounded-2xl p-8 text-white shadow-xl">

      <div className="flex items-center gap-3 mb-6">
        <Sparkles size={34} />
        <h2 className="text-3xl font-bold">
          AI Research Assistant
        </h2>
      </div>

      <div className="grid md:grid-cols-3 gap-6">

        <div className="bg-white/10 rounded-xl p-5 backdrop-blur-md">
          <TrendingUp className="mb-3 text-green-300" size={32}/>
          <h3 className="text-xl font-semibold">
            Innovation Score
          </h3>

          <p className="text-4xl font-bold mt-3">
            92%
          </p>

          <p className="text-cyan-100 mt-2">
            High innovation potential
          </p>
        </div>

        <div className="bg-white/10 rounded-xl p-5 backdrop-blur-md">
          <Rocket className="mb-3 text-yellow-300" size={32}/>
          <h3 className="text-xl font-semibold">
            Startup Readiness
          </h3>

          <p className="text-4xl font-bold mt-3">
            Medium
          </p>

          <p className="text-cyan-100 mt-2">
            Industry collaboration recommended
          </p>
        </div>

        <div className="bg-white/10 rounded-xl p-5 backdrop-blur-md">
          <Sparkles className="mb-3 text-pink-300" size={32}/>
          <h3 className="text-xl font-semibold">
            AI Recommendation
          </h3>

          <p className="mt-3">
            Apply for AICTE Research Funding to increase commercialization success.
          </p>
        </div>

      </div>

    </div>
  );
}