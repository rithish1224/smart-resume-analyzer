import { motion } from 'framer-motion'

export default function SkillGapChart({ skillGaps }) {
  // Sort by priority (High -> Med -> Low)
  const priorityWeight = { 'High': 3, 'Med': 2, 'Low': 1 }
  const sortedGaps = [...skillGaps].sort((a, b) => priorityWeight[b.priority] - priorityWeight[a.priority])

  const stats = {
    hardGaps: skillGaps.filter(g => g.status === 'hard').length,
    softGaps: skillGaps.filter(g => g.status === 'soft').length,
    met: skillGaps.filter(g => g.status === 'met').length
  }

  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } }
  }

  const item = {
    hidden: { opacity: 0, x: -20 },
    show: { opacity: 1, x: 0 }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'met': return 'bg-emerald-500'
      case 'soft': return 'bg-amber-500'
      case 'hard': return 'bg-red-500'
      default: return 'bg-slate-500'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'met': return '✅'
      case 'soft': return '⚠️'
      case 'hard': return '❌'
      default: return '➖'
    }
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-6 h-full flex flex-col"
    >
      <h3 className="text-lg font-outfit font-bold text-white mb-2">Skill Gap Analysis</h3>
      
      <div className="flex gap-4 text-xs font-medium text-slate-300 bg-white/5 p-3 rounded-xl mb-6">
        <span className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-red-500"/> {stats.hardGaps} Hard Gaps</span>
        <span className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-amber-500"/> {stats.softGaps} Soft Gaps</span>
        <span className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-emerald-500"/> {stats.met} Skills Met</span>
      </div>

      <motion.div variants={container} initial="hidden" animate="show" className="space-y-5 overflow-y-auto pr-2 custom-scrollbar flex-1">
        {sortedGaps.map((skill, idx) => (
          <motion.div key={idx} variants={item} className="w-full">
            <div className="flex justify-between items-center mb-1.5 text-sm">
              <span className="font-medium text-slate-200 flex items-center gap-2">
                {getStatusIcon(skill.status)} {skill.skillName}
              </span>
              <span className={`text-[10px] px-2 py-0.5 rounded border font-semibold ${
                skill.priority === 'High' ? 'bg-red-500/10 border-red-500/30 text-red-400' :
                skill.priority === 'Med' ? 'bg-amber-500/10 border-amber-500/30 text-amber-400' :
                'bg-slate-500/10 border-slate-500/30 text-slate-400'
              }`}>
                {skill.priority} Priority
              </span>
            </div>
            <div className="h-2 w-full bg-white/10 rounded-full overflow-hidden relative">
              {/* Background represents required level (100% width, just a visual guide) */}
              
              {/* Foreground represents candidate level */}
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: `${(skill.candidateLevel / skill.requiredLevel) * 100}%` }}
                transition={{ duration: 1, ease: "easeOut" }}
                className={`absolute top-0 left-0 h-full rounded-full ${getStatusColor(skill.status)}`}
                style={{ maxWidth: '100%' }}
              />
            </div>
          </motion.div>
        ))}
      </motion.div>
    </motion.div>
  )
}
