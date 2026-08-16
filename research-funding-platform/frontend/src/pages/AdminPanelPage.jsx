import React, { useState, useEffect } from 'react';
import { Navbar } from '../components/common/Navbar';
import { Sidebar } from '../components/common/Sidebar';
import { Footer } from '../components/common/Footer';
import { adminAPI } from '../services/api';
import { Loader } from '../components/common/Loader';
import { ShieldAlert, Users, Database, Activity, RefreshCw } from 'lucide-react';

export const AdminPanelPage = () => {
  const [users, setUsers] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [msg, setMsg] = useState('');

  const fetchAdminData = async () => {
    try {
      const [uRes, aRes] = await Promise.all([
        adminAPI.getUsers(),
        adminAPI.getAuditLogs()
      ]);
      setUsers(uRes.data);
      setAuditLogs(aRes.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

  const handleToggleStatus = async (id, currentStatus) => {
    try {
      await adminAPI.toggleStatus(id, !currentStatus);
      fetchAdminData();
    } catch (e) {
      console.error(e);
    }
  };

  const handleSeed = async () => {
    setSeeding(true);
    try {
      const res = await adminAPI.seedDatabase();
      setMsg(res.data.message);
      fetchAdminData();
    } catch (e) {
      setMsg('Seeding error.');
    } finally {
      setSeeding(false);
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
              <h1 className="text-3xl font-extrabold tracking-tight gradient-text flex items-center space-x-2">
                <ShieldAlert className="w-8 h-8 text-rose-500" />
                <span>Enterprise Administration Panel</span>
              </h1>
              <p className="text-sm text-slate-400 mt-1">Role-Based Control, Audit Logging, and System Seeding Controls.</p>
            </div>

            <button
              onClick={handleSeed}
              disabled={seeding}
              className="px-4 py-2.5 rounded-xl font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs flex items-center space-x-2 shadow-lg"
            >
              <Database className="w-4 h-4" />
              <span>{seeding ? 'Seeding Data...' : 'Re-Seed Dataset'}</span>
            </button>
          </div>

          {msg && <div className="p-3 bg-blue-500/10 border border-blue-500/30 text-blue-400 text-sm rounded-xl">{msg}</div>}

          {loading ? (
            <Loader message="Gathering system administrative logs..." />
          ) : (
            <div className="space-y-8">
              {/* User Management Table */}
              <div className="glass-card p-6 space-y-4">
                <h3 className="text-xl font-bold flex items-center space-x-2">
                  <Users className="w-5 h-5 text-blue-400" />
                  <span>User Role Management ({users.length} Users)</span>
                </h3>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm border-collapse">
                    <thead>
                      <tr className="border-b border-slate-800 text-xs text-slate-400 uppercase">
                        <th className="p-3">User</th>
                        <th className="p-3">Role</th>
                        <th className="p-3">Organization</th>
                        <th className="p-3">Status</th>
                        <th className="p-3 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {users.map((u) => (
                        <tr key={u.id} className="hover:bg-slate-900/40">
                          <td className="p-3 font-semibold text-slate-200">
                            <div>{u.full_name}</div>
                            <div className="text-xs text-slate-500 font-normal">{u.email}</div>
                          </td>
                          <td className="p-3"><span className="px-2 py-0.5 bg-blue-500/10 text-blue-400 text-xs rounded-md font-semibold">{u.role}</span></td>
                          <td className="p-3 text-slate-400">{u.organization}</td>
                          <td className="p-3">
                            <span className={`px-2 py-0.5 text-xs font-bold rounded-md ${u.is_active ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                              {u.is_active ? 'Active' : 'Disabled'}
                            </span>
                          </td>
                          <td className="p-3 text-right">
                            <button
                              onClick={() => handleToggleStatus(u.id, u.is_active)}
                              className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg"
                            >
                              {u.is_active ? 'Disable' : 'Enable'}
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Audit Logs Table */}
              <div className="glass-card p-6 space-y-4">
                <h3 className="text-xl font-bold flex items-center space-x-2">
                  <Activity className="w-5 h-5 text-teal-400" />
                  <span>Security & API Audit Log Feed</span>
                </h3>

                <div className="space-y-2 max-h-80 overflow-y-auto">
                  {auditLogs.map((log) => (
                    <div key={log.id} className="p-3 bg-slate-950/80 border border-slate-800 rounded-xl text-xs flex items-center justify-between">
                      <div>
                        <span className="font-bold text-teal-400 mr-2">{log.action}</span>
                        <span className="text-slate-300 font-mono">{log.endpoint}</span>
                      </div>
                      <div className="text-slate-500 font-mono">{new Date(log.timestamp).toLocaleTimeString()} • IP {log.ip_address || '127.0.0.1'}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
      <Footer />
    </div>
  );
};
