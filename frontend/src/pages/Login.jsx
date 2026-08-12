import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Mail, Lock, ArrowRight, AlertCircle, CheckCircle } from 'lucide-react';

export const Login = ({ onSwitchToSignup }) => {
  const { login } = useAuth();
  const theme = useTheme();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const demoAccounts = [
    { email: 'dr.thorne@stanford.edu', password: 'researcher123', role: 'RESEARCHER' },
    { email: 'elena@techstartup.com', password: 'startup123', role: 'STARTUP_FOUNDER' },
    { email: 'marcus@innovate.com', password: 'manager123', role: 'INNOVATION_MANAGER' },
    { email: 'admin@platform.com', password: 'admin123', role: 'SYSTEM_ADMIN' }
  ];

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');
    setLoading(true);

    try {
      // Validate credentials
      const demoAccount = demoAccounts.find(
        acc => acc.email.toLowerCase() === email.toLowerCase() && acc.password === password
      );

      if (!demoAccount) {
        setError('Invalid email or password. Please try again or use a demo account.');
        setLoading(false);
        return;
      }

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 800));
      
      setSuccessMessage('Login successful! Redirecting...');
      await login(demoAccount);
    } catch (err) {
      setError('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = (account) => {
    setEmail(account.email);
    setPassword(account.password);
    setError('');
  };

  return (
    <div
      style={{ backgroundColor: theme.colors.bg.primary }}
      className="min-h-screen flex items-center justify-center p-4 transition-colors duration-200"
    >
      <div className="w-full max-w-md">
        {/* Logo Section */}
        <div className="text-center mb-8">
          <div
            style={{ backgroundColor: theme.colors.bg.secondary, borderColor: theme.colors.border }}
            className="w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center border-2"
          >
            <span style={{ color: theme.colors.accent }} className="text-2xl font-bold">AI</span>
          </div>
          <h1 style={{ color: theme.colors.text.primary }} className="text-3xl font-bold mb-2">
            Innovation Intelligence
          </h1>
          <p style={{ color: theme.colors.text.secondary }} className="text-sm">
            Research Funding & Analytics Platform
          </p>
        </div>

        {/* Login Form Card */}
        <div
          style={{
            backgroundColor: theme.colors.bg.secondary,
            borderColor: theme.colors.border,
          }}
          className="border rounded-xl p-6 mb-6 shadow-lg"
        >
          <h2 style={{ color: theme.colors.text.primary }} className="text-xl font-bold mb-6">
            Sign In to Your Account
          </h2>

          {/* Error Message */}
          {error && (
            <div
              style={{
                backgroundColor: theme.isDark ? '#7f1d1d' : '#fee2e2',
                borderColor: theme.isDark ? '#dc2626' : '#fca5a5',
                color: theme.isDark ? '#fca5a5' : '#991b1b',
              }}
              className="p-3 rounded-lg mb-4 flex items-start gap-2 border"
            >
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <p className="text-sm">{error}</p>
            </div>
          )}

          {/* Success Message */}
          {successMessage && (
            <div
              style={{
                backgroundColor: theme.isDark ? '#064e3b' : '#ecfdf5',
                borderColor: theme.isDark ? '#10b981' : '#a7f3d0',
                color: theme.isDark ? '#a7f3d0' : '#065f46',
              }}
              className="p-3 rounded-lg mb-4 flex items-start gap-2 border"
            >
              <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <p className="text-sm">{successMessage}</p>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4 mb-6">
            {/* Email Input */}
            <div>
              <label style={{ color: theme.colors.text.secondary }} className="block text-sm font-medium mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 w-5 h-5" style={{ color: theme.colors.text.tertiary }} />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  style={{
                    backgroundColor: theme.colors.bg.primary,
                    borderColor: theme.colors.border,
                    color: theme.colors.text.primary,
                    focusRingColor: theme.colors.accent,
                  }}
                  className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2"
                  disabled={loading}
                />
              </div>
            </div>

            {/* Password Input */}
            <div>
              <label style={{ color: theme.colors.text.secondary }} className="block text-sm font-medium mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 w-5 h-5" style={{ color: theme.colors.text.tertiary }} />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  style={{
                    backgroundColor: theme.colors.bg.primary,
                    borderColor: theme.colors.border,
                    color: theme.colors.text.primary,
                  }}
                  className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2"
                  disabled={loading}
                />
              </div>
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  style={{ accentColor: theme.colors.accent }}
                  className="w-4 h-4 rounded"
                  disabled={loading}
                />
                <span style={{ color: theme.colors.text.secondary }}>Remember me</span>
              </label>
              <a href="#" style={{ color: theme.colors.accent }} className="hover:opacity-80">
                Forgot password?
              </a>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              disabled={loading || !email || !password}
              style={{
                backgroundColor: loading ? theme.colors.accent : theme.colors.accent,
                opacity: loading || !email || !password ? 0.6 : 1,
              }}
              className="w-full py-2 rounded-lg text-white font-semibold flex items-center justify-center gap-2 transition-all duration-200 hover:opacity-90"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Signing in...
                </>
              ) : (
                <>
                  Sign In
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Sign Up Link */}
          <p style={{ color: theme.colors.text.secondary }} className="text-center text-sm">
            Don't have an account?{' '}
            <button
              onClick={onSwitchToSignup}
              style={{ color: theme.colors.accent }}
              className="font-semibold hover:opacity-80"
            >
              Sign up
            </button>
          </p>
        </div>

        {/* Demo Accounts */}
        <div className="bg-opacity-5 rounded-lg p-4 mb-4" style={{ backgroundColor: theme.colors.accent }}>
          <h3 style={{ color: theme.colors.text.primary }} className="font-semibold text-sm mb-3">
            📋 Demo Accounts
          </h3>
          <div className="space-y-2">
            {demoAccounts.map((account, idx) => (
              <button
                key={idx}
                onClick={() => handleDemoLogin(account)}
                style={{
                  backgroundColor: theme.colors.bg.primary,
                  borderColor: theme.colors.border,
                  color: theme.colors.text.secondary,
                }}
                className="w-full text-left p-2 rounded border text-xs hover:opacity-80 transition-opacity"
              >
                <div style={{ color: theme.colors.text.primary }} className="font-medium">
                  {account.role.replace(/_/g, ' ')}
                </div>
                <div>{account.email}</div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
