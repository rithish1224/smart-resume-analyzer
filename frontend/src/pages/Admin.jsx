import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Activity, Users, Target, ShieldCheck, Cpu } from 'lucide-react'
import DemoDataBanner from '../components/common/DemoDataBanner'

export default function Admin() {
  const [stats, setStats] = useState(null)
  const [analyses, setAnalyses] = useState([])
  const [modelInfo, setModelInfo] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Mocking API calls for now
    setTimeout(() => {
      setStats({ totalAnalyses: 1245, totalCandidates: 892, avgScore: 68.4, shortlistRate: 24.5 })
      setModelInfo({ version: 'v2.4.1', trainingDate: '2026-07-15', ndcgScore: 0.92, profilesCount: 15420 })
      setAnalyses([
        { id: 'AN-1001', name: 'Alex Johnson', role: 'Frontend Eng', score: 82, decision: 'SHORTLIST', date: '2026-08-01' },
        { id: 'AN-1002', name: 'Maria Garcia', role: 'Data Scientist', score: 65, decision: 'REVIEW', date: '2026-08-02' },
        { id: 'AN-1003', name: 'James Smith', role: 'Backend Eng', score: 45, decision: 'REJECT', date: '2026-08-02' }
      ])
      setIsLoading(false)
    }, 1000)
  }, [])

  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } }
  }

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  }

  if (isLoading) {
    return (
      <div className="p-8 flex justify-center items-center h-[calc(100vh-64px)]">
        <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    )
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <DemoDataBanner />
        <h1 className="text-3xl font-outfit font-bold text-white mb-2">Admin Dashboard</h1>
        <p className="text-slate-400">System overview and analytics.</p>
      </motion.div>

      <motion.div variants={container} initial="hidden" animate="show" className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {[
          { label: 'Total Analyses', value: stats.totalAnalyses, icon: Activity, color: 'text-indigo-400' },
          { label: 'Total Candidates', value: stats.totalCandidates, icon: Users, color: 'text-cyan-400' },
          { label: 'Avg Score', value: `${stats.avgScore}%`, icon: Target, color: 'text-violet-400' },
          { label: 'Shortlist Rate', value: `${stats.shortlistRate}%`, icon: ShieldCheck, color: 'text-emerald-400' }
        ].map((stat, i) => (
          <motion.div key={i} variants={item} className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6 relative overflow-hidden">
            <div className={`absolute top-0 right-0 p-4 opacity-10 ${stat.color}`}>
              <stat.icon size={64} />
            </div>
            <div className={`w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center mb-4 ${stat.color}`}>
              <stat.icon size={20} />
            </div>
            <p className="text-slate-400 text-sm font-medium mb-1">{stat.label}</p>
            <p className="text-3xl font-outfit font-bold text-white">{stat.value}</p>
          </motion.div>
        ))}
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div variants={item} className="lg:col-span-2 backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
          <h2 className="text-xl font-outfit font-bold mb-6 flex items-center gap-2">
            <Activity className="text-indigo-400" size={20} />
            Recent Analyses
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="text-slate-400 border-b border-white/10">
                  <th className="pb-3 font-medium">ID</th>
                  <th className="pb-3 font-medium">Candidate</th>
                  <th className="pb-3 font-medium">Role</th>
                  <th className="pb-3 font-medium">Score</th>
                  <th className="pb-3 font-medium">Decision</th>
                  <th className="pb-3 font-medium">Date</th>
                </tr>
              </thead>
              <tbody>
                {analyses.map((analysis) => (
                  <tr key={analysis.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-4 text-slate-400">{analysis.id}</td>
                    <td className="py-4 font-medium text-white">{analysis.name}</td>
                    <td className="py-4 text-slate-300">{analysis.role}</td>
                    <td className="py-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${analysis.score >= 75 ? 'bg-emerald-500/20 text-emerald-400' : analysis.score >= 50 ? 'bg-amber-500/20 text-amber-400' : 'bg-red-500/20 text-red-400'}`}>
                        {analysis.score}%
                      </span>
                    </td>
                    <td className="py-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${analysis.decision === 'SHORTLIST' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : analysis.decision === 'REVIEW' ? 'bg-amber-500/10 border-amber-500/20 text-amber-400' : 'bg-red-500/10 border-red-500/20 text-red-400'}`}>
                        {analysis.decision}
                      </span>
                    </td>
                    <td className="py-4 text-slate-400">{analysis.date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>

        <div className="space-y-6">
          <motion.div variants={item} className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
            <h2 className="text-xl font-outfit font-bold mb-6 flex items-center gap-2">
              <Cpu className="text-cyan-400" size={20} />
              Model Information
            </h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center pb-4 border-b border-white/5">
                <span className="text-slate-400 text-sm">Version</span>
                <span className="font-medium text-white px-2 py-1 bg-indigo-500/20 text-indigo-400 rounded text-sm">{modelInfo.version}</span>
              </div>
              <div className="flex justify-between items-center pb-4 border-b border-white/5">
                <span className="text-slate-400 text-sm">Training Date</span>
                <span className="font-medium text-white">{modelInfo.trainingDate}</span>
              </div>
              <div className="flex justify-between items-center pb-4 border-b border-white/5">
                <span className="text-slate-400 text-sm">NDCG Score</span>
                <span className="font-medium text-white">{modelInfo.ndcgScore}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400 text-sm">Training Profiles</span>
                <span className="font-medium text-white">{modelInfo.profilesCount.toLocaleString()}</span>
              </div>
            </div>
          </motion.div>

          <motion.div variants={item} className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
            <h2 className="text-xl font-outfit font-bold mb-6">AI Providers</h2>
            <div className="space-y-4">
              {['OpenAI', 'Anthropic', 'Gemini'].map((provider) => (
                <div key={provider} className="flex items-center justify-between">
                  <span className="text-slate-300 font-medium">{provider}</span>
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span className="text-xs text-emerald-400">Operational</span>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
