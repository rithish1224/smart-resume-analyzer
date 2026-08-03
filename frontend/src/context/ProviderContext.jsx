import React, { createContext, useContext, useState, useEffect } from 'react';
import { roadmapApi } from '../api/client';

const ProviderContext = createContext(null);

export const ProviderProvider = ({ children }) => {
  const [primaryProvider, setPrimaryProvider] = useState('openai');
  const [fallbackProvider, setFallbackProvider] = useState('gemini');
  const [activeProvider, setActiveProvider] = useState('openai');
  const [fallbackEnabled, setFallbackEnabled] = useState(true);
  const [freeTierUsed, setFreeTierUsed] = useState(0);
  const [freeTierLimit, setFreeTierLimit] = useState(100);
  const [isLoading, setIsLoading] = useState(true);

  const fetchStatus = async () => {
    try {
      const res = await roadmapApi.getProviderStatus();
      const data = res.data || {};
      setPrimaryProvider(data.primary_provider || data.primaryProvider || 'openai');
      setFallbackProvider(data.fallback_provider || data.fallbackProvider || 'gemini');
      setActiveProvider(data.active_provider || data.activeProvider || 'openai');
      setFallbackEnabled(data.fallback_enabled ?? data.fallbackEnabled ?? true);
      setFreeTierUsed(data.free_tier_used ?? data.freeTierUsed ?? 0);
      setFreeTierLimit(data.free_tier_limit ?? data.freeTierLimit ?? 100);
    } catch (error) {
      console.error('Failed to fetch provider status', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <ProviderContext.Provider value={{
      primaryProvider,
      fallbackProvider,
      activeProvider,
      fallbackEnabled,
      freeTierUsed,
      freeTierLimit,
      isLoading,
      refreshStatus: fetchStatus
    }}>
      {children}
    </ProviderContext.Provider>
  );
};

export const ProviderContextProvider = ProviderProvider;

export const useProvider = () => {
  const context = useContext(ProviderContext);
  if (!context) {
    throw new Error('useProvider must be used within a ProviderProvider');
  }
  return context;
};
