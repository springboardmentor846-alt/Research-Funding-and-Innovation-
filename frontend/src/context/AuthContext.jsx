import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load user from localStorage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    const savedToken = localStorage.getItem('token');
    
    if (savedUser && savedToken) {
      try {
        setUser(JSON.parse(savedUser));
        setToken(savedToken);
        setIsAuthenticated(true);
      } catch (e) {
        localStorage.removeItem('user');
        localStorage.removeItem('token');
      }
    }
    setLoading(false);
  }, []);

  const rolesInfo = {
    RESEARCHER: {
      name: 'Researcher',
      email: 'researcher@example.com',
      full_name: 'Dr. Aris Thorne',
      badge: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30'
    },
    STARTUP_FOUNDER: {
      name: 'Startup Founder',
      email: 'startup@example.com',
      full_name: 'Elena Vance',
      badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
    },
    INNOVATION_MANAGER: {
      name: 'Innovation Manager',
      email: 'manager@example.com',
      full_name: 'Marcus Brody',
      badge: 'bg-amber-500/10 text-amber-400 border-amber-500/30'
    },
    SYSTEM_ADMIN: {
      name: 'Administrator',
      email: 'admin@example.com',
      full_name: 'System Administrator',
      badge: 'bg-purple-500/10 text-purple-400 border-purple-500/30'
    }
  };

  const login = (userData) => {
    // Generate a mock token
    const mockToken = `token_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const userWithDefaults = {
      id: userData.id || `user_${Date.now()}`,
      email: userData.email,
      full_name: userData.full_name,
      first_name: userData.first_name,
      last_name: userData.last_name,
      role: userData.role,
      organization: userData.organization,
    };

    setUser(userWithDefaults);
    setToken(mockToken);
    setIsAuthenticated(true);

    // Save to localStorage
    localStorage.setItem('user', JSON.stringify(userWithDefaults));
    localStorage.setItem('token', mockToken);
  };

  const switchRole = (newRole) => {
    if (rolesInfo[newRole] && user) {
      const updatedUser = {
        ...user,
        role: newRole,
      };
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('user');
    localStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      token, 
      isAuthenticated,
      loading,
      login,
      switchRole, 
      rolesInfo, 
      logout, 
      setUser, 
      setToken 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
