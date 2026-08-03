import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const Home = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.2 },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 },
  };

  return (
    <div className="min-h-screen bg-[#0a0a1a] text-white overflow-hidden relative font-inter">
      {/* Animated Background */}
      <div className="absolute inset-0 z-0 overflow-hidden opacity-30 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-[#6366f1] rounded-full blur-[150px] mix-blend-screen" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-[#8b5cf6] rounded-full blur-[150px] mix-blend-screen" />
        <div className="absolute top-[40%] left-[60%] w-[30%] h-[30%] bg-[#06b6d4] rounded-full blur-[120px] mix-blend-screen" />
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMCIgaGVpZ2h0PSIyMCI+CjxjaXJjbGUgY3g9IjIiIGN5PSIyIiByPSIxIiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMDUpIiAvPgo8L3N2Zz4=')] opacity-50" />
      </div>

      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-6 py-20 mx-auto max-w-7xl">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="flex flex-col items-center text-center space-y-12 w-full"
        >
          {/* Hero Section */}
          <div className="space-y-6 max-w-4xl">
            <motion.h1
              variants={itemVariants}
              className="font-outfit text-5xl md:text-7xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-[#6366f1] via-[#8b5cf6] to-[#06b6d4]"
            >
              🧠 Smart Competency Diagnostic
            </motion.h1>
            <motion.p
              variants={itemVariants}
              className="text-lg md:text-2xl text-gray-400 font-light max-w-2xl mx-auto"
            >
              AI-Powered Candidate Scoring with XGBoost + SHAP Explainability
            </motion.p>
            <motion.div variants={itemVariants} className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
              <Link to="/analyze">
                <button className="px-8 py-4 bg-gradient-to-r from-[#6366f1] to-[#8b5cf6] hover:from-[#4f46e5] hover:to-[#7c3aed] text-white rounded-xl font-medium text-lg transition-all shadow-[0_0_20px_rgba(99,102,241,0.4)] hover:shadow-[0_0_30px_rgba(99,102,241,0.6)] hover:-translate-y-1">
                  Start Analyzing →
                </button>
              </Link>
              <Link to="/about">
                <button className="px-8 py-4 bg-white/5 border border-white/10 hover:bg-white/10 text-white rounded-xl font-medium text-lg transition-all backdrop-blur-md">
                  View Demo & Details
                </button>
              </Link>
            </motion.div>
          </div>

          {/* Floating Score Card Preview */}
          <motion.div
            variants={itemVariants}
            className="w-full max-w-md p-6 mt-8 rounded-2xl backdrop-blur-xl bg-white/5 border border-white/10 shadow-2xl relative"
          >
             <div className="absolute -top-4 -right-4 bg-green-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">
                Top Match
             </div>
             <div className="flex justify-between items-center mb-6">
                <div>
                   <h3 className="text-xl font-bold font-outfit text-white">Software Engineer</h3>
                   <p className="text-sm text-gray-400">Match Score</p>
                </div>
                <div className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-[#06b6d4] to-[#6366f1]">
                   87<span className="text-2xl text-gray-500">/100</span>
                </div>
             </div>
             <div className="space-y-3">
               {[
                 { label: 'Technical Skills', val: '92%' },
                 { label: 'Problem Solving', val: '85%' },
                 { label: 'Experience', val: '80%' }
               ].map((item, i) => (
                 <div key={i} className="flex justify-between items-center">
                   <span className="text-gray-300 text-sm">{item.label}</span>
                   <div className="w-1/2 bg-white/10 rounded-full h-2">
                     <div className="bg-gradient-to-r from-[#6366f1] to-[#06b6d4] h-2 rounded-full" style={{width: item.val}} />
                   </div>
                 </div>
               ))}
             </div>
          </motion.div>

          {/* Feature Cards */}
          <motion.div
            variants={containerVariants}
            className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full pt-16"
          >
            {[
              { icon: '🎯', title: 'Transparent Scoring', desc: 'XGBoost + SHAP for fully explainable AI decisions.' },
              { icon: '⚡', title: 'Skill Gap Radar', desc: '6-axis competency visualization for deep insights.' },
              { icon: '🛡️', title: 'Fairness Audit', desc: 'DIR + DP + EO metrics to ensure unbiased hiring.' },
            ].map((feat, index) => (
              <motion.div
                key={index}
                variants={itemVariants}
                className="p-8 rounded-2xl backdrop-blur-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
              >
                <div className="text-4xl mb-4">{feat.icon}</div>
                <h3 className="text-xl font-semibold font-outfit text-white mb-2">{feat.title}</h3>
                <p className="text-gray-400">{feat.desc}</p>
              </motion.div>
            ))}
          </motion.div>

          {/* Stats Row */}
          <motion.div variants={itemVariants} className="w-full pt-12 border-t border-white/10">
             <div className="flex flex-wrap justify-center gap-8 md:gap-16 text-center text-sm md:text-base text-gray-400 font-medium">
               <span>500+ Profiles Trained</span>
               <span>8 Domains</span>
               <span>20+ Features</span>
               <span>3 Fairness Metrics</span>
             </div>
          </motion.div>

          {/* Footer Note */}
          <motion.div variants={itemVariants} className="pt-8 opacity-60 text-xs">
            B.Tech CSE Final Year Project
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
};

export default Home;
