import { Link } from "react-router-dom";
import {
  Rocket,
  Users,
  Briefcase,
  Star,
  ArrowRight,
} from "lucide-react";

export default function StartupDashboard() {
  return (
    <div className="max-w-6xl mx-auto p-8">

      {/* Header */}

      <div className="mb-10">

        <span className="uppercase tracking-[3px] text-xs font-semibold text-slate-500">
          STARTUP WORKSPACE
        </span>

        <h1 className="text-4xl font-bold text-slate-900 mt-3">
          Startup Founder Dashboard
        </h1>

        <p className="text-slate-500 mt-3 text-lg">
          Manage your startup profile, discover researchers and explore
          funding opportunities from a single workspace.
        </p>

      </div>

      {/* Statistics */}

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-10">

        <div className="bg-white rounded-2xl shadow-lg border border-slate-100 p-6">

          <Rocket className="text-blue-600 mb-5" size={34} />

          <p className="text-slate-500 text-sm">
            Startup Stage
          </p>

          <h2 className="text-3xl font-bold mt-2">
            Idea
          </h2>

        </div>

        <div className="bg-white rounded-2xl shadow-lg border border-slate-100 p-6">

          <Users className="text-green-600 mb-5" size={34} />

          <p className="text-slate-500 text-sm">
            Researchers Connected
          </p>

          <h2 className="text-3xl font-bold mt-2">
            0
          </h2>

        </div>

        <div className="bg-white rounded-2xl shadow-lg border border-slate-100 p-6">

          <Briefcase className="text-purple-600 mb-5" size={34} />

          <p className="text-slate-500 text-sm">
            Collaboration Requests
          </p>

          <h2 className="text-3xl font-bold mt-2">
            0
          </h2>

        </div>

        <div className="bg-white rounded-2xl shadow-lg border border-slate-100 p-6">

          <Star className="text-amber-500 mb-5" size={34} />

          <p className="text-slate-500 text-sm">
            Innovation Score
          </p>

          <h2 className="text-3xl font-bold mt-2">
            --
          </h2>

        </div>

      </div>

      {/* Dashboard Modules */}

      <div className="mb-6">

        <h2 className="text-2xl font-bold text-slate-900">
          Startup Modules
        </h2>

        <p className="text-slate-500 mt-2">
          Everything required to build collaborations and secure funding.
        </p>

      </div>

      <div className="grid md:grid-cols-2 xl:grid-cols-2 gap-6">

        <Link
          to="/startup/profile"
          className="bg-white rounded-2xl shadow-lg border border-slate-100 p-7 hover:shadow-xl transition"
        >

          <Rocket className="text-blue-600 mb-5" size={34} />

          <h3 className="text-xl font-semibold">
            Startup Profile
          </h3>

          <p className="text-slate-500 mt-3">
            Complete your startup information and improve visibility to
            researchers and funding agencies.
          </p>

          <ArrowRight className="mt-8" />

        </Link>

        <Link
          to="/startup/researchers"
          className="bg-white rounded-2xl shadow-lg border border-slate-100 p-7 hover:shadow-xl transition"
        >

          <Users className="text-green-600 mb-5" size={34} />

          <h3 className="text-xl font-semibold">
            Find Researchers
          </h3>

          <p className="text-slate-500 mt-3">
            Browse researchers based on technology domains,
            expertise and publications.
          </p>

          <ArrowRight className="mt-8" />

        </Link>

        <Link
          to="/startup/requests"
          className="bg-white rounded-2xl shadow-lg border border-slate-100 p-7 hover:shadow-xl transition"
        >

          <Briefcase className="text-purple-600 mb-5" size={34} />

          <h3 className="text-xl font-semibold">
            Collaboration Requests
          </h3>

          <p className="text-slate-500 mt-3">
            View incoming collaboration requests and manage partnerships.
          </p>

          <ArrowRight className="mt-8" />

        </Link>

        <Link
          to="/startup/funding"
          className="bg-white rounded-2xl shadow-lg border border-slate-100 p-7 hover:shadow-xl transition"
        >

          <Star className="text-amber-500 mb-5" size={34} />

          <h3 className="text-xl font-semibold">
            Funding Opportunities
          </h3>

          <p className="text-slate-500 mt-3">
            Discover grants, startup schemes and investment opportunities.
          </p>

          <ArrowRight className="mt-8" />

        </Link>

      </div>

      {/* Recent Activity */}

      <div className="bg-white rounded-2xl shadow-lg border border-slate-100 p-8 mt-10">

        <h2 className="text-2xl font-bold mb-4">
          Recent Activity
        </h2>

        <div className="rounded-xl bg-slate-50 p-10 text-center text-slate-500">

          No recent activity.

          <br />

          Your startup activity will appear here as you use the platform.

        </div>

      </div>

    </div>
  );
}