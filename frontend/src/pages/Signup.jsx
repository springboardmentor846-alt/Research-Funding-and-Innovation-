import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Mail, Lock, User, Building2, ArrowRight, AlertCircle, CheckCircle } from 'lucide-react';

export const Signup = ({ onSwitchToLogin }) => {
  const { login } = useAuth();
  const theme = useTheme();
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'RESEARCHER',
    organization: '',
    agreedToTerms: false,
  });
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const roles = [
    { value: 'RESEARCHER', label: 'Academic Researcher', description: 'Research and publication focus' },
    { value: 'STARTUP_FOUNDER', label: 'Startup Founder', description: 'Innovation commercialization' },
    { value: 'INNOVATION_MANAGER', label: 'Innovation Manager', description: 'Portfolio management' },
  ];

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const validateForm = () => {
    if (!formData.firstName.trim()) {
      setError('First name is required');
      return false;
    }
    if (!formData.lastName.trim()) {
      setError('Last name is required');
      return false;
    }
    if (!formData.email.includes('@')) {
      setError('Valid email is required');
      return false;
    }
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters');
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }
    if (!formData.organization.trim()) {
      setError('Organization is required');
      return false;
    }
    if (!formData.agreedToTerms) {
      setError('You must agree to the terms and conditions');
      return false;
    }
    return true;
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');

    if (!validateForm()) return;

    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Create new user object
      const newUser = {
        id: `user-${Date.now()}`,
        email: formData.email,
        full_name: `${formData.firstName} ${formData.lastName}`,
        first_name: formData.firstName,
        last_name: formData.lastName,
        role: formData.role,
        organization: formData.organization,
      };

      setSuccessMessage('Account created successfully! Redirecting...');
      await new Promise(resolve => setTimeout(resolve, 500));
      
      await login(newUser);
    } catch (err) {
      setError('Failed to create account. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{ backgroundColor: theme.colors.bg.primary }}
      className="min-h-screen flex items-center justify-center p-4 transition-colors duration-200 py-8"
    >
      <div className="w-full max-w-2xl">
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
            Join the Research Funding & Analytics Platform
          </p>
        </div>

        {/* Signup Form Card */}
        <div
          style={{
            backgroundColor: theme.colors.bg.secondary,
            borderColor: theme.colors.border,
          }}
          className="border rounded-xl p-6 mb-6 shadow-lg"
        >
          <h2 style={{ color: theme.colors.text.primary }} className="text-2xl font-bold mb-6">
            Create Your Account
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

          <form onSubmit={handleSignup} className="space-y-4">
            {/* First and Last Name */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label style={{ color: theme.colors.text.secondary }} className="block text-sm font-medium mb-2">
                  First Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-3 w-5 h-5" style={{ color: theme.colors.text.tertiary }} />
                  <input
                    type="text"
                    name="firstName"
                    value={formData.firstName}
                    onChange={handleChange}
                    placeholder="John"
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
              <div>
                <label style={{ color: theme.colors.text.secondary }} className="block text-sm font-medium mb-2">
                  Last Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-3 w-5 h-5" style={{ color: theme.colors.text.tertiary }} />
                  <input
                    type="text"
                    name="lastName"
                    value={formData.lastName}
                    onChange={handleChange}
                    placeholder="Doe"
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
            </div>

            {/* Email Input */}
            <div>
              <label style={{ color: theme.colors.text.secondary }} className="block text-sm font-medium mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 w-5 h-5" style={{ color: theme.colors.text.tertiary }} />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="you@example.com"
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

            {/* Organization */}
            <div>
              <label style={{ color: theme.colors.text.secondary }} className="block text-sm font-medium mb-2">
                Organization
              </label>
              <div className="relative">
                <Building2 className="absolute left-3 top-3 w-5 h-5" style={{ color: theme.colors.text.tertiary }} />
                <input
                  type="text"
                  name="organization"
                  value={formData.organization}
                  onChange={handleChange}
                  placeholder="University or Company Name"
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

            {/* Role Selection */}
            <div>
              <label style={{ color: theme.colors.text.secondary }} className="block text-sm font-medium mb-3">
                Account Type
              </label>
              <div className="grid grid-cols-1 gap-3">
                {roles.map(role => (
                  <label
                    key={role.value}
                    style={{
                      backgroundColor: formData.role === role.value ? theme.colors.bg.primary : theme.colors.bg.primary,
                      borderColor: formData.role === role.value ? theme.colors.accent : theme.colors.border,
                      borderWidth: '2px',
                    }}
                    className="flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-all"
                  >
                    <input
                      type="radio"
                      name="role"
                      value={role.value}
                      checked={formData.role === role.value}
                      onChange={handleChange}
                      disabled={loading}
                      style={{ accentColor: theme.colors.accent }}
                      className="w-4 h-4 mt-1"
                    />
                    <div>
                      <div style={{ color: theme.colors.text.primary }} className="font-medium text-sm">
                        {role.label}
                      </div>
                      <div style={{ color: theme.colors.text.tertiary }} className="text-xs">
                        {role.description}
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Password Inputs */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label style={{ color: theme.colors.text.secondary }} className="block text-sm font-medium mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 w-5 h-5" style={{ color: theme.colors.text.tertiary }} />
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
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
              <div>
                <label style={{ color: theme.colors.text.secondary }} className="block text-sm font-medium mb-2">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 w-5 h-5" style={{ color: theme.colors.text.tertiary }} />
                  <input
                    type="password"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
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
            </div>

            {/* Terms Agreement */}
            <label className="flex items-start gap-3">
              <input
                type="checkbox"
                name="agreedToTerms"
                checked={formData.agreedToTerms}
                onChange={handleChange}
                style={{ accentColor: theme.colors.accent }}
                className="w-4 h-4 rounded mt-1"
                disabled={loading}
              />
              <span style={{ color: theme.colors.text.secondary }} className="text-sm">
                I agree to the{' '}
                <a href="#" style={{ color: theme.colors.accent }} className="hover:opacity-80">
                  Terms of Service
                </a>{' '}
                and{' '}
                <a href="#" style={{ color: theme.colors.accent }} className="hover:opacity-80">
                  Privacy Policy
                </a>
              </span>
            </label>

            {/* Sign Up Button */}
            <button
              type="submit"
              disabled={loading || !formData.firstName || !formData.email || !formData.password}
              style={{
                backgroundColor: theme.colors.accent,
                opacity: loading || !formData.firstName || !formData.email || !formData.password ? 0.6 : 1,
              }}
              className="w-full py-2 rounded-lg text-white font-semibold flex items-center justify-center gap-2 transition-all duration-200 hover:opacity-90"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Creating Account...
                </>
              ) : (
                <>
                  Create Account
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Login Link */}
          <p style={{ color: theme.colors.text.secondary }} className="text-center text-sm mt-6">
            Already have an account?{' '}
            <button
              onClick={onSwitchToLogin}
              style={{ color: theme.colors.accent }}
              className="font-semibold hover:opacity-80"
            >
              Sign in
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};
