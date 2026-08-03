import { useState, createContext, useContext } from 'react';

export const ProviderContext = createContext(null);

export const useProvider = () => {
  const context = useContext(ProviderContext);

  // Fallback defaults if context is absent
  const activeProvider = context?.activeProvider || 'openai';
  const isRuleBased = activeProvider === 'rule-based';
  const isGoogleAI = activeProvider === 'google';
  const isOpenRouter = activeProvider === 'openrouter';
  
  const providerLabel = isRuleBased ? 'Rule-Based Engine' : 
                        isGoogleAI ? 'Google Gemini AI' : 
                        isOpenRouter ? 'OpenRouter Models' : 'OpenAI';
                        
  const providerColor = isRuleBased ? 'text-orange-500' :
                        isGoogleAI ? 'text-blue-500' :
                        isOpenRouter ? 'text-purple-500' : 'text-green-500';

  const isFallback = context?.isFallback || false;
  const freeTierPercent = context?.freeTierPercent || 100;

  return {
    activeProvider,
    isOpenRouter,
    isGoogleAI,
    isRuleBased,
    isFallback,
    freeTierPercent,
    providerColor,
    providerLabel
  };
};
