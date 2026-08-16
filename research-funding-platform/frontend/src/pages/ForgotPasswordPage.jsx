import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { authAPI } from '../services/api';
import { Navbar } from '../components/common/Navbar';
import { Footer } from '../components/common/Footer';
import { Mail } from 'lucide-react';

export const ForgotPasswordPage = () => {
  const [email, setEmail] = useState('');
  const [msg, setMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await authAPI.forgotPassword({ email });
      setMsg(res.data.message);
    } catch (e) {
      setMsg('Error dispatching password reset request.');
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="glass-card max-w-md w-full p-8 space-y-6">
          <h2 className="text-2xl font-bold gradient-text text-center">Password Recovery</h2>
          <p className="text-xs text-slate-400 text-center">Enter your registered email address to receive recovery instructions.</p>
          
          {msg && <div className="p-3 bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs rounded-xl">{msg}</div>}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Email Address</label>
              <div className="relative">
                <Mail className="w-5 h-5 absolute left-3 top-3 text-slate-500" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your.email@org.com"
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-sm focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <button type="submit" className="w-full py-3 rounded-xl font-bold text-white gradient-bg-accent">
              Send Recovery Token
            </button>
          </form>

          <div className="text-center text-xs">
            <Link to="/login" className="text-blue-400 hover:underline">Back to Login</Link>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};
