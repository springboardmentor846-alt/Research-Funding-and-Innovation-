import React, { useState, useEffect } from 'react';
import { Navbar } from '../components/common/Navbar';
import { Sidebar } from '../components/common/Sidebar';
import { Footer } from '../components/common/Footer';
import { fundingAPI } from '../services/api';
import { Loader } from '../components/common/Loader';
import { Modal } from '../components/common/Modal';
import { Search, Filter, DollarSign, Calendar, ExternalLink, Plus, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

export const FundingDiscoveryPage = () => {
  const [grants, setGrants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [grantType, setGrantType] = useState('All');
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [newGrant, setNewGrant] = useState({
    title: '',
    agency: '',
    grant_type: 'Government',
    amount: 500000,
    deadline: '2026-12-31',
    description: '',
    eligibility_criteria: '',
    keywords: ''
  });

  const fetchGrants = async () => {
    setLoading(true);
    try {
      const res = await fundingAPI.getAll({ query, grant_type: grantType });
      setGrants(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGrants();
  }, [grantType]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchGrants();
  };

  const handleCreateGrant = async (e) => {
    e.preventDefault();
    try {
      await fundingAPI.create(newGrant);
      setIsModalOpen(false);
      fetchGrants();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />
      <div className="flex-1 flex">
        <Sidebar />
        <main className="flex-1 p-8 space-y-8 overflow-y-auto">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight gradient-text">
                Funding Opportunity Discovery
              </h1>
              <p className="text-sm text-slate-400 mt-1">Search multi-million dollar federal grants, innovation funds, and private research foundations.</p>
            </div>
            <div className="flex items-center space-x-3">
              <Link
                to="/recommendations"
                className="px-4 py-2.5 rounded-xl font-semibold bg-blue-500/10 border border-blue-500/30 text-blue-400 hover:bg-blue-500/20 text-sm flex items-center space-x-2"
              >
                <Sparkles className="w-4 h-4" />
                <span>AI Recommended Match</span>
              </Link>
              <button
                onClick={() => setIsModalOpen(true)}
                className="px-4 py-2.5 rounded-xl font-bold text-white gradient-bg-accent shadow-lg text-sm flex items-center space-x-2"
              >
                <Plus className="w-4 h-4" />
                <span>Add Opportunity</span>
              </button>
            </div>
          </div>

          {/* Search & Filter Bar */}
          <div className="glass-card p-4 flex flex-col md:flex-row items-center gap-4">
            <form onSubmit={handleSearchSubmit} className="flex-1 relative w-full">
              <Search className="w-5 h-5 absolute left-3 top-3 text-slate-500" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search by keywords, agency (e.g. NSF, NIH, ARPA-H), or technology area..."
                className="w-full pl-10 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm focus:outline-none focus:border-blue-500"
              />
            </form>

            <div className="flex items-center space-x-2 w-full md:w-auto">
              <Filter className="w-4 h-4 text-slate-400" />
              <select
                value={grantType}
                onChange={(e) => setGrantType(e.target.value)}
                className="px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-200 focus:outline-none"
              >
                <option value="All">All Grant Types</option>
                <option value="Government">Government Grants</option>
                <option value="Innovation">Innovation Grants</option>
                <option value="Startup Grant">Startup Grants</option>
                <option value="Research Council">Research Councils</option>
                <option value="International">International Funding</option>
              </select>
            </div>
          </div>

          {loading ? (
            <Loader message="Fetching funding opportunities..." />
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {grants.map((grant) => (
                <div key={grant.id} className="glass-card p-6 space-y-4 flex flex-col justify-between">
                  <div className="space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <span className="px-3 py-1 bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-bold rounded-lg uppercase tracking-wider">
                        {grant.grant_type}
                      </span>
                      <div className="text-xs text-slate-400 flex items-center">
                        <Calendar className="w-3.5 h-3.5 mr-1" /> Deadline: {grant.deadline}
                      </div>
                    </div>

                    <h3 className="text-xl font-bold text-slate-100">{grant.title}</h3>
                    <div className="text-xs font-semibold text-teal-400">{grant.agency}</div>

                    <p className="text-sm text-slate-300 line-clamp-3">{grant.description}</p>
                  </div>

                  <div className="space-y-3 pt-3 border-t border-slate-800/80">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-1 text-emerald-400 font-extrabold text-lg">
                        <DollarSign className="w-5 h-5" />
                        <span>{grant.amount.toLocaleString()} USD</span>
                      </div>
                      {grant.url && (
                        <a
                          href={grant.url}
                          target="_blank"
                          rel="noreferrer"
                          className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold flex items-center space-x-1"
                        >
                          <span>Apply Page</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Add Grant Opportunity Modal */}
          <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Add Funding Opportunity">
            <form onSubmit={handleCreateGrant} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Grant Title</label>
                <input
                  type="text"
                  required
                  value={newGrant.title}
                  onChange={(e) => setNewGrant({...newGrant, title: e.target.value})}
                  className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Agency</label>
                  <input
                    type="text"
                    required
                    value={newGrant.agency}
                    onChange={(e) => setNewGrant({...newGrant, agency: e.target.value})}
                    className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Amount ($)</label>
                  <input
                    type="number"
                    required
                    value={newGrant.amount}
                    onChange={(e) => setNewGrant({...newGrant, amount: parseFloat(e.target.value) || 0})}
                    className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm"
                  />
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Description</label>
                <textarea
                  rows={3}
                  required
                  value={newGrant.description}
                  onChange={(e) => setNewGrant({...newGrant, description: e.target.value})}
                  className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm"
                />
              </div>
              <button type="submit" className="w-full py-2.5 rounded-xl font-bold text-white gradient-bg-accent mt-2">
                Save Opportunity
              </button>
            </form>
          </Modal>
        </main>
      </div>
      <Footer />
    </div>
  );
};
