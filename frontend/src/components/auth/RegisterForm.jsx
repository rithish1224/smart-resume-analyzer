import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Mail, Lock, User, Briefcase, GraduationCap, Loader2, Sparkles } from 'lucide-react';

const RegisterForm = ({ onRegister, isLoading, error }) => {
  const [formData, setFormData] = useState({ name: '', email: '', password: '', confirm: '', role: 'candidate' });

  const handleSubmit = (e) => {
    e.preventDefault();
    if(formData.password !== formData.confirm) {
      toast.error("Passwords do not match"); 
      return;
    }
    if(onRegister) onRegister(formData);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-md mx-auto bg-[#0a0a1a]/90 backdrop-blur-2xl border border-white/10 rounded-3xl p-8 shadow-[0_0_40px_rgba(99,102,241,0.15)] text-white font-['Inter'] relative overflow-hidden"
    >
      <div className="absolute top-0 left-0 w-64 h-64 bg-violet-500/10 rounded-full blur-3xl -translate-y-1/2 -translate-x-1/2 pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl translate-y-1/2 translate-x-1/2 pointer-events-none" />

      <div className="text-center mb-8 relative z-10">
        <h2 className="text-2xl font-bold font-['Outfit'] mb-2">Create Account</h2>
        <p className="text-gray-400 text-sm">Join the Smart Competency Diagnostic platform</p>
      </div>

      <motion.form onSubmit={handleSubmit} className="space-y-4 relative z-10">
        
        {/* Role Selection */}
        <div className="grid grid-cols-2 gap-3 mb-6">
          <label className={`flex flex-col items-center justify-center p-3 border rounded-xl cursor-pointer transition-all ${formData.role === 'candidate' ? 'bg-indigo-500/20 border-indigo-500 text-indigo-300' : 'bg-black/30 border-white/10 text-gray-400 hover:bg-white/5'}`}>
            <input type="radio" name="role" value="candidate" checked={formData.role === 'candidate'} onChange={(e) => setFormData({...formData, role: e.target.value})} className="hidden" />
            <GraduationCap className="w-6 h-6 mb-1" />
            <span className="text-sm font-medium">Candidate</span>
          </label>
          <label className={`flex flex-col items-center justify-center p-3 border rounded-xl cursor-pointer transition-all ${formData.role === 'recruiter' ? 'bg-indigo-500/20 border-indigo-500 text-indigo-300' : 'bg-black/30 border-white/10 text-gray-400 hover:bg-white/5'}`}>
            <input type="radio" name="role" value="recruiter" checked={formData.role === 'recruiter'} onChange={(e) => setFormData({...formData, role: e.target.value})} className="hidden" />
            <Briefcase className="w-6 h-6 mb-1" />
            <span className="text-sm font-medium">Recruiter</span>
          </label>
        </div>

        <div className="relative">
          <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input required type="text" placeholder="Full Name" value={formData.name} onChange={e=>setFormData({...formData, name: e.target.value})}
            className="w-full bg-black/30 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all placeholder:text-gray-600" />
        </div>

        <div className="relative">
          <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input required type="email" placeholder="Email Address" value={formData.email} onChange={e=>setFormData({...formData, email: e.target.value})}
            className="w-full bg-black/30 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all placeholder:text-gray-600" />
        </div>

        <div className="relative">
          <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input required type="password" placeholder="Password" value={formData.password} onChange={e=>setFormData({...formData, password: e.target.value})}
            className="w-full bg-black/30 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all placeholder:text-gray-600" />
        </div>

        <div className="relative">
          <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input required type="password" placeholder="Confirm Password" value={formData.confirm} onChange={e=>setFormData({...formData, confirm: e.target.value})}
            className="w-full bg-black/30 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all placeholder:text-gray-600" />
        </div>

        <button type="submit" disabled={isLoading} className="w-full mt-4 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white rounded-xl py-3 font-semibold shadow-lg shadow-indigo-500/25 transition-all flex items-center justify-center gap-2">
          {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Register'}
        </button>

        <p className="text-center text-sm text-gray-400 mt-4">
          Already have an account? <Link to="/login" className="text-indigo-400 hover:text-indigo-300 font-medium">Sign In</Link>
        </p>

      </motion.form>
    </motion.div>
  );
};

export default RegisterForm;
