import { motion } from 'framer-motion'
import { Server, Database, Brain, Code, Cpu, Layout, Layers } from 'lucide-react'

export default function About() {
  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } }
  }

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  }

  const features = [
    "Context-Aware Skill Extraction",
    "Fuzzy Skill Matching",
    "Semantic Role Understanding",
    "Domain-Specific Ontologies",
    "Cross-Domain Transfer Matching",
    "Experience Calibration",
    "Education Normalization",
    "SHAP Explainability",
    "Bias Mitigation",
    "Automated Interview Generation"
  ]

  const techStack = [
    { name: 'XGBoost', icon: Brain, color: 'text-amber-500' },
    { name: 'SHAP', icon: Cpu, color: 'text-indigo-500' },
    { name: 'FastAPI', icon: Server, color: 'text-teal-500' },
    { name: 'React', icon: Layout, color: 'text-cyan-500' },
    { name: 'Tailwind CSS', icon: Code, color: 'text-sky-400' },
    { name: 'Framer Motion', icon: Code, color: 'text-fuchsia-500' },
    { name: 'spaCy', icon: Brain, color: 'text-blue-500' },
    { name: 'PyMuPDF', icon: Code, color: 'text-yellow-500' },
    { name: 'SQLite', icon: Database, color: 'text-blue-400' },
    { name: 'Docker', icon: Layers, color: 'text-blue-600' }
  ]

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto">
      <motion.div initial="hidden" animate="show" variants={container} className="space-y-16">
        
        {/* Hero Section */}
        <motion.div variants={item} className="text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-sm font-medium mb-6">
            <span>B.Tech CSE Final Year Project</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-outfit font-bold mb-6 bg-gradient-to-r from-indigo-400 via-violet-400 to-cyan-400 text-transparent bg-clip-text">
            Smart Competency Diagnostic
          </h1>
          <p className="text-lg text-slate-400 max-w-3xl mx-auto leading-relaxed">
            An advanced AI-driven platform for objective resume evaluation and competency scoring. 
            Leveraging NLP and ensemble machine learning to minimize hiring bias and provide explainable talent analytics.
          </p>
        </motion.div>

        {/* Architecture */}
        <motion.div variants={item} className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl" />
          <h2 className="text-2xl font-outfit font-bold mb-8 flex items-center gap-3">
            <Layers className="text-indigo-400" />
            System Architecture
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {['1. Document Ingestion & OCR', '2. NLP Entity Extraction', '3. Knowledge Graph Mapping', '4. Feature Engineering', '5. XGBoost Inference', '6. Explainability Layer'].map((layer, idx) => (
              <div key={idx} className="bg-white/5 border border-white/10 p-4 rounded-xl flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold font-outfit">
                  {idx + 1}
                </div>
                <span className="font-medium text-slate-200">{layer.split('. ')[1]}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Tech Stack */}
        <motion.div variants={item}>
          <h2 className="text-2xl font-outfit font-bold mb-8 text-center">Technology Stack</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {techStack.map((tech, idx) => (
              <div key={idx} className="backdrop-blur-md bg-white/5 border border-white/10 p-6 rounded-xl flex flex-col items-center justify-center gap-3 hover:bg-white/10 transition-colors">
                <tech.icon className={`w-8 h-8 ${tech.color}`} />
                <span className="text-sm font-medium text-slate-300">{tech.name}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Novel Features */}
        <motion.div variants={item}>
          <h2 className="text-2xl font-outfit font-bold mb-8 text-center">Novel Capabilities</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {features.map((feature, idx) => (
              <div key={idx} className="backdrop-blur-sm bg-white/5 border border-white/5 p-5 rounded-xl flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-cyan-400 mt-2 flex-shrink-0 shadow-[0_0_8px_rgba(6,182,212,0.8)]" />
                <span className="text-slate-300 leading-snug">{feature}</span>
              </div>
            ))}
          </div>
        </motion.div>

      </motion.div>
    </div>
  )
}
