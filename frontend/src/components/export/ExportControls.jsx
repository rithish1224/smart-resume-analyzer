import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FileDown, FileJson, Link, Loader2, Check } from 'lucide-react';

const ExportControls = ({ analysisId, modelVersion = 'v1.0.0', onExportPDF, onExportJSON }) => {
  const [loadingPdf, setLoadingPdf] = useState(false);
  const [loadingJson, setLoadingJson] = useState(false);
  const [copied, setCopied] = useState(false);

  const handlePdf = async () => {
    setLoadingPdf(true);
    if(onExportPDF) await onExportPDF(analysisId);
    setTimeout(() => setLoadingPdf(false), 1500);
  };

  const handleJson = async () => {
    setLoadingJson(true);
    if(onExportJSON) await onExportJSON(analysisId);
    setTimeout(() => setLoadingJson(false), 1500);
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(`${window.location.origin}/report/${analysisId}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-[#0a0a1a]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-6 text-white font-['Inter'] shadow-xl flex flex-col lg:flex-row justify-between items-center gap-6">
      
      <div className="flex flex-col gap-1">
        <h3 className="font-['Outfit'] text-lg font-semibold text-gray-200">Export & Share</h3>
        <div className="flex gap-3 text-xs text-gray-500">
          <span>Model: {modelVersion}</span>
          <span>|</span>
          <span>Generated: {new Date().toLocaleString()}</span>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-4">
        <motion.button 
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleCopyLink}
          className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg transition-colors text-sm font-medium"
        >
          {copied ? <Check className="w-4 h-4 text-green-400" /> : <Link className="w-4 h-4 text-gray-400" />}
          {copied ? 'Copied!' : 'Copy Link'}
        </motion.button>

        <motion.button 
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          disabled={loadingJson}
          onClick={handleJson}
          className="flex items-center gap-2 px-4 py-2 bg-violet-600/20 hover:bg-violet-600/30 border border-violet-500/30 text-violet-300 rounded-lg transition-colors text-sm font-medium disabled:opacity-50"
        >
          {loadingJson ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileJson className="w-4 h-4" />}
          Export JSON
        </motion.button>

        <motion.button 
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          disabled={loadingPdf}
          onClick={handlePdf}
          className="flex items-center gap-2 px-6 py-2 bg-indigo-600 hover:bg-indigo-700 shadow-[0_0_15px_rgba(99,102,241,0.5)] border border-indigo-500 text-white rounded-lg transition-colors text-sm font-medium disabled:opacity-50"
        >
          {loadingPdf ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileDown className="w-4 h-4" />}
          Export PDF
        </motion.button>
      </div>

    </div>
  );
};

export default ExportControls;
