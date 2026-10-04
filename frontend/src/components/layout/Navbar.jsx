import { useState } from 'react'
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom'
import { Clock3, FileSearch, Info, LogOut, Menu, X } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import Logo from '../ui/Logo'

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth()
  const [open, setOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const signOut = async () => { await logout(); navigate('/login') }
  const close = () => setOpen(false)
  if (!isAuthenticated || location.pathname === '/' || location.pathname === '/about') return <header className="absolute inset-x-0 top-0 z-50 border-b border-white/[.07] bg-[#09090b]/70 backdrop-blur-xl">
    <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
      <Logo />
      <button className="hidden max-md:block text-gray-400" onClick={() => setOpen(!open)} aria-label="Toggle menu">{open ? <X size={20} /> : <Menu size={20} />}</button>
      <nav className={`${open ? 'flex' : 'hidden md:flex'} items-center gap-7 max-md:absolute max-md:left-0 max-md:right-0 max-md:top-full max-md:flex-col max-md:items-stretch max-md:border-b max-md:border-white/[.07] max-md:bg-[#09090b] max-md:p-6`}>
        <a href="/" onClick={close} className="text-sm text-gray-400 hover:text-white">Home</a>
        <a href="/#how-it-works" onClick={close} className="text-sm text-gray-400 hover:text-white">How it works</a>
        <Link to="/about" onClick={close} className="text-sm text-gray-400 hover:text-white">About</Link>
        <div className="flex gap-2 max-md:flex-col">{isAuthenticated ? <><Link to="/analyze" onClick={close} className="primary-button rounded-lg px-4 py-2 text-center text-sm font-medium">Analyze</Link><button onClick={signOut} className="rounded-lg border border-white/[.1] px-4 py-2 text-sm text-gray-300">Logout</button></> : <><Link to="/login" onClick={close} className="rounded-lg border border-white/[.1] px-4 py-2 text-center text-sm text-gray-300">Login</Link><Link to="/register" onClick={close} className="primary-button rounded-lg px-4 py-2 text-center text-sm font-medium">Register</Link></>}</div>
      </nav>
    </div>
  </header>
  return <aside className="fixed inset-y-0 left-0 z-50 w-64 border-r border-white/[.07] bg-[#0d0d0f]/95 px-4 py-5 backdrop-blur-xl max-md:w-full max-md:h-auto max-md:inset-x-0 max-md:bottom-auto">
    <div className="flex items-center justify-between px-3"><Logo /><button className="hidden max-md:block text-gray-400" onClick={() => setOpen(!open)} aria-label="Toggle navigation">{open ? <X size={20} /> : <Menu size={20} />}</button></div>
    <nav className={`${open ? 'block' : 'max-md:hidden'} mt-10 space-y-1`} aria-label="Primary navigation">
      {[[FileSearch, 'Analyze', '/analyze'], [Clock3, 'History', '/history'], [Info, 'About', '/about']].map(([Icon, label, to]) => <NavLink key={to} to={to} onClick={close} className={({ isActive }) => `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm ${isActive ? 'bg-white/[.09] text-white' : 'text-gray-400 hover:bg-white/[.05] hover:text-white'}`}><Icon size={18} />{label}</NavLink>)}
    </nav>
    <div className={`${open ? 'block' : 'max-md:hidden'} absolute bottom-5 left-4 right-4 max-md:static max-md:mt-5 border-t border-white/[.07] pt-4`}>
      <div className="mb-3 px-2"><p className="truncate text-sm text-white">{user?.name || user?.full_name || user?.email}</p><p className="truncate text-xs text-gray-500">{user?.email}</p></div>
      <button onClick={signOut} className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-gray-400 hover:bg-white/[.05] hover:text-white"><LogOut size={18} /> Logout</button>
    </div>
  </aside>
}
