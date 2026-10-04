import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, Loader2, Lock, Mail } from 'lucide-react'
import Logo from '../components/ui/Logo'
import toast from 'react-hot-toast'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { isAuthenticated, login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  if (isAuthenticated) return <Navigate to="/analyze" replace />
  const submit = async event => {
    event.preventDefault()
    setLoading(true)
    try { await login(email, password); navigate('/analyze') }
    catch (error) { toast.error(error.response?.data?.detail || 'Unable to sign in.') }
    finally { setLoading(false) }
  }
  return <div className="app-shell flex min-h-screen items-center justify-center px-6 py-12">
    <div className="surface w-full max-w-md p-8">
      <div className="mb-10"><Logo /></div>
      <h1 className="text-3xl font-bold">Welcome back</h1><p className="mt-2 text-sm text-gray-400">Sign in to continue your analysis.</p>
      <form onSubmit={submit} className="mt-8 space-y-4">
        <label className="block text-sm text-gray-300">Email<div className="relative mt-2"><Mail size={17} className="absolute left-3 top-3.5 text-gray-500" /><input className="field pl-10 pr-4 py-3" type="email" required value={email} onChange={e => setEmail(e.target.value)} /></div></label>
        <label className="block text-sm text-gray-300">Password<div className="relative mt-2"><Lock size={17} className="absolute left-3 top-3.5 text-gray-500" /><input className="field pl-10 pr-11 py-3" type={showPassword ? 'text' : 'password'} required value={password} onChange={e => setPassword(e.target.value)} /><button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-3 text-gray-500" aria-label="Show or hide password">{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button></div></label>
        <button className="primary-button flex w-full items-center justify-center gap-2 rounded-xl px-4 py-3 font-medium disabled:opacity-60" disabled={loading}>{loading ? <Loader2 className="animate-spin" size={18} /> : 'Sign in'}</button>
      </form>
      <p className="mt-6 text-center text-sm text-gray-500">New here? <Link className="text-[#c084fc] hover:text-white" to="/register">Create an account</Link></p>
    </div>
  </div>
}
