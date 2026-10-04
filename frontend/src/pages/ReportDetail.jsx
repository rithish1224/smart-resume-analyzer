import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { reportsApi } from '../api/client'
import { ResultCard } from './Analyze'

export default function ReportDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [report, setReport] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => { reportsApi.get(id).then(response => setReport(response.data)).catch(() => setError('Report not found.')) }, [id])
  const remove = async () => { if (!window.confirm('Delete this report?')) return; await reportsApi.remove(id); navigate('/history') }
  if (error) return <main className="mx-auto max-w-4xl px-6 py-10"><p className="text-red-300">{error}</p><Link className="mt-4 inline-block text-[#c084fc]" to="/history">Back to history</Link></main>
  if (!report) return <main className="mx-auto max-w-4xl px-6 py-10 text-gray-400">Loading report...</main>
  return <main className="mx-auto max-w-4xl px-6 py-10"><div className="no-print mb-6 flex flex-wrap items-center justify-between gap-3"><div><p className="text-sm text-[#c084fc]">Report history</p><h1 className="mt-1 text-3xl font-bold">{report.target_role || 'Untitled role'}</h1><p className="mt-2 text-xs text-gray-500">{report.resume_filename} · {new Date(report.created_at).toLocaleString()}</p></div><div className="flex gap-2"><button onClick={() => window.print()} className="rounded-lg border border-white/[.1] px-3 py-2 text-sm text-gray-300">Print / Save as PDF</button><button onClick={remove} className="rounded-lg border border-red-500/30 px-3 py-2 text-sm text-red-300">Delete report</button></div></div><ResultCard result={report} /><details className="surface mt-4 p-5"><summary className="cursor-pointer text-sm font-medium">Job description</summary><p className="mt-4 whitespace-pre-wrap text-sm leading-6 text-gray-400">{report.job_description}</p></details></main>
}
