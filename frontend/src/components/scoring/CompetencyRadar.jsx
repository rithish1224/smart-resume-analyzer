import { motion } from 'framer-motion'
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, Radar, Legend } from 'recharts'

export default function CompetencyRadar({ competencyScores, requiredScores }) {
  const data = [
    { subject: 'Technical', A: competencyScores.technical || 0, B: requiredScores.technical || 0 },
    { subject: 'Experience', A: competencyScores.experience || 0, B: requiredScores.experience || 0 },
    { subject: 'Education', A: competencyScores.education || 0, B: requiredScores.education || 0 },
    { subject: 'Projects', A: competencyScores.projects || 0, B: requiredScores.projects || 0 },
    { subject: 'Certifications', A: competencyScores.certifications || 0, B: requiredScores.certifications || 0 },
    { subject: 'Communication', A: competencyScores.communication || 0, B: requiredScores.communication || 0 }
  ]

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-6 h-full flex flex-col"
    >
      <h3 className="text-lg font-outfit font-bold bg-gradient-to-r from-indigo-400 to-cyan-400 text-transparent bg-clip-text mb-2">
        Competency Breakdown
      </h3>
      <p className="text-sm text-slate-400 mb-6">Candidate profile vs Role requirements</p>
      
      <div className="flex-1 w-full min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="70%" data={data}>
            <PolarGrid stroke="rgba(255,255,255,0.1)" />
            <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <Radar
              name="Candidate"
              dataKey="A"
              stroke="#6366f1"
              strokeWidth={2}
              fill="#6366f1"
              fillOpacity={0.4}
            />
            <Radar
              name="Required"
              dataKey="B"
              stroke="#06b6d4"
              strokeWidth={2}
              strokeDasharray="4 4"
              fill="none"
            />
            <Legend wrapperStyle={{ paddingTop: '20px', fontSize: '12px', color: '#cbd5e1' }} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  )
}
