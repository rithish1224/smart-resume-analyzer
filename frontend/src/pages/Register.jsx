import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuth } from '../context/AuthContext'
import RegisterForm from '../components/auth/RegisterForm'
import toast from 'react-hot-toast'

export default function Register() {
  const { isAuthenticated, register, login } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()

  if (isAuthenticated) {
    return <Navigate to="/analyze" replace />
  }

  const handleRegister = async (formData) => {
    try {
      setIsLoading(true)
      await register({
        email: formData.email,
        password: formData.password,
        full_name: formData.name,
        name: formData.name,
        role: formData.role
      })
      
      // Auto login right after registration
      await login(formData.email, formData.password)
      toast.success('Account created successfully!')
      navigate('/analyze')
    } catch (err) {
      const message = err.response?.data?.detail || 'Registration failed. Please try again.'
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="min-h-[calc(100vh-64px)] flex"
    >
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-indigo-900/50 to-violet-900/50 p-12 flex-col justify-between border-r border-white/10 relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]" />
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-12">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-r from-indigo-500 to-violet-500 flex items-center justify-center">
              <span className="font-outfit font-bold text-xl">S</span>
            </div>
            <span className="font-outfit font-bold text-2xl tracking-tight">SmartCompetency</span>
          </div>
          
          <h1 className="text-4xl font-outfit font-bold mb-6 leading-tight">
            Next-Gen AI <br /> Talent Analytics
          </h1>
          
          <ul className="space-y-6 mt-12">
            {[
              { title: 'Resume Parsing', desc: 'Accurate extraction of skills and experience.' },
              { title: 'Competency Scoring', desc: 'Multi-dimensional evaluation against role requirements.' },
              { title: 'Explainable AI', desc: 'SHAP values to understand every AI decision.' }
            ].map((feature, idx) => (
              <li key={idx} className="flex gap-4">
                <div className="w-8 h-8 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center flex-shrink-0">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-white">{feature.title}</h3>
                  <p className="text-slate-400 text-sm mt-1">{feature.desc}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
        
        <div className="relative z-10 text-slate-400 text-sm">
          &copy; {new Date().getFullYear()} Smart Competency Diagnostic.
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-8 sm:p-12">
        <div className="w-full max-w-md">
          <RegisterForm onRegister={handleRegister} isLoading={isLoading} />
        </div>
      </div>
    </motion.div>
  )
}
