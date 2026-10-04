import { motion } from 'framer-motion'

function displayValue(value, suffix = '') {
  return value === null || value === undefined ? 'Not available' : `${value}${suffix}`
}

export default function RequirementCoverage({ coverage = {} }) {
  const skills = `${coverage.skills_matched ?? 0}/${coverage.skills_required ?? 0}`
  const years = `${displayValue(coverage.years_candidate)} / ${displayValue(coverage.years_required)}`
  const degree = coverage.degree_met === null || coverage.degree_met === undefined
    ? 'Not available'
    : coverage.degree_met ? 'Met' : 'Not met'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-6 h-full"
    >
      <h3 className="text-lg font-outfit font-bold text-white mb-1">Requirement coverage</h3>
      <p className="text-xs text-slate-400 mb-5">Directly extracted evidence against this job description.</p>
      <div className="space-y-4 text-sm">
        <div className="flex justify-between gap-4">
          <span className="text-slate-300">Skills</span>
          <span className="font-semibold text-emerald-300">{skills} ({displayValue(coverage.coverage_pct, '%')})</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-slate-300">Experience</span>
          <span className="font-semibold text-slate-100">{years} years; {coverage.years_met === null || coverage.years_met === undefined ? 'not comparable' : coverage.years_met ? 'requirement met' : 'requirement not met'}</span>
        </div>
        <div className="flex justify-between gap-4">
          <span className="text-slate-300">Degree</span>
          <span className="font-semibold text-slate-100">{degree}</span>
        </div>
      </div>
    </motion.div>
  )
}
