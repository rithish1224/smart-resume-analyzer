import { useState, useEffect, useContext, createContext } from 'react';

// Mock context for demonstration
export const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  
  // Fallback state if context provider is missing
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const login = async (credentials) => {
    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise(r => setTimeout(r, 1000));
      setUser({ id: '123', email: credentials.email, role: 'candidate' });
      setIsAuthenticated(true);
    } catch (err) {
      console.error(err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData) => {
    setIsLoading(true);
    try {
      await new Promise(r => setTimeout(r, 1000));
      setUser({ id: '124', email: userData.email, role: userData.role });
      setIsAuthenticated(true);
    } catch (err) {
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    // Redirect logic typically goes here
  };

  return context || { user, isAuthenticated, isLoading, login, register, logout };
};
