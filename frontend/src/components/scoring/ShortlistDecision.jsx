import { motion } from 'framer-motion'
import { CheckCircle2, AlertTriangle, XOctagon } from 'lucide-react'

export default function ShortlistDecision({ decision, score }) {
  const config = {
    SHORTLIST: {
      color: 'emerald',
      icon: CheckCircle2,
      bg: 'bg-emerald-500/20',
      border: 'border-emerald-500/50',
      text: 'text-emerald-400',
      shadow: 'shadow-[0_0_30px_rgba(16,185,129,0.3)]',
      rec: 'Highly recommended for next interview rounds.'
    },
    REVIEW: {
      color: 'amber',
      icon: AlertTriangle,
      bg: 'bg-amber-500/20',
      border: 'border-amber-500/50',
      text: 'text-amber-400',
      shadow: 'shadow-[0_0_30px_rgba(245,158,11,0.3)]',
      rec: 'Proceed with caution. Verify soft skills.'
    },
    REJECT: {
      color: 'red',
      icon: XOctagon,
      bg: 'bg-red-500/20',
      border: 'border-red-500/50',
      text: 'text-red-400',
      shadow: 'shadow-[0_0_30px_rgba(239,68,68,0.3)]',
      rec: 'Does not meet minimum role requirements.'
    }
  }

  const current = config[decision] || config.REVIEW
  const Icon = current.icon

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-6 h-full flex flex-col items-center justify-center text-center"
    >
      <h3 className="text-sm font-medium text-slate-400 mb-6 uppercase tracking-wider">AI Recommendation</h3>
      
      <motion.div 
        animate={{ 
          boxShadow: ['0 0 0px rgba(0,0,0,0)', current.shadow, '0 0 0px rgba(0,0,0,0)']
        }}
        transition={{ duration: 2, repeat: Infinity }}
        className={`w-32 h-32 rounded-full ${current.bg} ${current.border} border-2 flex flex-col items-center justify-center mb-6`}
      >
        <Icon size={40} className={`${current.text} mb-2`} />
        <span className={`font-outfit font-bold tracking-wide ${current.text}`}>
          {decision}
        </span>
      </motion.div>

      <p className="text-slate-300 text-sm mb-8 px-4">
        {current.rec}
      </p>

      <div className="w-full bg-black/20 rounded-xl p-4 text-xs">
        <div className="flex justify-between items-center mb-2 pb-2 border-b border-white/5">
          <span className="text-slate-400">Score &gt; 75</span>
          <span className="text-emerald-400 font-medium">Shortlist</span>
        </div>
        <div className="flex justify-between items-center mb-2 pb-2 border-b border-white/5">
          <span className="text-slate-400">Score 50-75</span>
          <span className="text-amber-400 font-medium">Review</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-slate-400">Score &lt; 50</span>
          <span className="text-red-400 font-medium">Reject</span>
        </div>
      </div>
    </motion.div>
  )
}
