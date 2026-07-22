import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import { useEffect, useState } from "react";
import axios from "axios";
import {
  Lightbulb,
  TrendingUp,
  Cpu,
  Rocket,
} from "lucide-react";

export default function Technologies() {
  const [technologies, setTechnologies] = useState([]);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/technologies/")
      .then((res) => setTechnologies(res.data))
      .catch((err) => console.log(err));
  }, []);

  return (
    <div className="flex bg-slate-950 min-h-screen">

      <Sidebar />

      <main className="flex-1 p-8 overflow-auto">

        <Header
          title="Technologies"
          subtitle="Discover emerging technologies."
        />

        {/* Summary Cards */}

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">

          <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 hover:border-yellow-400 transition">
            <Lightbulb className="text-yellow-400 w-8 h-8 mb-3" />
            <h2 className="text-3xl font-bold text-white">
              {technologies.length}
            </h2>
            <p className="text-slate-400">
              Technologies
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 hover:border-green-400 transition">
            <TrendingUp className="text-green-400 w-8 h-8 mb-3" />
            <h2 className="text-3xl font-bold text-white">
              24%
            </h2>
            <p className="text-slate-400">
              Avg Growth
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 hover:border-cyan-400 transition">
            <Cpu className="text-cyan-400 w-8 h-8 mb-3" />
            <h2 className="text-3xl font-bold text-white">
              92%
            </h2>
            <p className="text-slate-400">
              AI Adoption
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 hover:border-purple-400 transition">
            <Rocket className="text-purple-400 w-8 h-8 mb-3" />
            <h2 className="text-3xl font-bold text-white">
              High
            </h2>
            <p className="text-slate-400">
              Innovation
            </p>
          </div>

        </div>

        {/* Technology Cards */}

        <div className="bg-slate-900 rounded-2xl border border-slate-700 p-6">

          <h2 className="text-2xl font-bold text-white mb-6">
            💡 Emerging Technologies
          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">

            {technologies.map((tech) => (

              <div
                key={tech.id}
                className="bg-slate-800 rounded-xl p-5 border border-slate-700 hover:border-cyan-500 hover:scale-105 transition duration-300"
              >

                <h3 className="text-xl font-bold text-white">
                  {tech.technology_name}
                </h3>

                <p className="text-slate-400 mt-2">
                  {tech.description}
                </p>

                <div className="mt-5">

                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-cyan-300">
                      Growth Score
                    </span>

                    <span className="text-green-400">
                      {tech.growth_score}
                    </span>
                  </div>

                  <div className="w-full bg-slate-700 rounded-full h-2">

                    <div
                      className="bg-green-400 h-2 rounded-full"
                      style={{
                        width: `${Math.min(
                          Number(tech.growth_score),
                          100
                        )}%`,
                      }}
                    ></div>

                  </div>

                </div>

                <div className="mt-5 space-y-2">

                  <p className="text-cyan-300">
                    📂 {tech.category}
                  </p>

                  <p className="text-yellow-400">
                    📈 Adoption: {tech.adoption_rate}%
                  </p>

                  <p className="text-purple-400">
                    🚀 {tech.maturity_level}
                  </p>

                </div>

              </div>

            ))}

          </div>

        </div>

        {/* Summary */}

        <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 mt-8">

          <h2 className="text-2xl font-bold text-white mb-4">
            Technology Insights
          </h2>

          <div className="space-y-4 text-slate-300">

            <p>💡 Artificial Intelligence continues to dominate research.</p>

            <p>📈 Healthcare AI is attracting the highest investments.</p>

            <p>🚀 Green Energy technologies show rapid commercialization.</p>

            <p>🤖 Robotics adoption is steadily increasing across industries.</p>

          </div>

        </div>

      </main>

    </div>
  );
}