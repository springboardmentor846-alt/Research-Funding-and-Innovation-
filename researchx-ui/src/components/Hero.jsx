import { ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Hero() {
  const navigate = useNavigate();

  const handleExplore = () => {
    const section = document.getElementById("features");

    if (section) {
      section.scrollIntoView({
        behavior: "smooth",
      });
    }
  };

  return (
    <section className="max-w-7xl mx-auto px-8 pt-20 pb-24">
      <div className="text-center">

        {/* Badge */}
        <span className="inline-block bg-cyan-500/20 text-cyan-300 px-6 py-2 rounded-full text-sm font-medium border border-cyan-500/30">
          🚀 AI Powered Research Platform
        </span>

        {/* Heading */}
        <h1 className="text-6xl md:text-7xl font-extrabold text-white mt-8 leading-tight">
          Transforming{" "}
          <span className="text-cyan-400">Research</span>
          <br />
          Into Innovation
        </h1>

        {/* Description */}
        <p className="text-slate-400 text-xl mt-8 max-w-3xl mx-auto leading-8">
          Discover funding opportunities, analyze patents, explore
          emerging technologies and evaluate commercialization
          potential using AI-powered insights.
        </p>

        {/* Buttons */}
        <div className="flex flex-col md:flex-row justify-center items-center gap-6 mt-12">

          {/* Explore Platform */}
          <button
            onClick={handleExplore}
            className="flex items-center gap-2 bg-cyan-500 hover:bg-cyan-600 text-black px-8 py-4 rounded-xl text-lg font-semibold shadow-lg transition-all duration-300 hover:scale-105"
          >
            Explore Platform
            <ArrowRight size={20} />
          </button>

          {/* Live Demo */}
          <button
            onClick={() => navigate("/dashboard")}
            className="flex items-center gap-2 bg-slate-800 border-2 border-cyan-400 text-white px-8 py-4 rounded-xl text-lg font-semibold shadow-lg transition-all duration-300 hover:bg-cyan-500 hover:text-black hover:scale-105"
          >
            Live Demo
            <ArrowRight size={20} />
          </button>

        </div>

      </div>
    </section>
  );
}