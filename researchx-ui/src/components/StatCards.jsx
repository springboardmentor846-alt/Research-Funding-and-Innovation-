import { useEffect, useState } from "react";
import axios from "axios";
import { FileText, Lightbulb, Landmark, TrendingUp } from "lucide-react";

export default function StatCards() {
  const [patents, setPatents] = useState(0);
  const [technologies, setTechnologies] = useState(0);
  const [funding, setFunding] = useState(0);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/patents/")
      .then((res) => setPatents(res.data.length))
      .catch(console.error);

    axios
      .get("http://127.0.0.1:8000/technologies/")
      .then((res) => setTechnologies(res.data.length))
      .catch(console.error);

    axios
      .get("http://127.0.0.1:8000/funding/")
      .then((res) => setFunding(res.data.length))
      .catch(console.error);
  }, []);

  const cards = [
    {
      title: "Patents",
      value: patents,
      icon: FileText,
      iconColor: "text-cyan-400",
      border: "hover:border-cyan-400",
      bg: "from-cyan-500/20 to-cyan-700/10",
      trend: "+12%",
      subtitle: "Research patents",
    },
    {
      title: "Technologies",
      value: technologies,
      icon: Lightbulb,
      iconColor: "text-yellow-400",
      border: "hover:border-yellow-400",
      bg: "from-yellow-500/20 to-yellow-700/10",
      trend: "+8%",
      subtitle: "Emerging technologies",
    },
    {
      title: "Funding",
      value: funding,
      icon: Landmark,
      iconColor: "text-green-400",
      border: "hover:border-green-400",
      bg: "from-green-500/20 to-green-700/10",
      trend: "+15%",
      subtitle: "Funding opportunities",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {cards.map((card, index) => {
        const Icon = card.icon;

        return (
          <div
            key={index}
            className={`relative overflow-hidden rounded-2xl border border-slate-700 bg-gradient-to-br ${card.bg} p-6 shadow-lg transition-all duration-300 hover:scale-105 ${card.border}`}
          >
            <div className="absolute top-0 right-0 h-24 w-24 rounded-full bg-white/5 blur-2xl"></div>

            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">{card.title}</p>

                <h2 className="text-5xl font-bold text-white mt-3">
                  {card.value}
                </h2>

                <p className="text-slate-300 mt-3">
                  {card.subtitle}
                </p>
              </div>

              <div className="bg-slate-900/60 p-4 rounded-xl">
                <Icon className={`${card.iconColor}`} size={34} />
              </div>
            </div>

            <div className="mt-6 flex items-center gap-2 text-green-400 font-semibold">
              <TrendingUp size={18} />
              {card.trend}
              <span className="text-slate-400 text-sm font-normal">
                this month
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}