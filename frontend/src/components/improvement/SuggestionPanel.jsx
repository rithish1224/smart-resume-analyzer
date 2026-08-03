import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function SuggestionPanel({ generalSuggestions = [], domainSuggestions = [], companySuggestions = [], company, domain, priorityActions = [] }) {
  const [activeTab, setActiveTab] = useState('general');
  const [completedActions, setCompletedActions] = useState(new Set());

  const toggleAction = (id) => {
    const next = new Set(completedActions);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setCompletedActions(next);
  };

  const getActiveSuggestions = () => {
    if (activeTab === 'general') return generalSuggestions;
    if (activeTab === 'domain') return domainSuggestions;
    if (activeTab === 'company') return companySuggestions;
    return [];
  };

  const currentSuggestions = getActiveSuggestions();
  const totalSuggestions = currentSuggestions.length;
  const completedCount = currentSuggestions.filter(s => completedActions.has(s.id)).length;
  const progress = totalSuggestions === 0 ? 0 : (completedCount / totalSuggestions) * 100;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 rounded-2xl backdrop-blur-xl bg-white/5 border border-white/10"
    >
      {priorityActions.length > 0 && (
        <div className="mb-8 p-4 rounded-xl bg-red-500/10 border border-red-500/30">
          <h3 className="text-red-400 font-bold mb-3 flex items-center gap-2">
            <span>🔥</span> Do These First
          </h3>
          <ul className="space-y-2">
            {priorityActions.slice(0, 3).map((action, i) => (
              <li key={i} className="text-sm text-gray-200 flex items-start gap-2">
                <span className="text-red-400 mt-0.5">•</span>
                {action}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex gap-2 mb-6 border-b border-white/10 pb-4">
        {['general', 'domain', 'company'].map(tab => {
          const isDisabled = tab === 'company' && !company;
          return (
            <button
              key={tab}
              disabled={isDisabled}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab 
                  ? 'bg-indigo-500 text-white' 
                  : isDisabled 
                    ? 'text-gray-600 cursor-not-allowed' 
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              {tab === 'general' && 'General ✨'}
              {tab === 'domain' && 'Domain 🎯'}
              {tab === 'company' && 'Company 🏢'}
            </button>
          );
        })}
      </div>

      <div className="mb-6">
        <div className="flex justify-between text-xs text-gray-400 mb-2">
          <span>{completedCount}/{totalSuggestions} suggestions addressed</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="w-full h-1.5 bg-gray-700 rounded-full overflow-hidden">
          <motion.div 
            className="h-full bg-emerald-500"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="min-h-[200px]">
        {activeTab === 'company' && !companySuggestions.length && company && (
          <div className="p-4 rounded-xl bg-white/5 border border-white/10 text-center text-gray-400 text-sm">
            Based on general best practices for {domain} companies.
          </div>
        )}
        
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -10 }}
            className="space-y-4"
          >
            {currentSuggestions.map((suggestion, i) => (
              <motion.div 
                key={suggestion.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className={`p-4 rounded-xl border transition-colors flex gap-4 ${
                  completedActions.has(suggestion.id) 
                    ? 'bg-emerald-500/5 border-emerald-500/20' 
                    : 'bg-white/5 border-white/10'
                }`}
              >
                <button 
                  onClick={() => toggleAction(suggestion.id)}
                  className={`mt-1 shrink-0 w-6 h-6 rounded border flex items-center justify-center transition-colors ${
                    completedActions.has(suggestion.id)
                      ? 'bg-emerald-500 border-emerald-500 text-white'
                      : 'border-gray-500 text-transparent hover:border-emerald-400'
                  }`}
                >
                  ✓
                </button>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span>{suggestion.icon || '💡'}</span>
                    <h4 className={`font-medium ${completedActions.has(suggestion.id) ? 'text-gray-400 line-through' : 'text-gray-200'}`}>
                      {suggestion.title}
                    </h4>
                    {suggestion.priority && (
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        suggestion.priority === 'High' ? 'bg-red-500/20 text-red-400' :
                        suggestion.priority === 'Med' ? 'bg-amber-500/20 text-amber-400' :
                        'bg-blue-500/20 text-blue-400'
                      }`}>
                        {suggestion.priority}
                      </span>
                    )}
                  </div>
                  <p className={`text-sm ${completedActions.has(suggestion.id) ? 'text-gray-500' : 'text-gray-400'}`}>
                    {suggestion.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
