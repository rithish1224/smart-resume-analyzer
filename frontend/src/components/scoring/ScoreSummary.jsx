import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { getMatchBand } from '../../config/decisionBands'

export default function ScoreSummary({ score, modelVersion }) {
  const [displayScore, setDisplayScore] = useState(0)

  useEffect(() => {
    let startTimestamp = null
    const duration = 1500 // 1.5 seconds

    const step = (timestamp) => {
      if (!startTimestamp) startTimestamp = timestamp
      const progress = Math.min((timestamp - startTimestamp) / duration, 1)
      
      // Easing function (easeOutExpo)
      const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress)
      
      setDisplayScore(Math.floor(easeProgress * score))
      
      if (progress < 1) {
        window.requestAnimationFrame(step)
      }
    }

    window.requestAnimationFrame(step)
  }, [score])

  const getColorClass = (val) => {
    if (val >= 75) return 'text-emerald-400 stroke-emerald-400'
    if (val >= 50) return 'text-amber-400 stroke-amber-400'
    return 'text-red-400 stroke-red-400'
  }

  const radius = 80
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (score / 100) * circumference
  const colorClass = getColorClass(score)

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-8 flex flex-col items-center relative overflow-hidden h-full"
    >
      <h3 className="text-lg font-outfit font-medium text-slate-300 mb-6">Overall Competency Score</h3>
      
      <div className="relative w-48 h-48 mb-6 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 200 200">
          {/* Background circle */}
          <circle
            cx="100"
            cy="100"
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth="10"
            className="text-white/10"
          />
          {/* Progress circle */}
          <motion.circle
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            cx="100"
            cy="100"
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circumference}
            className={colorClass.split(' ')[1]}
          />
        </svg>
        
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-5xl font-outfit font-bold ${colorClass.split(' ')[0]}`}>
            {displayScore}
          </span>
          <span className="text-slate-400 text-sm mt-1">out of 100</span>
        </div>
      </div>

      <div className="flex flex-col items-center gap-4">
        <div className="px-4 py-2 rounded-full border border-white/10 bg-white/5 text-slate-200 font-bold text-sm">
          Match band: {getMatchBand(score)}
        </div>
        <div className="text-xs text-slate-500 font-medium text-center">
          Decision support only; human review required.
        </div>
      </div>

      <div className="absolute bottom-4 right-4">
        <span className="text-[10px] px-2 py-1 bg-white/5 text-slate-500 rounded-full font-mono">
          {modelVersion}
        </span>
      </div>
    </motion.div>
  )
}
