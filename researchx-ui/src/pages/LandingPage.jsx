import Navbar from "../components/Navbar";
import Hero from "../components/Hero";
import Stats from "../components/Stats";
import FeatureCards from "../components/FeatureCards";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950">

      <Navbar />

      <Hero />

      <Stats />

      <FeatureCards />

    </div>
  );
}