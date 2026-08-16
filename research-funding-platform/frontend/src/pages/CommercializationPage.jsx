import React, { useState, useEffect } from 'react';
import { Navbar } from '../components/common/Navbar';
import { Sidebar } from '../components/common/Sidebar';
import { Footer } from '../components/common/Footer';
import { commercialAPI } from '../services/api';
import { Loader } from '../components/common/Loader';
import { Briefcase, DollarSign, Mail, Building, Plus } from 'lucide-react';
import { Modal } from '../components/common/Modal';

export const CommercializationPage = () => {
  const [opps, setOpps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [newOpp, setNewOpp] = useState({
    title: '',
    insight_type: 'Licensing',
    description: '',
    target_industry: '',
    estimated_value: '$5.0M Licensing',
    contact_email: ''
  });

  const fetchOpps = async () => {
    try {
      const res = await commercialAPI.getAll();
      setOpps(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOpps();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await commercialAPI.create(newOpp);
      setIsModalOpen(false);
      fetchOpps();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />
      <div className="flex-1 flex">
        <Sidebar />
        <main className="flex-1 p-8 space-y-8 overflow-y-auto">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight gradient-text">
                Commercialization & Spin-off Opportunities
              </h1>
              <p className="text-sm text-slate-400 mt-1">Transform academic research into commercial startup spin-offs and industry licensing agreements.</p>
            </div>
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-4 py-2.5 rounded-xl font-bold text-white gradient-bg-accent shadow-lg text-sm flex items-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>Post Opportunity</span>
            </button>
          </div>

          {loading ? (
            <Loader message="Loading commercialization opportunities..." />
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {opps.map((op) => (
                <div key={op.id} className="glass-card p-6 space-y-4 flex flex-col justify-between">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="px-3 py-1 bg-teal-500/10 border border-teal-500/30 text-teal-400 text-xs font-bold rounded-lg uppercase">
                        {op.insight_type}
                      </span>
                      <span className="text-xs font-extrabold text-emerald-400">{op.estimated_value}</span>
                    </div>

                    <h3 className="text-xl font-bold text-slate-100">{op.title}</h3>
                    <div className="text-xs font-semibold text-slate-400">Target Industry: <strong className="text-slate-200">{op.target_industry}</strong></div>
                    <p className="text-sm text-slate-300">{op.description}</p>
                  </div>

                  <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
                    <span className="text-slate-400">Contact: {op.contact_email || 'techtransfer@org.com'}</span>
                    <a href={`mailto:${op.contact_email}`} className="px-3 py-1 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-lg">
                      Inquire Deal
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}

          <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Post Commercial Opportunity">
            <form onSubmit={handleCreate} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Opportunity Title</label>
                <input type="text" required value={newOpp.title} onChange={(e) => setNewOpp({...newOpp, title: e.target.value})} className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm" />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Type</label>
                  <select value={newOpp.insight_type} onChange={(e) => setNewOpp({...newOpp, insight_type: e.target.value})} className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm">
                    <option value="Licensing">Licensing</option>
                    <option value="Startup Spin-off">Startup Spin-off</option>
                    <option value="Productization">Productization</option>
                    <option value="Industry Partnership">Industry Partnership</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Target Industry</label>
                  <input type="text" required value={newOpp.target_industry} onChange={(e) => setNewOpp({...newOpp, target_industry: e.target.value})} className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm" />
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Description</label>
                <textarea rows={3} required value={newOpp.description} onChange={(e) => setNewOpp({...newOpp, description: e.target.value})} className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm" />
              </div>
              <button type="submit" className="w-full py-2.5 rounded-xl font-bold text-white gradient-bg-accent">
                Submit Opportunity
              </button>
            </form>
          </Modal>
        </main>
      </div>
      <Footer />
    </div>
  );
};
