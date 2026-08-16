import React from 'react';
import { Link } from 'react-router-dom';
import { Navbar } from '../components/common/Navbar';
import { Footer } from '../components/common/Footer';
import { AlertTriangle, ArrowLeft } from 'lucide-react';

export const NotFoundPage = () => (
  <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
    <Navbar />
    <div className="flex-1 flex flex-col items-center justify-center p-6 text-center space-y-4">
      <AlertTriangle className="w-16 h-16 text-amber-400 animate-bounce" />
      <h1 className="text-4xl font-extrabold gradient-text">404 - Page Not Found</h1>
      <p className="text-sm text-slate-400 max-w-md">The requested intelligence vector or router endpoint could not be resolved on the system grid.</p>
      <Link to="/dashboard" className="px-6 py-3 rounded-xl font-bold text-white gradient-bg-accent shadow-lg flex items-center space-x-2">
        <ArrowLeft className="w-4 h-4" />
        <span>Return to Dashboard</span>
      </Link>
    </div>
    <Footer />
  </div>
);
