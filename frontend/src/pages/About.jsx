import { FileSearch, Layers3, ShieldCheck } from 'lucide-react'

export default function About() {
  return <main className="mx-auto max-w-5xl px-6 py-12 md:px-10">
    <p className="text-sm text-[#c084fc]">About the workspace</p>
    <h1 className="mt-2 text-4xl font-bold tracking-tight">Evidence-led resume analysis.</h1>
    <p className="mt-4 max-w-2xl leading-7 text-gray-400">Skillora helps reviewers compare resume evidence with a role description. It is designed to surface useful context, not make an automatic hiring decision.</p>
    <div className="mt-12 grid gap-4 md:grid-cols-3">
      {[
        [FileSearch, 'Extract', 'Read skills and experience from the submitted resume.'],
        [Layers3, 'Compare', 'Map resume evidence to the requirements in a role.'],
        [ShieldCheck, 'Review', 'Use the result as assistive context alongside human judgment.'],
      ].map(([Icon, title, text]) => <section className="surface p-6" key={title}><Icon className="mb-5 text-[#c084fc]" size={22} /><h2 className="font-semibold">{title}</h2><p className="mt-2 text-sm leading-6 text-gray-400">{text}</p></section>)}
    </div>
    <p className="mt-10 text-xs text-gray-500">Analysis is assistive and should not be used for automatic rejection.</p>
  </main>
}
