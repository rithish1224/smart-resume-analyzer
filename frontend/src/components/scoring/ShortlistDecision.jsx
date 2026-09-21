import { motion } from 'framer-motion'

export default function ShortlistDecision() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-3xl p-6 h-full flex flex-col items-center justify-center text-center"
    >
      <h3 className="text-sm font-medium text-slate-400 mb-6 uppercase tracking-wider">
        Decision support
      </h3>
      <div className="w-full rounded-2xl bg-white/5 border border-white/10 p-6">
        <p className="text-slate-200 font-semibold">Human review required</p>
        <p className="text-slate-400 text-sm mt-2">
          This model supports review and does not make hiring decisions.
        </p>
      </div>
    </motion.div>
  )
}
