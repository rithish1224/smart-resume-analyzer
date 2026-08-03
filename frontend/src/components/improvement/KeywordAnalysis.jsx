import React from 'react';
import { motion } from 'framer-motion';

export default function KeywordAnalysis({ keywordGaps = [], keywordScore = 0, quantificationScore = 0, trendingKeywords = [], domain = '' }) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 rounded-2xl backdrop-blur-xl bg-white/5 border border-white/10"
    >
      <h2 className="text-2xl font-bold mb-6 bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
        🔍 Keyword Gap Analysis
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span className="text-gray-300">Keyword Density Score</span>
            <span className="text-white font-bold">{keywordScore}/100</span>
          </div>
          <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: `${keywordScore}%` }}
              transition={{ duration: 1 }}
              className="h-full bg-gradient-to-r from-cyan-400 to-blue-500"
            />
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative w-12 h-12 shrink-0">
            <svg className="w-full h-full transform -rotate-90">
              <circle cx="24" cy="24" r="20" stroke="currentColor" strokeWidth="4" fill="transparent" className="text-gray-700" />
              <motion.circle cx="24" cy="24" r="20" stroke="currentColor" strokeWidth="4" fill="transparent"
                strokeDasharray={125.6}
                initial={{ strokeDashoffset: 125.6 }}
                animate={{ strokeDashoffset: 125.6 - (quantificationScore / 100) * 125.6 }}
                className="text-amber-400"
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center text-xs font-bold text-white">
              {quantificationScore}%
            </div>
          </div>
          <div className="text-sm">
            <h4 className="font-medium text-amber-400">Add Metrics</h4>
            <p className="text-gray-400 text-xs mt-1">Only {quantificationScore}% of your bullets include measurable results. Add numbers like percentages, counts, or timelines.</p>
          </div>
        </div>
      </div>

      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-300 mb-3">Missing Keywords</h3>
        {keywordGaps.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {keywordGaps.map((kw, idx) => (
              <motion.span
                key={kw}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.05 }}
                className="px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-sm animate-pulse"
              >
                {kw}
              </motion.span>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-400">No major keyword gaps found.</p>
        )}
      </div>

      <div>
        <h3 className="text-sm font-medium text-gray-300 mb-3">Trending Keywords for {domain || 'your domain'}</h3>
        <div className="flex flex-wrap gap-2">
          {trendingKeywords.map((kw, idx) => (
            <motion.span
              key={kw}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: idx * 0.05 }}
              className="px-3 py-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-sm"
            >
              {kw}
            </motion.span>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
