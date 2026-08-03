import { motion } from 'framer-motion'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ReferenceLine } from 'recharts'
import { TrendingUp, TrendingDown } from 'lucide-react'

export default function ShapExplainer({ shapData }) {
  const chartData = shapData.features.map(f => ({
    name: f.name,
    value: f.contribution,
    color: f.contribution >= 0 ? '#6366f1' : '#ef4444' // indigo for positive, red for negative
  })).sort((a, b) => Math.abs(b.value) - Math.abs(a.value))

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-[#0f0f2e] border border-white/10 p-3 rounded-lg shadow-xl">
          <p className="text-sm font-medium text-white mb-1">{data.name}</p>
          <p className={`text-xs font-bold ${data.value >= 0 ? 'text-indigo-400' : 'text-red-400'}`}>
            Impact: {data.value > 0 ? '+' : ''}{data.value.toFixed(2)}%
          </p>
        </div>
      )
    }
    return null
  }

  const positiveFactors = shapData.features.filter(f => f.contribution > 0).sort((a, b) => b.contribution - a.contribution).slice(0, 3)
  const negativeFactors = shapData.features.filter(f => f.contribution < 0).sort((a, b) => a.contribution - b.contribution).slice(0, 3)

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-6 lg:p-8"
    >
      <h3 className="text-xl font-outfit font-bold bg-gradient-to-r from-violet-400 to-indigo-400 text-transparent bg-clip-text mb-6 flex items-center gap-2">
        <span>🔍</span> SHAP Explanation
      </h3>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <h4 className="text-sm font-medium text-slate-300 mb-4">Feature Contributions</h4>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: '#cbd5e1', fontSize: 11 }} width={100} />
                <Tooltip cursor={{ fill: 'rgba(255,255,255,0.05)' }} content={<CustomTooltip />} />
                <ReferenceLine x={0} stroke="rgba(255,255,255,0.2)" />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="space-y-6">
          <div>
            <h4 className="text-sm font-medium text-slate-300 mb-3 flex items-center gap-2">
              <TrendingUp size={16} className="text-indigo-400" />
              🚀 Boosting Factors
            </h4>
            <div className="space-y-2">
              {positiveFactors.map((factor, idx) => (
                <div key={idx} className="bg-indigo-500/10 border border-indigo-500/20 p-3 rounded-xl flex justify-between items-start gap-4">
                  <div>
                    <span className="text-sm font-medium text-white block">{factor.name}</span>
                    <span className="text-xs text-indigo-200 mt-1 block leading-relaxed">{factor.evidence}</span>
                  </div>
                  <span className="text-xs font-bold text-indigo-400 bg-indigo-500/20 px-2 py-1 rounded whitespace-nowrap">
                    +{factor.contribution.toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          </div>

          {negativeFactors.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-slate-300 mb-3 flex items-center gap-2">
                <TrendingDown size={16} className="text-red-400" />
                ⬇️ Dragging Factors
              </h4>
              <div className="space-y-2">
                {negativeFactors.map((factor, idx) => (
                  <div key={idx} className="bg-red-500/10 border border-red-500/20 p-3 rounded-xl flex justify-between items-start gap-4">
                    <div>
                      <span className="text-sm font-medium text-white block">{factor.name}</span>
                      <span className="text-xs text-red-200 mt-1 block leading-relaxed">{factor.evidence}</span>
                    </div>
                    <span className="text-xs font-bold text-red-400 bg-red-500/20 px-2 py-1 rounded whitespace-nowrap">
                      {factor.contribution.toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="mt-8 bg-white/5 border border-white/10 p-4 rounded-xl">
        <p className="text-sm text-slate-300 leading-relaxed italic">
          "{shapData.summary}"
        </p>
      </div>
    </motion.div>
  )
}
