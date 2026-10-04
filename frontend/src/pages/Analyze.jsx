import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { FileText, Loader2, UploadCloud, CheckCircle2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { analyzeApi } from '../api/client'

function SkillChip({ children, missing }) {
  return <span className={`rounded-full border px-2.5 py-1 text-xs ${missing ? 'border-white/[.08] bg-white/[.04] text-gray-400' : 'border-green-500/20 bg-green-500/10 text-green-300'}`}>{children}</span>
}

function RequirementChecks({ coverage, skillCoverage }) {
  if (!coverage) return null
  const experienceKnown = coverage.years_required != null && coverage.years_candidate != null
  const educationKnown = coverage.degree_required != null && coverage.degree_found != null && coverage.degree_met != null
  const row = (label, text, state) => <div className="flex items-center justify-between gap-3 text-sm"><span className="text-gray-400">{label}</span><span className={state === 'met' ? 'text-green-300' : state === 'below' ? 'text-amber-300' : 'text-gray-500'}>{state === 'met' ? '✓ ' : state === 'below' ? '⚠ ' : ''}{text}</span></div>
  const degreeName = value => value >= 3 ? "Master's" : value >= 2 ? "Bachelor's" : 'Diploma'
  return <div className="mt-5 space-y-2 border-t border-white/[.07] pt-4">
    <div className="flex items-center justify-between gap-3 text-sm"><span className="text-gray-400">Skills</span><span className="text-gray-300">{(coverage.skill_coverage ?? skillCoverage) == null ? 'Not enough information' : `${coverage.skill_coverage ?? skillCoverage}%`}</span></div>
    {row('Experience:', experienceKnown ? `${coverage.years_candidate} yrs vs ${coverage.years_required}+ required (${coverage.years_met ? 'Met' : 'Below'})` : 'Not enough information', experienceKnown ? (coverage.years_met ? 'met' : 'below') : 'unknown')}
    {row('Education:', educationKnown ? `${degreeName(coverage.degree_required)} required, ${degreeName(coverage.degree_found)} found (${coverage.degree_met ? 'Met' : 'Below'})` : 'Not enough information', educationKnown ? (coverage.degree_met ? 'met' : 'below') : 'unknown')}
    <p className="pt-2 text-xs text-gray-500">Overall match combines skills (70%), experience (20%) and education (10%). Parts that could not be found are left out.</p>
  </div>
}

export function ResultCard({ result, onReset }) {
  const coverage = result.skill_coverage
  const overallMatch = result.overall_match_percent ?? result.skill_coverage
  return <section className="surface p-6">
    <div className="flex flex-wrap items-start justify-between gap-4">
      <div><p className="text-xs uppercase tracking-[.18em] text-gray-500">Analysis result</p><h2 className="mt-2 text-2xl font-semibold">{result.match_level || 'Review match'}</h2></div>
      <div className="text-right"><strong className="text-3xl">{overallMatch == null ? '—' : `${overallMatch}%`}</strong><p className="text-xs text-gray-500">overall match</p></div>
    </div>
    {coverage !== null && <div className="mt-6 h-2 overflow-hidden rounded-full bg-white/[.08]"><div className="h-full rounded-full bg-gradient-to-r from-[#8b3dff] to-[#e040c0]" style={{ width: `${coverage}%` }} /></div>}
    <RequirementChecks coverage={result.requirement_coverage} skillCoverage={result.skill_coverage} />
    <div className="mt-6 grid gap-5 md:grid-cols-2">
      <div><p className="mb-3 text-xs font-medium uppercase tracking-wider text-gray-500">Matched skills</p><div className="flex flex-wrap gap-2">{(result.matched_skills || []).length ? result.matched_skills.map(skill => <SkillChip key={skill}>{skill}</SkillChip>) : <span className="text-sm text-gray-500">None recognized</span>}</div></div>
      <div><p className="mb-3 text-xs font-medium uppercase tracking-wider text-gray-500">Missing skills</p><div className="flex flex-wrap gap-2">{(result.missing_skills || []).length ? result.missing_skills.map(skill => <SkillChip key={skill} missing>{skill}</SkillChip>) : <span className="text-sm text-gray-500">None recognized</span>}</div></div>
    </div>
    <p className="mt-6 border-t border-white/[.07] pt-4 text-sm text-gray-300">{result.summary}</p>
    {result.rank && <p className="mt-3 text-sm text-gray-400">Rank {result.rank} · Relative score {result.relative_score}/100</p>}
    <p className="mt-6 text-xs leading-5 text-gray-500">Assistive analysis only. Not a hiring decision. A human must review.</p>
    <div className="no-print mt-5 flex flex-wrap gap-4 text-sm"><button type="button" onClick={onReset} className="rounded-lg border border-white/[.1] px-3 py-2 text-gray-300 hover:bg-white/[.05]">Analyze another</button>{result.report_id && <Link to={`/history/${result.report_id}`} className="px-3 py-2 text-[#c084fc] hover:text-white">View in history</Link>}</div>
  </section>
}

export default function Analyze() {
  const [file, setFile] = useState(null)
  const [role, setRole] = useState('')
  const [jd, setJd] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const resultRef = useRef(null)
  useEffect(() => { if (result) resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }) }, [result])
  const reset = () => { setFile(null); setRole(''); setJd(''); setResult(null); setError('') }
  const chooseFile = event => {
    const selected = event.target.files?.[0]
    if (!selected) return
    const allowed = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'image/jpeg', 'image/png']
    if (selected.size > 1048576) { setError('File too large. Maximum size is 1 MB.'); setFile(null); return }
    if (!allowed.includes(selected.type)) { setError('Unsupported file type. Use PDF, DOCX, TXT, JPG, or PNG.'); setFile(null); return }
    setError(''); setFile(selected)
  }

  const submit = async (event) => {
    event.preventDefault()
    if (!file || !jd.trim()) { setError('Add a resume and job description to continue.'); return }
    setLoading(true); setError('')
    try {
      const response = await analyzeApi.analyze(file, jd, role)
      setResult(response.data)
    } catch (err) {
      const message = err.response?.data?.detail || 'Analysis failed. Please try again.'
      setError(message); toast.error(message)
    } finally { setLoading(false) }
  }

  return <main className="mx-auto max-w-6xl px-6 py-10 md:px-10">
    <header className="mb-8"><p className="text-sm text-[#c084fc]">Resume analysis</p><h1 className="mt-2 text-4xl font-bold tracking-tight">Understand the match.</h1><p className="mt-3 max-w-2xl text-gray-400">Upload one resume and compare its evidence with the role requirements.</p></header>
    <form onSubmit={submit} className="grid gap-5 lg:grid-cols-[.9fr_1.1fr]">
      <section className="surface p-6">
        <label className="mb-3 block text-sm font-medium">Resume</label>
        <label className="flex min-h-64 cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed border-white/[.15] bg-white/[.02] px-6 text-center hover:border-[#9b2cff]/70">
          <input className="sr-only" type="file" accept=".pdf,.docx,.txt,.jpg,.jpeg,.png" onChange={chooseFile} />
          {file ? <><CheckCircle2 className="mb-3 text-green-400" size={32} /><span className="text-sm">{file.name}</span><span className="mt-1 text-xs text-gray-500">Ready to analyze</span><span className="mt-4 flex gap-3 text-xs"><button type="button" onClick={event => { event.preventDefault(); event.currentTarget.closest('label').querySelector('input').click() }} className="text-[#c084fc]">Replace</button><button type="button" onClick={event => { event.preventDefault(); setFile(null) }} className="text-gray-400">Remove</button></span></> : <><UploadCloud className="mb-3 text-[#c084fc]" size={32} /><span className="text-sm">Drop a resume here or browse</span><span className="mt-1 text-xs text-gray-500">PDF, DOCX, TXT, JPG, PNG · max 1 MB</span></>}
        </label>
      </section>
      <section className="surface p-6">
        <label className="mb-2 block text-sm font-medium" htmlFor="role">Target role <span className="text-gray-500">(optional)</span></label>
        <input id="role" spellCheck={false} className="field mb-5 px-4 py-3 text-sm" value={role} onChange={event => setRole(event.target.value)} placeholder="e.g. Backend Engineer" />
        <label className="mb-2 block text-sm font-medium" htmlFor="jd">Job description</label>
        <textarea id="jd" spellCheck={false} className="field min-h-44 resize-y px-4 py-3 text-sm" value={jd} onChange={event => setJd(event.target.value)} placeholder="Paste the job description here..." required />
        {error && <p className="mt-3 text-sm text-red-300">{error}</p>}
        <button className="primary-button mt-5 flex w-full items-center justify-center gap-2 rounded-xl px-4 py-3 font-medium disabled:cursor-not-allowed disabled:opacity-60" disabled={loading || !file || !jd.trim()}>{loading ? <><Loader2 className="animate-spin" size={18} /> Analyzing...</> : <><FileText size={18} /> Analyze resume</>}</button>
      </section>
    </form>
    {result && <div ref={resultRef} className="mt-6"><ResultCard result={result} onReset={reset} /></div>}
  </main>
}
