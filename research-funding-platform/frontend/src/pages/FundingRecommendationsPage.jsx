import React, { useState, useEffect } from 'react';
import { Navbar } from '../components/common/Navbar';
import { Sidebar } from '../components/common/Sidebar';
import { Footer } from '../components/common/Footer';
import { fundingAPI, userAPI } from '../services/api';
import { Loader } from '../components/common/Loader';
import { Sparkles, DollarSign, Calendar, ExternalLink, CheckCircle } from 'lucide-react';

export const FundingRecommendationsPage = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fundingAPI.getRecommendations(),
      userAPI.getProfile()
    ]).then(([rRes, pRes]) => {
      setRecommendations(rRes.data);
      setProfile(pRes.data);
    }).catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />
      <div className="flex-1 flex">
        <Sidebar />
        <main className="flex-1 p-8 space-y-8 overflow-y-auto">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight gradient-text flex items-center space-x-2">
              <Sparkles className="w-8 h-8 text-blue-400" />
              <span>AI Personalized Grant Recommendations</span>
            </h1>
            <p className="text-sm text-slate-400 mt-1">Matched against your profile's research domains, keywords, and publication history.</p>
          </div>

          {profile && (
            <div className="p-4 bg-blue-500/10 border border-blue-500/30 text-blue-300 rounded-xl text-sm space-y-1">
              <strong className="text-slate-200 uppercase text-xs font-bold block">Current Profile Match Criteria</strong>
              <div>Domains: <span className="text-blue-400 font-semibold">{profile.domains}</span></div>
              <div>Keywords: <span className="text-teal-400 font-semibold">{profile.keywords}</span></div>
            </div>
          )}

          {loading ? (
            <Loader message="Running TF-IDF & Keyword Vector Matching Engine..." />
          ) : (
            <div className="space-y-6">
              {recommendations.map((item) => (
                <div key={item.id} className="glass-card p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 border-l-4 border-l-blue-500">
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center space-x-3">
                      <span className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold rounded-lg flex items-center space-x-1">
                        <CheckCircle className="w-3.5 h-3.5" />
                        <span>{item.match_score}% Match ({item.match_tier})</span>
                      </span>
                      <span className="text-xs text-slate-400 font-semibold uppercase">{item.agency}</span>
                    </div>

                    <h3 className="text-xl font-bold text-slate-100">{item.title}</h3>
                    <p className="text-sm text-slate-300">{item.description}</p>
                    
                    <div className="text-xs text-slate-400">
                      <strong className="text-slate-200">Eligibility:</strong> {item.eligibility_criteria}
                    </div>
                  </div>

                  <div className="flex flex-col items-start md:items-end space-y-3 min-w-[200px]">
                    <div className="text-2xl font-extrabold text-emerald-400 flex items-center">
                      <DollarSign className="w-6 h-6" />
                      <span>{item.amount.toLocaleString()}</span>
                    </div>
                    <div className="text-xs text-slate-400 flex items-center">
                      <Calendar className="w-3.5 h-3.5 mr-1" /> Deadline: {item.deadline}
                    </div>
                    {item.url && (
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noreferrer"
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold flex items-center space-x-1 shadow-md shadow-blue-500/20"
                      >
                        <span>View Official Call</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
      <Footer />
    </div>
  );
};
