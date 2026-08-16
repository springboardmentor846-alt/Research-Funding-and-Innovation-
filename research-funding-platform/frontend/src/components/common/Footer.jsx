import React from 'react';

export const Footer = () => (
  <footer className="border-t border-slate-800/60 bg-slate-950/80 py-6 px-8 text-center text-xs text-slate-500">
    <div className="flex flex-col md:flex-row items-center justify-between gap-4">
      <div>
        © 2026 InnovateAI Research & Intelligence Platform. All rights reserved.
      </div>
      <div className="flex space-x-6">
        <a href="#privacy" className="hover:text-slate-300">Privacy Policy</a>
        <a href="#terms" className="hover:text-slate-300">Terms of Service</a>
        <a href="#api" className="hover:text-slate-300">OpenAPI Docs</a>
        <a href="#security" className="hover:text-slate-300">Enterprise Security</a>
      </div>
    </div>
  </footer>
);
