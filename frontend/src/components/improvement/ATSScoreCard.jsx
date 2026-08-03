import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export default function ATSScoreCard({ atsScore = 0, passRateEstimate = 'Low Chance', issues = [] }) {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    let start = 0;
    const end = parseInt(atsScore, 10);
    if (start === end) return;
    const duration = 1000;
    let startTimestamp = null;
    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      setAnimatedScore(Math.floor(progress * end));
      if (progress < 1) {
        window.requestAnimationFrame(step);
      }
    };
    window.requestAnimationFrame(step);
  }, [atsScore]);

  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (animatedScore / 100) * circumference;

  let badgeColor = 'bg-red-500/20 text-red-400 border-red-500/30';
  if (atsScore > 80) badgeColor = 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
  else if (atsScore > 50) badgeColor = 'bg-amber-500/20 text-amber-400 border-amber-500/30';

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 rounded-2xl backdrop-blur-xl bg-white/5 border border-white/10 h-full flex flex-col items-center"
    >
      <h3 className="text-lg font-semibold text-gray-200 mb-6 w-full text-left">ATS Friendliness</h3>
      
      <div className="relative w-32 h-32 mb-4">
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="64"
            cy="64"
            r={radius}
            stroke="currentColor"
            strokeWidth="8"
            fill="transparent"
            className="text-gray-700"
          />
          <motion.circle
            cx="64"
            cy="64"
            r={radius}
            stroke="currentColor"
            strokeWidth="8"
            fill="transparent"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1, ease: "easeOut" }}
            className="text-cyan-400"
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold text-white">{animatedScore}</span>
        </div>
      </div>

      <div className={`px-3 py-1 rounded-full border text-sm font-medium mb-6 ${badgeColor}`}>
        {passRateEstimate}
      </div>

      <div className="w-full mt-auto">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Identified Issues</h4>
        {issues.length > 0 ? (
          <ul className="space-y-2">
            {issues.map((issue, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                <span className="text-red-400 mt-0.5">❌</span>
                <span>{issue}</span>
              </li>
            ))}
          </ul>
        ) : (
          <div className="flex items-center gap-2 text-emerald-400 font-medium bg-emerald-500/10 p-3 rounded-lg border border-emerald-500/20">
            <span>✅</span> ATS-Ready
          </div>
        )}
      </div>
    </motion.div>
  );
}
