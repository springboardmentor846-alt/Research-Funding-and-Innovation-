import {
  Brain,
  FileSearch,
  Database,
  Rocket,
} from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "AI Recommendations",
    desc: "Get intelligent funding and commercialization suggestions."
  },
  {
    icon: FileSearch,
    title: "Patent Intelligence",
    desc: "Analyze patent trends and innovation insights."
  },
  {
    icon: Database,
    title: "Technology Intelligence",
    desc: "Track emerging technologies and adoption rates."
  },
  {
    icon: Rocket,
    title: "Commercialization",
    desc: "Measure startup potential and market readiness."
  }
];

export default function FeatureCards() {
  return (
    <section
      id="features"
      className="max-w-7xl mx-auto px-8 py-16"
    >

      <div className="text-center mb-14">

        <h2 className="text-4xl font-bold text-white">
          Platform Features
        </h2>

        <p className="text-slate-400 mt-4">
          Everything researchers need in one intelligent platform.
        </p>

      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">

        {features.map((item, index) => {

          const Icon = item.icon;

          return (

            <div
              key={index}
              className="bg-slate-900 rounded-2xl border border-slate-800 p-8 hover:-translate-y-2 hover:border-cyan-400 hover:shadow-xl hover:shadow-cyan-500/20 transition-all duration-300"
            >

              <Icon className="text-cyan-400 w-12 h-12" />

              <h3 className="text-white text-xl font-semibold mt-6">
                {item.title}
              </h3>

              <p className="text-slate-400 mt-4">
                {item.desc}
              </p>

            </div>

          );

        })}

      </div>

    </section>
  );
}