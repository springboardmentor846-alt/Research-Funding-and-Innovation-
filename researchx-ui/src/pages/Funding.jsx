import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import FundingTable from "../components/FundingTable";
import { Landmark, Building2, IndianRupee, Briefcase } from "lucide-react";

export default function Funding() {
  return (
    <div className="flex bg-slate-950 min-h-screen">

      <Sidebar />

      <main className="flex-1 p-8 overflow-auto">

        <Header
          title="Funding"
          subtitle="Explore funding opportunities."
        />

        {/* Summary Cards */}

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">

          <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 hover:border-cyan-400 transition">

            <Landmark className="text-cyan-400 w-8 h-8 mb-3" />

            <h2 className="text-3xl font-bold text-white">
              18
            </h2>

            <p className="text-slate-400">
              Funding Programs
            </p>

          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 hover:border-green-400 transition">

            <Building2 className="text-green-400 w-8 h-8 mb-3" />

            <h2 className="text-3xl font-bold text-white">
              12
            </h2>

            <p className="text-slate-400">
              Organizations
            </p>

          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 hover:border-yellow-400 transition">

            <IndianRupee className="text-yellow-400 w-8 h-8 mb-3" />

            <h2 className="text-3xl font-bold text-white">
              ₹5 Cr
            </h2>

            <p className="text-slate-400">
              Total Funding
            </p>

          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 hover:border-purple-400 transition">

            <Briefcase className="text-purple-400 w-8 h-8 mb-3" />

            <h2 className="text-3xl font-bold text-white">
              8
            </h2>

            <p className="text-slate-400">
              Active Grants
            </p>

          </div>

        </div>

        {/* Funding Table */}

        <FundingTable />

      </main>

    </div>
  );
}