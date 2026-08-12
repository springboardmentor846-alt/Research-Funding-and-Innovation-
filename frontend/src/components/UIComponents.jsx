import React from 'react';
import { useTheme } from '../context/ThemeContext';

// Card Component
export const Card = ({ children, className = '', ...props }) => {
  const { theme } = useTheme();
  return (
    <div
      style={{
        backgroundColor: theme.colors.bg.secondary,
        borderColor: theme.colors.border,
      }}
      className={`border rounded-lg p-6 transition-colors duration-200 ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

// Button Component
export const Button = ({ children, variant = 'primary', className = '', ...props }) => {
  const { theme } = useTheme();
  
  const baseStyle = {
    padding: '10px 20px',
    borderRadius: '8px',
    fontWeight: '500',
    border: 'none',
    cursor: 'pointer',
    transition: 'all 0.2s',
    fontSize: '14px',
  };

  const variants = {
    primary: {
      ...baseStyle,
      backgroundColor: theme.colors.accent,
      color: '#ffffff',
    },
    secondary: {
      ...baseStyle,
      backgroundColor: theme.colors.bg.tertiary,
      color: theme.colors.text.primary,
      border: `1px solid ${theme.colors.border}`,
    },
    ghost: {
      ...baseStyle,
      backgroundColor: 'transparent',
      color: theme.colors.accent,
      border: `1px solid ${theme.colors.accent}`,
    },
  };

  return (
    <button
      style={variants[variant] || variants.primary}
      className={className}
      onMouseEnter={(e) => {
        if (variant === 'primary') {
          e.currentTarget.style.backgroundColor = theme.colors.accentHover;
          e.currentTarget.style.boxShadow = `0 0 20px ${theme.colors.accent}40`;
        }
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = 'none';
        if (variant === 'primary') {
          e.currentTarget.style.backgroundColor = theme.colors.accent;
        }
      }}
      {...props}
    >
      {children}
    </button>
  );
};

// Badge Component
export const Badge = ({ children, color = 'accent', className = '' }) => {
  const { theme } = useTheme();
  
  const colors = {
    accent: theme.colors.accent,
    success: theme.colors.success,
    warning: theme.colors.warning,
    error: theme.colors.error,
  };

  const badgeColor = colors[color] || theme.colors.accent;

  return (
    <span
      style={{
        backgroundColor: badgeColor + '20',
        color: badgeColor,
        borderColor: badgeColor + '50',
      }}
      className={`inline-block px-3 py-1 rounded-full text-xs font-bold border ${className}`}
    >
      {children}
    </span>
  );
};

// Stat Card Component
export const StatCard = ({ icon: Icon, label, value, description, onClick, color }) => {
  const { theme } = useTheme();

  return (
    <button
      onClick={onClick}
      style={{
        backgroundColor: theme.colors.bg.secondary,
        borderColor: theme.colors.border,
      }}
      className="border rounded-lg p-6 hover:shadow-lg transition-all duration-200 text-left group w-full"
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor = theme.colors.bg.tertiary;
        e.currentTarget.style.borderColor = color;
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = theme.colors.bg.secondary;
        e.currentTarget.style.borderColor = theme.colors.border;
      }}
    >
      <div className="flex items-start justify-between mb-4">
        <div
          style={{ backgroundColor: color + '20', color: color }}
          className="p-3 rounded-lg"
        >
          <Icon size={24} />
        </div>
      </div>
      <p style={{ color: theme.colors.text.tertiary }} className="text-sm mb-1">
        {label}
      </p>
      <p style={{ color: theme.colors.text.primary }} className="text-2xl font-bold">
        {value}
      </p>
      {description && (
        <p style={{ color: theme.colors.text.tertiary }} className="text-xs mt-2">
          {description}
        </p>
      )}
    </button>
  );
};

// Section Header Component
export const SectionHeader = ({ title, description, children }) => {
  const { theme } = useTheme();

  return (
    <div className="mb-6">
      <h2 style={{ color: theme.colors.text.primary }} className="text-2xl font-bold mb-2">
        {title}
      </h2>
      {description && (
        <p style={{ color: theme.colors.text.tertiary }} className="text-sm">
          {description}
        </p>
      )}
      {children}
    </div>
  );
};

// Input Component
export const Input = ({ label, ...props }) => {
  const { theme } = useTheme();

  return (
    <div className="mb-4">
      {label && (
        <label style={{ color: theme.colors.text.primary }} className="block text-sm font-medium mb-2">
          {label}
        </label>
      )}
      <input
        style={{
          backgroundColor: theme.colors.bg.primary,
          color: theme.colors.text.primary,
          borderColor: theme.colors.border,
        }}
        className="w-full px-4 py-2 rounded-lg border focus:outline-none transition-colors"
        onFocus={(e) => (e.target.style.borderColor = theme.colors.accent)}
        onBlur={(e) => (e.target.style.borderColor = theme.colors.border)}
        {...props}
      />
    </div>
  );
};

// Loading Spinner
export const Spinner = ({ size = 'md' }) => {
  const { theme } = useTheme();

  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div
      className={`${sizes[size]} border-4 border-t-transparent rounded-full animate-spin`}
      style={{
        borderColor: theme.colors.border,
        borderTopColor: theme.colors.accent,
      }}
    />
  );
};
