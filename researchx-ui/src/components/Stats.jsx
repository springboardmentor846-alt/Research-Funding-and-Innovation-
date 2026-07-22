import { TrendingUp, FileText, Landmark, Lightbulb } from "lucide-react";

const stats = [
  {
    icon: TrendingUp,
    number: "92%",
    title: "Innovation Score",
    color: "text-cyan-400",
  },
  {
    icon: FileText,
    number: "2.5K+",
    title: "Patents",
    color: "text-purple-400",
  },
  {
    icon: Landmark,
    number: "350+",
    title: "Funding Programs",
    color: "text-emerald-400",
  },
  {
    icon: Lightbulb,
    number: "180+",
    title: "Technologies",
    color: "text-yellow-400",
  },
];

export default function Stats() {
  return (
    <section className="max-w-7xl mx-auto px-8 py-10">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

        {stats.map((item, index) => {
          const Icon = item.icon;

          return (
            <div
              key={index}
              className="bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-cyan-400 hover:shadow-xl hover:shadow-cyan-500/20 transition-all duration-300"
            >
              <Icon className={`w-10 h-10 ${item.color}`} />

              <h2 className="text-4xl font-bold text-white mt-6">
                {item.number}
              </h2>

              <p className="text-slate-400 mt-2">
                {item.title}
              </p>
            </div>
          );
        })}

      </div>
    </section>
  );
}