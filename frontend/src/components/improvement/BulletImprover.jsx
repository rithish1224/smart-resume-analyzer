import React from 'react';
import { motion } from 'framer-motion';

export default function BulletImprover({ bulletScore = 0, weakBullets = [], strongRewrites = [] }) {
  const verbs = ['Developed', 'Implemented', 'Optimized', 'Architected', 'Spearheaded', 'Engineered', 'Streamlined', 'Pioneered'];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 rounded-2xl backdrop-blur-xl bg-white/5 border border-white/10"
    >
      <h2 className="text-2xl font-bold mb-6 bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
        💬 Bullet Point Optimizer
      </h2>

      <div className="mb-8">
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-300">Overall Bullet Quality</span>
          <span className="text-white font-bold">{bulletScore}/100</span>
        </div>
        <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: `${bulletScore}%` }}
            transition={{ duration: 1 }}
            className="h-full bg-gradient-to-r from-indigo-500 to-violet-500"
          />
        </div>
      </div>

      <div className="mb-8">
        <h3 className="text-lg font-medium text-gray-200 mb-4">Weak Bullets Found</h3>
        {weakBullets.length > 0 ? (
          <div className="space-y-6">
            {weakBullets.map((bullet, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="space-y-3"
              >
                <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-gray-300 text-sm flex gap-3">
                  <span className="text-red-400 shrink-0">⚠️</span>
                  <p>{bullet}</p>
                </div>
                {strongRewrites[idx] && (
                  <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-gray-200 text-sm ml-6 relative before:absolute before:-left-4 before:top-4 before:w-4 before:h-px before:bg-emerald-500/30">
                    <p className="font-medium mb-1">Suggested Rewrite:</p>
                    <p className="mb-2">{strongRewrites[idx].text}</p>
                    <p className="text-xs text-emerald-400/80 italic">{strongRewrites[idx].reason}</p>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-medium">
            ✅ All bullets look strong!
          </div>
        )}
      </div>

      <div>
        <h3 className="text-sm font-medium text-gray-400 mb-3">Strong Action Verbs to Use</h3>
        <div className="flex flex-wrap gap-2">
          {verbs.map(verb => (
            <motion.span
              key={verb}
              whileHover={{ scale: 1.05 }}
              className="px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs cursor-pointer hover:bg-indigo-500/20"
            >
              {verb}
            </motion.span>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
