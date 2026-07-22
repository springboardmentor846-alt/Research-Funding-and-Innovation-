import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import AIRecommendation from "../components/AIRecommendation";

export default function AIInsights() {
  return (
    <div className="flex bg-slate-950 min-h-screen">

      <Sidebar />

      <main className="flex-1 p-8 overflow-auto">

        <Header
          title="AI Insights"
          subtitle="AI-powered research intelligence."
        />

        <AIRecommendation />

      </main>

    </div>
  );
}