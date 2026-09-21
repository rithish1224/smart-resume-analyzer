import { motion } from 'framer-motion'

export default function SkillGapChart({ matchedSkills = [], missingSkills = [], relatedSkills = [] }) {
  const groups = [
    ['Matched skills', matchedSkills, 'text-emerald-300', 'bg-emerald-500/15 border-emerald-500/30'],
    ['Missing skills', missingSkills, 'text-red-300', 'bg-red-500/15 border-red-500/30'],
    ['Related / learning skills', relatedSkills, 'text-amber-300', 'bg-amber-500/15 border-amber-500/30'],
  ]

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-6 h-full flex flex-col"
    >
      <h3 className="text-lg font-outfit font-bold text-white mb-2">Skill Gap Analysis</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {groups.map(([label, skills, textColor, background]) => (
          <div key={label} className={`rounded-xl border p-4 ${background}`}>
            <div className={`flex justify-between text-sm font-semibold ${textColor}`}>
              <span>{label}</span><span>{skills.length}</span>
            </div>
            <div className="flex flex-wrap gap-2 mt-3">
              {skills.length ? skills.map(skill => (
                <span key={skill} className="px-2 py-1 rounded-full bg-black/20 text-xs text-slate-200">{skill}</span>
              )) : <span className="text-xs text-slate-400">None reported</span>}
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  )
}
