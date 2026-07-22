import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import TechnologyChart from "../components/TechnologyChart";
import PatentChart from "../components/PatentChart";
import {
  BarChart3,
  TrendingUp,
  Activity,
  FileText,
} from "lucide-react";

export default function Analytics() {
  return (
    <div className="flex bg-slate-950 min-h-screen">

      <Sidebar />

      <main className="flex-1 p-8 overflow-auto">

        <Header
          title="Analytics"
          subtitle="Research performance and innovation analytics."
        />

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">

          <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 hover:border-green-400 transition">

            <TrendingUp className="text-green-400 w-8 h-8 mb-3" />

            <h2 className="text-3xl font-bold text-white">
              24%
            </h2>

            <p className="text-slate-400">
              Research Growth
            </p>

          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 hover:border-cyan-400 transition">

            <Activity className="text-cyan-400 w-8 h-8 mb-3" />

            <h2 className="text-3xl font-bold text-white">
              96%
            </h2>

            <p className="text-slate-400">
              AI Accuracy
            </p>

          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 hover:border-yellow-400 transition">

            <BarChart3 className="text-yellow-400 w-8 h-8 mb-3" />

            <h2 className="text-3xl font-bold text-white">
              89
            </h2>

            <p className="text-slate-400">
              Innovation Index
            </p>

          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 hover:border-purple-400 transition">

            <FileText className="text-purple-400 w-8 h-8 mb-3" />

            <h2 className="text-3xl font-bold text-white">
              125
            </h2>

            <p className="text-slate-400">
              Patents Analyzed
            </p>

          </div>

        </div>

        {/* Technology Chart */}

        <TechnologyChart />

        {/* Patent Chart */}

        <PatentChart />

        {/* Research Summary */}

        <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 mt-8">

          <h2 className="text-2xl font-bold text-white mb-6">
            📊 Research Summary
          </h2>

          <div className="grid md:grid-cols-2 gap-6">

            <div className="bg-slate-800 rounded-xl p-5">

              <h3 className="text-cyan-400 font-semibold mb-3">
                Emerging Technology
              </h3>

              <p className="text-slate-300">
                Artificial Intelligence continues to dominate
                research publications and patent filings across
                healthcare, education, and automation.
              </p>

            </div>

            <div className="bg-slate-800 rounded-xl p-5">

              <h3 className="text-green-400 font-semibold mb-3">
                Funding Insights
              </h3>

              <p className="text-slate-300">
                Healthcare and Green Energy attracted the highest
                funding opportunities during this quarter.
              </p>

            </div>

            <div className="bg-slate-800 rounded-xl p-5">

              <h3 className="text-yellow-400 font-semibold mb-3">
                Patent Activity
              </h3>

              <p className="text-slate-300">
                Patent submissions increased by 24% compared to
                the previous quarter, indicating higher innovation
                output.
              </p>

            </div>

            <div className="bg-slate-800 rounded-xl p-5">

              <h3 className="text-purple-400 font-semibold mb-3">
                Commercialization
              </h3>

              <p className="text-slate-300">
                AI-based recommendation models predict strong
                commercialization potential for emerging
                technologies in healthcare and robotics.
              </p>

            </div>

          </div>

        </div>

        {/* Export Buttons */}

        <div className="flex justify-end gap-4 mt-8">

          <button className="bg-cyan-500 hover:bg-cyan-600 text-black px-6 py-3 rounded-xl font-semibold transition">

            Export PDF

          </button>

          <button className="bg-green-500 hover:bg-green-600 text-black px-6 py-3 rounded-xl font-semibold transition">

            Export Excel

          </button>

        </div>

      </main>

    </div>
  );
}