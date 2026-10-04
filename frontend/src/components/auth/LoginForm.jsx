import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useForm } from 'react-form';
import { Eye, EyeOff, Lock, Mail, Loader2, Sparkles } from 'lucide-react';
// Note: Simulating Zod/React Hook Form for simplicity as they aren't standard built-in. Assuming structure.

const LoginForm = ({ onLogin, isLoading, error }) => {
  const [showPwd, setShowPwd] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if(onLogin) onLogin({ email, password });
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-md mx-auto bg-[#0a0a1a]/90 backdrop-blur-2xl border border-white/10 rounded-3xl p-8 shadow-[0_0_40px_rgba(99,102,241,0.15)] text-white font-['Inter'] relative overflow-hidden"
    >
      <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-64 h-64 bg-violet-500/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2 pointer-events-none" />

      <div className="text-center mb-8 relative z-10">
        <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-2xl mx-auto flex items-center justify-center mb-4 shadow-lg shadow-indigo-500/30">
          <Sparkles className="w-8 h-8 text-white" />
        </div>
        <h2 className="text-2xl font-bold font-['Outfit'] mb-2">Welcome Back</h2>
        <p className="text-gray-400 text-sm">Sign in to Skillora</p>
      </div>

      <motion.form 
        onSubmit={handleSubmit} 
        className="space-y-5 relative z-10"
        animate={error ? { x: [-10, 10, -10, 10, 0] } : {}}
        transition={{ duration: 0.4 }}
      >
        {error && (
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm text-center">
            {error}
          </div>
        )}
        
        <div className="space-y-1">
          <label className="text-sm font-medium text-gray-300 ml-1">Email</label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input 
              type="email" 
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-black/30 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all placeholder:text-gray-600"
              placeholder="name@company.com"
            />
          </div>
        </div>

        <div className="space-y-1">
          <label className="text-sm font-medium text-gray-300 ml-1">Password</label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input 
              type={showPwd ? 'text' : 'password'} 
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-black/30 border border-white/10 rounded-xl py-3 pl-10 pr-12 text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all placeholder:text-gray-600"
              placeholder="••••••••"
            />
            <button 
              type="button" 
              onClick={() => setShowPwd(!showPwd)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
            >
              {showPwd ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between text-sm">
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" className="rounded border-gray-600 bg-black/30 text-indigo-500 focus:ring-indigo-500 focus:ring-offset-gray-900" />
            <span className="text-gray-400">Remember me</span>
          </label>
          <a href="#" className="text-indigo-400 hover:text-indigo-300">Forgot password?</a>
        </div>

        <button 
          type="submit" 
          disabled={isLoading}
          className="w-full bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white rounded-xl py-3 font-semibold shadow-lg shadow-indigo-500/25 transition-all flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed mt-2"
        >
          {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Sign In'}
        </button>
        
        <p className="text-center text-sm text-gray-400 mt-6">
          Don't have an account? <a href="/register" className="text-indigo-400 hover:text-indigo-300 font-medium">Create one</a>
        </p>
      </motion.form>
    </motion.div>
  );
};

export default LoginForm;
