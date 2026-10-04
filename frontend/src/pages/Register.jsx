import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuth } from '../context/AuthContext'
import RegisterForm from '../components/auth/RegisterForm'
import toast from 'react-hot-toast'
import Logo from '../components/ui/Logo'

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
      className="app-shell flex min-h-screen items-center justify-center px-6 py-12"
    >
      <div className="hidden lg:flex lg:w-1/2 max-w-xl p-12 flex-col justify-center relative overflow-hidden">
        <div className="relative z-10">
          <div className="mb-12"><Logo /></div>
          
          <h1 className="text-4xl font-bold mb-6 leading-tight">
            Start with clearer candidate evidence.
          </h1>
          
          <ul className="space-y-6 mt-12">
            {[
              { title: 'Resume analysis', desc: 'Extract the evidence that matters for a role.' },
              { title: 'Skill coverage', desc: 'See matched and missing requirements at a glance.' },
              { title: 'Human review', desc: 'Keep the final decision with a human reviewer.' }
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
          © 2026 Skillora
        </div>
      </div>

      <div className="w-full max-w-md flex items-center justify-center p-8 sm:p-12">
        <div className="w-full max-w-md">
          <RegisterForm onRegister={handleRegister} isLoading={isLoading} />
        </div>
      </div>
    </motion.div>
  )
}
