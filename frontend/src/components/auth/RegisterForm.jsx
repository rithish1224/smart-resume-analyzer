import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Eye, EyeOff, Loader2 } from 'lucide-react'

export default function RegisterForm({ onRegister, isLoading }) {
  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '' })
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const update = event => setForm({ ...form, [event.target.name]: event.target.value })
  const mismatch = form.confirm.length > 0 && form.password !== form.confirm
  const submit = event => { event.preventDefault(); if (!mismatch) onRegister({ ...form, role: 'candidate' }) }
  const passwordField = (name, label, visible, toggle) => <label className="block text-sm text-gray-300">{label}<div className="relative mt-2"><input className="field px-4 py-3 pr-11" name={name} type={visible ? 'text' : 'password'} required value={form[name]} onChange={update} /><button type="button" onClick={toggle} className="absolute right-3 top-3 text-gray-500 hover:text-white" aria-label={`Show or hide ${label.toLowerCase()}`}>{visible ? <EyeOff size={17} /> : <Eye size={17} />}</button></div>{name === 'confirm' && mismatch && <span className="mt-1 block text-xs text-red-300">Passwords do not match</span>}</label>
  return <div className="surface w-full p-8">
    <h2 className="text-2xl font-bold">Create your account</h2><p className="mt-2 text-sm text-gray-400">Start reviewing resume skill coverage.</p>
    <form onSubmit={submit} className="mt-7 space-y-4">
      <label className="block text-sm text-gray-300">Name<input className="field mt-2 px-4 py-3" name="name" required value={form.name} onChange={update} /></label>
      <label className="block text-sm text-gray-300">Email<input className="field mt-2 px-4 py-3" name="email" type="email" required value={form.email} onChange={update} /></label>
      {passwordField('password', 'Password', showPassword, () => setShowPassword(!showPassword))}
      {passwordField('confirm', 'Confirm password', showConfirm, () => setShowConfirm(!showConfirm))}
      <button className="primary-button flex w-full items-center justify-center gap-2 rounded-xl px-4 py-3 font-medium disabled:opacity-60" disabled={isLoading || mismatch}>{isLoading ? <Loader2 className="animate-spin" size={18} /> : 'Create account'}</button>
    </form>
    <p className="mt-6 text-center text-sm text-gray-500">Already have an account? <Link className="text-[#c084fc]" to="/login">Sign in</Link></p>
  </div>
}
