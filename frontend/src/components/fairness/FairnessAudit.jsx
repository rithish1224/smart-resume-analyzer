import React from 'react';
import { motion } from 'framer-motion';
import { Shield, ShieldAlert, ShieldCheck, Info } from 'lucide-react';

const FairnessAudit = ({ fairnessData = {} }) => {
  const {
    dir = 0.85,
    dp = 0.05,
    eo = { tprGap: 0.04, fprGap: 0.06 },
    verdict = 'FAIR',
    timestamp = new Date().toISOString(),
    version = 'v1.0.0',
    proxyNote = 'Groups inferred from name (gender proxy) and graduation year (age proxy)'
  } = fairnessData;

  const getDirStatus = (val) => val >= 0.8 ? 'PASS' : (val >= 0.7 ? 'CAUTION' : 'FAIL');
  const getDpStatus = (val) => val <= 0.1 ? 'PASS' : (val <= 0.15 ? 'CAUTION' : 'FAIL');
  const getEoStatus = (tpr, fpr) => (tpr <= 0.1 && fpr <= 0.1) ? 'PASS' : 'FAIL';

  const dirStatus = getDirStatus(dir);
  const dpStatus = getDpStatus(dp);
  const eoStatus = getEoStatus(eo.tprGap, eo.fprGap);

  const StatusBadge = ({ status }) => (
    <span className={`px-2 py-1 text-xs font-semibold rounded-full border ${
      status === 'PASS' ? 'bg-green-500/20 text-green-400 border-green-500/50' :
      status === 'CAUTION' ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50' :
      'bg-red-500/20 text-red-400 border-red-500/50'
    }`}>
      {status}
    </span>
  );

  const containerVariants = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <div className="bg-[#0a0a1a]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 text-white font-['Inter'] shadow-2xl">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <Shield className="w-8 h-8 text-indigo-400" />
          <h2 className="text-2xl font-bold font-['Outfit']">Fairness Audit Report</h2>
        </div>
        <div className="flex items-center gap-2">
          {verdict === 'FAIR' ? (
            <div className="flex items-center gap-2 bg-green-500/20 text-green-400 px-4 py-2 rounded-lg border border-green-500/30 font-semibold tracking-wider">
              <ShieldCheck className="w-5 h-5" /> FAIR VERDICT
            </div>
          ) : (
            <div className="flex items-center gap-2 bg-red-500/20 text-red-400 px-4 py-2 rounded-lg border border-red-500/30 font-semibold tracking-wider">
              <ShieldAlert className="w-5 h-5" /> BIAS DETECTED
            </div>
          )}
        </div>
      </div>

      <motion.div 
        className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6"
        variants={containerVariants}
        initial="hidden"
        animate="show"
      >
        {/* DIR Card */}
        <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-xl p-5 flex flex-col justify-between">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="font-['Outfit'] font-semibold text-gray-300">Disparate Impact Ratio</h3>
              <p className="text-xs text-gray-500">Target ≥ 0.80</p>
            </div>
            <StatusBadge status={dirStatus} />
          </div>
          <div className="flex items-center justify-center">
            <div className="relative w-24 h-24 rounded-full flex items-center justify-center border-4" style={{
              borderColor: dirStatus === 'PASS' ? '#22c55e' : (dirStatus === 'CAUTION' ? '#eab308' : '#ef4444')
            }}>
              <span className="text-2xl font-bold">{dir.toFixed(2)}</span>
            </div>
          </div>
        </motion.div>

        {/* DP Card */}
        <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-xl p-5 flex flex-col justify-between">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="font-['Outfit'] font-semibold text-gray-300">Demographic Parity</h3>
              <p className="text-xs text-gray-500">Target ≤ 0.10 Diff</p>
            </div>
            <StatusBadge status={dpStatus} />
          </div>
          <div className="mt-4">
            <div className="flex justify-between text-sm mb-1">
              <span>Diff Value</span>
              <span>{dp.toFixed(2)}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-3">
              <div 
                className={`h-3 rounded-full ${dpStatus === 'PASS' ? 'bg-green-500' : 'bg-red-500'}`} 
                style={{ width: `${Math.min(dp * 100 * 5, 100)}%` }} 
              />
            </div>
          </div>
        </motion.div>

        {/* EO Card */}
        <motion.div variants={itemVariants} className="bg-white/5 border border-white/10 rounded-xl p-5 flex flex-col justify-between">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="font-['Outfit'] font-semibold text-gray-300">Equalized Odds</h3>
              <p className="text-xs text-gray-500">Target TPR/FPR Gap ≤ 0.10</p>
            </div>
            <StatusBadge status={eoStatus} />
          </div>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span>TPR Gap</span>
                <span>{eo.tprGap.toFixed(2)}</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div className={`h-2 rounded-full ${eo.tprGap <= 0.1 ? 'bg-green-500' : 'bg-red-500'}`} style={{ width: `${Math.min(eo.tprGap * 100 * 5, 100)}%` }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span>FPR Gap</span>
                <span>{eo.fprGap.toFixed(2)}</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div className={`h-2 rounded-full ${eo.fprGap <= 0.1 ? 'bg-green-500' : 'bg-red-500'}`} style={{ width: `${Math.min(eo.fprGap * 100 * 5, 100)}%` }} />
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>

      <div className="bg-white/5 rounded-lg p-4 border border-white/5 flex gap-4 text-sm text-gray-400 items-start">
        <Info className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
        <div>
          <p className="mb-1"><strong className="text-gray-300">Proxy Information:</strong> {proxyNote}</p>
          <p className="text-xs">Model Version: {version} | Audit Time: {new Date(timestamp).toLocaleString()}</p>
        </div>
      </div>
    </div>
  );
};

export default FairnessAudit;
