import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const DOMAINS = [
  'Software Engineer',
  'Data Analyst',
  'ML Engineer',
  'Web Developer',
  'Cybersecurity',
  'Cloud Engineer',
  'UI/UX Designer',
  'DevOps Engineer'
];

export default function CompanyTargeting({ onSubmit, isLoading, knownCompanies = [] }) {
  const [domain, setDomain] = useState(DOMAINS[0]);
  const [company, setCompany] = useState('');
  const [aiEnabled, setAiEnabled] = useState(true);
  const [showTooltip, setShowTooltip] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ domain, company, aiEnabled });
  };

  const isKnownCompany = knownCompanies.includes(company);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 rounded-2xl backdrop-blur-xl bg-white/5 border border-white/10"
    >
      <h2 className="text-2xl font-bold mb-6 bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
        🎯 Resume Targeting
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Target Domain</label>
          <motion.select
            whileHover={{ scale: 1.01 }}
            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-indigo-500 outline-none"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
          >
            {DOMAINS.map(d => <option key={d} value={d} className="bg-[#0a0a1a]">{d}</option>)}
          </motion.select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Target Company (Optional)</label>
          <div className="relative">
            <motion.input
              whileHover={{ scale: 1.01 }}
              type="text"
              placeholder="e.g. Google, Amazon..."
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-indigo-500 outline-none"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              list="known-companies"
            />
            {company && isKnownCompany && (
              <span className="absolute right-3 top-3.5 text-xl">🏢</span>
            )}
            <datalist id="known-companies">
              {knownCompanies.map(c => <option key={c} value={c} />)}
            </datalist>
          </div>
          {company && !isKnownCompany && (
            <p className="mt-2 text-sm text-amber-400/80">
              Company not in our database — will use general {domain} best practices
            </p>
          )}
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 relative">
            <label className="text-sm font-medium text-gray-300">Enable AI-Enhanced Suggestions</label>
            <button 
              type="button"
              className="text-gray-400 hover:text-white"
              onMouseEnter={() => setShowTooltip(true)}
              onMouseLeave={() => setShowTooltip(false)}
            >
              ℹ️
            </button>
            <AnimatePresence>
              {showTooltip && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="absolute left-0 bottom-6 w-64 p-3 bg-gray-900 border border-white/10 rounded-lg text-xs text-gray-300 z-10 shadow-xl"
                >
                  We analyze your resume against this company's known hiring patterns and ATS behavior
                </motion.div>
              )}
            </AnimatePresence>
          </div>
          
          <button
            type="button"
            onClick={() => setAiEnabled(!aiEnabled)}
            className={`w-12 h-6 rounded-full p-1 transition-colors ${aiEnabled ? 'bg-indigo-500' : 'bg-gray-600'}`}
          >
            <motion.div
              className="w-4 h-4 bg-white rounded-full"
              animate={{ x: aiEnabled ? 24 : 0 }}
            />
          </button>
        </div>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          disabled={isLoading}
          type="submit"
          className="w-full py-4 rounded-xl bg-gradient-to-r from-indigo-500 to-violet-600 text-white font-semibold shadow-lg shadow-indigo-500/25 disabled:opacity-50"
        >
          {isLoading ? 'Analyzing...' : 'Analyze for Improvement'}
        </motion.button>
      </form>
    </motion.div>
  );
}
