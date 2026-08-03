import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { Mail, Lock, Loader2 } from 'lucide-react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { isAuthenticated, login } = useAuth();
  const navigate = useNavigate();

  if (isAuthenticated) {
    return <Navigate to="/analyze" replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error('Please enter email and password');
      return;
    }

    try {
      setIsLoading(true);
      await login(email, password);
      toast.success('Successfully signed in!');
      navigate('/analyze');
    } catch (err) {
      const message = err.response?.data?.detail || 'Invalid email or password';
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a1a] flex text-white font-inter">
      {/* Left Panel */}
      <div className="hidden lg:flex lg:w-1/2 p-12 flex-col justify-between relative overflow-hidden bg-white/5 backdrop-blur-3xl border-r border-white/10">
        <div className="absolute inset-0 z-0 opacity-20 pointer-events-none">
          <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-[#6366f1]/30 to-transparent" />
        </div>
        
        <div className="relative z-10">
          <h2 className="text-3xl font-outfit font-bold text-transparent bg-clip-text bg-gradient-to-r from-[#6366f1] to-[#06b6d4]">
            Smart Competency Diagnostic
          </h2>
        </div>
        
        <div className="relative z-10 space-y-6">
          <h1 className="text-5xl font-outfit font-extrabold leading-tight">
            Unlock AI-Powered Hiring Insights.
          </h1>
          <ul className="space-y-4 text-gray-300">
            <li className="flex items-center gap-3"><span className="text-[#6366f1]">✓</span> XGBoost Candidate Scoring</li>
            <li className="flex items-center gap-3"><span className="text-[#8b5cf6]">✓</span> SHAP Waterfall Explainability</li>
            <li className="flex items-center gap-3"><span className="text-[#06b6d4]">✓</span> Fairness & Disparate Impact Auditing</li>
          </ul>
        </div>
        
        <div className="relative z-10 text-sm text-gray-500">
          © {new Date().getFullYear()} Smart Competency Diagnostic.
        </div>
      </div>

      {/* Right Panel */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 relative">
        <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-md space-y-8"
        >
          <div className="text-center">
            <h2 className="text-3xl font-outfit font-bold text-white mb-2">Welcome Back</h2>
            <p className="text-gray-400">Sign in to access your dashboard</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input 
                  type="email" 
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:border-[#6366f1] focus:ring-1 focus:ring-[#6366f1] transition-all text-white placeholder:text-gray-600"
                  placeholder="name@company.com"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="text-sm font-medium text-gray-300">Password</label>
              </div>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input 
                  type="password" 
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:border-[#6366f1] focus:ring-1 focus:ring-[#6366f1] transition-all text-white placeholder:text-gray-600"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button 
              type="submit" 
              disabled={isLoading}
              className="w-full py-3 bg-gradient-to-r from-[#6366f1] to-[#8b5cf6] hover:from-[#4f46e5] hover:to-[#7c3aed] text-white rounded-xl font-medium transition-all shadow-[0_0_15px_rgba(99,102,241,0.3)] hover:shadow-[0_0_25px_rgba(99,102,241,0.5)] flex items-center justify-center gap-2"
            >
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Sign In'}
            </button>
          </form>

          <p className="text-center text-gray-400 text-sm">
            Don't have an account? <Link to="/register" className="text-[#6366f1] hover:text-[#8b5cf6] font-medium">Create one</Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default Login;
