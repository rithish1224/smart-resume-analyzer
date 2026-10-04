import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { reportsApi } from '../api/client'

function Coverage({ value }) {
  return <div className="mt-3 flex items-center gap-3"><div className="h-1.5 flex-1 rounded-full bg-white/[.08]"><div className="h-full rounded-full bg-gradient-to-r from-[#8b3dff] to-[#e040c0]" style={{ width: `${value || 0}%` }} /></div><span className="text-xs text-gray-400">{value == null ? '—' : `${value}% overall match`}</span></div>
}

export default function History() {
  const [reports, setReports] = useState([])
  const [offset, setOffset] = useState(0)
  const [filter, setFilter] = useState('All')
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const load = async (nextOffset = 0) => { try { const { data } = await reportsApi.list({ limit: 20, offset: nextOffset }); setReports(current => nextOffset ? [...current, ...data.reports] : data.reports); setTotal(data.total); setOffset(nextOffset) } catch { setError('Could not load report history.') } finally { setLoading(false) } }
  useEffect(() => { load() }, [])
  const visible = filter === 'All' ? reports : reports.filter(report => report.match_level === filter)
  return <main className="mx-auto max-w-5xl px-6 py-10 md:px-10"><header className="mb-8"><p className="text-sm text-[#c084fc]">Saved analyses</p><h1 className="mt-2 text-4xl font-bold">Report history</h1><p className="mt-3 text-gray-400">Reports are saved to your account. You can delete them anytime.</p></header>
    <div className="mb-5 flex flex-wrap items-center justify-between gap-3"><label className="text-sm text-gray-400">Filter by match level<select className="field ml-3 w-auto px-3 py-2" value={filter} onChange={event => setFilter(event.target.value)}><option>All</option><option>Strong match</option><option>Partial match</option><option>Weak match</option><option>Not enough information</option></select></label><span className="text-xs text-gray-500">{total} total</span></div>
    {loading && <p className="text-gray-400">Loading reports...</p>}{error && <p className="text-red-300">{error}</p>}{!loading && !error && !visible.length && <div className="surface p-10 text-center"><h2 className="text-xl font-semibold">No reports yet</h2><p className="mt-2 text-sm text-gray-400">Analyze a resume to create your first report.</p><Link to="/analyze" className="primary-button mt-5 inline-block rounded-xl px-4 py-2 text-sm font-medium">Analyze a resume</Link></div>}
    <div className="space-y-3">{visible.map(report => <Link key={report.id} to={`/history/${report.id}`} className="surface block p-5 hover:border-[#9b2cff]/50"><div className="flex flex-wrap justify-between gap-3"><div><h2 className="font-medium">{report.target_role || 'Untitled role'}</h2><p className="mt-1 text-xs text-gray-500">{report.resume_filename} · {new Date(report.created_at).toLocaleString()}</p></div><span className="text-sm text-[#c084fc]">{report.match_level}</span></div><Coverage value={report.overall_match_percent ?? report.skill_coverage} /></Link>)}</div>
    {reports.length < total && <button onClick={() => load(offset + 20)} className="mt-6 rounded-xl border border-white/[.1] px-4 py-2 text-sm text-gray-300 hover:bg-white/[.05]">Load more</button>}
  </main>
}
