import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const ProviderStatus = ({ primaryProvider, fallbackProvider, activeProvider, freeTierUsed, freeTierLimit, fallbackEnabled }) => {
  const [showTooltip, setShowTooltip] = useState(false);

  const getStatusColor = (provider) => {
    if (provider?.toLowerCase().includes('openrouter')) return 'bg-green-500';
    if (provider?.toLowerCase().includes('google')) return 'bg-yellow-500';
    return 'bg-orange-500';
  };

  const usagePercent = Math.min(100, Math.round((freeTierUsed / freeTierLimit) * 100)) || 0;

  return (
    <div 
      className="relative inline-flex items-center gap-3 px-4 py-2 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xl cursor-help"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <motion.div
        animate={{ scale: [1, 1.2, 1], opacity: [0.7, 1, 0.7] }}
        transition={{ duration: 2, repeat: Infinity }}
        className={`w-3 h-3 rounded-full ${getStatusColor(activeProvider)}`}
      />
      
      <div className="flex flex-col">
        <span className="text-sm font-medium text-white">{activeProvider}</span>
        {activeProvider !== primaryProvider && fallbackEnabled && (
           <span className="text-xs text-yellow-400">Fallback Mode Active</span>
        )}
      </div>

      <AnimatePresence>
        {showTooltip && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            className="absolute top-full left-0 mt-2 w-64 p-4 rounded-xl bg-[#0a0a1a] border border-white/10 shadow-2xl z-50"
          >
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-400">Primary Provider</span>
                  <span className="text-white font-medium">{primaryProvider}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-400">Fallback Provider</span>
                  <span className="text-white font-medium">{fallbackProvider}</span>
                </div>
              </div>
              
              <div className="pt-3 border-t border-white/10">
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-gray-400">Free Tier Usage</span>
                  <span className="text-white font-medium">{freeTierUsed} / {freeTierLimit}</span>
                </div>
                <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${usagePercent > 90 ? 'bg-red-500' : usagePercent > 70 ? 'bg-yellow-500' : 'bg-indigo-500'}`}
                    style={{ width: `${usagePercent}%` }}
                  />
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ProviderStatus;
