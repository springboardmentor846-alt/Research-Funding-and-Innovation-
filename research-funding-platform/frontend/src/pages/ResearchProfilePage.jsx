import React, { useState, useEffect } from 'react';
import { Navbar } from '../components/common/Navbar';
import { Sidebar } from '../components/common/Sidebar';
import { Footer } from '../components/common/Footer';
import { userAPI } from '../services/api';
import { Loader } from '../components/common/Loader';
import { Save, UserCheck, BookOpen, Award, FileText } from 'lucide-react';

export const ResearchProfilePage = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    userAPI.getProfile()
      .then(res => setProfile(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMsg('');
    try {
      const res = await userAPI.updateProfile(profile);
      setProfile(res.data);
      setMsg('Research profile updated successfully!');
    } catch (err) {
      setMsg('Failed to update research profile.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />
      <div className="flex-1 flex">
        <Sidebar />
        <main className="flex-1 p-8 space-y-8 overflow-y-auto">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight gradient-text">
              Research & Innovation Profile
            </h1>
            <p className="text-sm text-slate-400 mt-1">Configure your scientific expertise, keywords, and impact metrics for grant matching.</p>
          </div>

          {loading ? (
            <Loader message="Fetching research profile..." />
          ) : (
            <form onSubmit={handleSave} className="glass-card p-8 space-y-6 max-w-4xl">
              {msg && (
                <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm rounded-xl">
                  {msg}
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Primary Research Domains</label>
                  <input
                    type="text"
                    value={profile?.domains || ''}
                    onChange={(e) => setProfile({...profile, domains: e.target.value})}
                    placeholder="Artificial Intelligence, Quantum Computing, Genomics"
                    className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm focus:border-blue-500 focus:outline-none"
                  />
                  <p className="text-xs text-slate-500 mt-1">Comma-separated list of scientific disciplines.</p>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Keywords & Focus Areas</label>
                  <input
                    type="text"
                    value={profile?.keywords || ''}
                    onChange={(e) => setProfile({...profile, keywords: e.target.value})}
                    placeholder="Machine Learning, Gene Editing, Solar Energy"
                    className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm focus:border-blue-500 focus:outline-none"
                  />
                  <p className="text-xs text-slate-500 mt-1">Key methodologies, materials, or target outputs.</p>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Institutional Bio / Executive Summary</label>
                <textarea
                  rows={4}
                  value={profile?.bio || ''}
                  onChange={(e) => setProfile({...profile, bio: e.target.value})}
                  placeholder="Summarize your lab's core technical capabilities, past grants, and commercialization track record..."
                  className="w-full p-4 bg-slate-950 border border-slate-800 rounded-xl text-sm focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4 border-t border-slate-800">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Total Publications</label>
                  <input
                    type="number"
                    value={profile?.publications_count || 0}
                    onChange={(e) => setProfile({...profile, publications_count: parseInt(e.target.value) || 0})}
                    className="w-full px-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Patents Held</label>
                  <input
                    type="number"
                    value={profile?.patents_count || 0}
                    onChange={(e) => setProfile({...profile, patents_count: parseInt(e.target.value) || 0})}
                    className="w-full px-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">H-Index</label>
                  <input
                    type="number"
                    value={profile?.h_index || 0}
                    onChange={(e) => setProfile({...profile, h_index: parseInt(e.target.value) || 0})}
                    className="w-full px-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm"
                  />
                </div>
              </div>

              <div className="flex justify-end pt-4">
                <button
                  type="submit"
                  disabled={saving}
                  className="px-6 py-3 rounded-xl font-bold text-white gradient-bg-accent shadow-lg flex items-center space-x-2"
                >
                  <Save className="w-4 h-4" />
                  <span>{saving ? 'Saving...' : 'Update Profile'}</span>
                </button>
              </div>
            </form>
          )}
        </main>
      </div>
      <Footer />
    </div>
  );
};
