import { Link } from 'react-router-dom'
import { ArrowRight, CheckCircle2, FileSearch, ShieldCheck, Sparkles } from 'lucide-react'

export default function Home() {
  return (
    <div className="app-shell min-h-screen px-6 py-24">
      <div className="mx-auto max-w-6xl">
        <div className="max-w-3xl pt-16">
          <span className="mb-6 inline-flex items-center gap-2 rounded-full border border-[#9b2cff]/30 bg-[#9b2cff]/10 px-3 py-1.5 text-xs text-[#d5a9ff]"><Sparkles size={14} /> Resume intelligence for human review</span>
          <h1 className="text-5xl font-bold leading-[1.05] tracking-tight md:text-7xl">Match people to roles with <span className="bg-gradient-to-r from-[#8b3dff] to-[#e040c0] bg-clip-text text-transparent">clarity.</span></h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-gray-400">Analyze resume evidence against a job description, understand skill coverage, and keep every decision with a human reviewer.</p>
          <div className="mt-9 flex flex-wrap gap-3"><Link to="/analyze" className="primary-button inline-flex items-center gap-2 rounded-xl px-5 py-3 font-medium">Analyze a resume <ArrowRight size={18} /></Link><a href="#how-it-works" className="rounded-xl border border-white/[.1] px-5 py-3 text-gray-300 hover:bg-white/[.05]">Learn how it works</a></div>
        </div>
        <section id="how-it-works" className="mx-auto mt-24 max-w-6xl scroll-mt-8">
          <p className="text-sm text-[#c084fc]">How it works</p><h2 className="mt-2 text-3xl font-bold">A clear review flow.</h2>
          <div className="mt-7 grid gap-4 md:grid-cols-3">{['Upload a resume', 'Paste the job description', 'Review skill coverage and missing skills'].map((step, index) => <div className="surface p-6" key={step}><span className="text-sm text-[#c084fc]">0{index + 1}</span><h3 className="mt-5 font-semibold">{step}</h3></div>)}</div>
        </section>
        <footer className="mx-auto mt-24 flex max-w-6xl flex-wrap justify-between gap-3 border-t border-white/[.08] pt-6 text-xs text-gray-500"><span>© 2026 Skillora</span><span>Assistive analysis only. Not a hiring decision.</span></footer>
        <div className="mt-20 grid gap-4 md:grid-cols-3">
          {[
            [FileSearch, 'Evidence first', 'See matched and missing skills instead of opaque labels.'],
            [CheckCircle2, 'Relative ranking', 'Compare candidates for the same role when you need to.'],
            [ShieldCheck, 'Human-led', 'Assistive analysis only. Review the evidence before acting.'],
          ].map(([Icon, title, text]) => <div className="surface p-6" key={title}><Icon className="mb-5 text-[#c084fc]" size={22} /><h2 className="font-semibold">{title}</h2><p className="mt-2 text-sm leading-6 text-gray-400">{text}</p></div>)}
        </div>
      </div>
    </div>
  )
}
