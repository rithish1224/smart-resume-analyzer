import React, { useState } from 'react';
import MultiCompare from '../components/compare/MultiCompare';
import toast from 'react-hot-toast';

const initialCandidates = [
  { id: '1', name: 'Alex Johnson', role: 'Senior ML Engineer', score: 92, match: 94, radarData: [{ subject: 'Python', value: 95 }, { subject: 'ML Ops', value: 85 }, { subject: 'System Design', value: 90 }, { subject: 'NLP', value: 92 }] },
  { id: '2', name: 'Samantha Lee', role: 'Backend Developer', score: 87, match: 89, radarData: [{ subject: 'FastAPI', value: 92 }, { subject: 'Database', value: 88 }, { subject: 'System Design', value: 84 }, { subject: 'Docker', value: 85 }] },
  { id: '3', name: 'David Smith', role: 'Data Scientist', score: 81, match: 82, radarData: [{ subject: 'Statistics', value: 90 }, { subject: 'Python', value: 85 }, { subject: 'XGBoost', value: 88 }, { subject: 'SQL', value: 75 }] },
  { id: '4', name: 'Elena Rostova', role: 'DevOps Engineer', score: 78, match: 76, radarData: [{ subject: 'Kubernetes', value: 85 }, { subject: 'CI/CD', value: 80 }, { subject: 'Cloud', value: 82 }, { subject: 'Python', value: 65 }] }
];

const Compare = () => {
  const [candidates, setCandidates] = useState(initialCandidates);

  const handleShortlist = (selectedIds) => {
    toast.success(`Shortlisted ${selectedIds.length} candidate(s) successfully!`);
  };

  const handleExport = (list) => {
    toast.success(`Exporting comparison report for ${list.length} candidate(s)...`);
  };

  return (
    <div className="min-h-screen bg-[#0a0a1a] text-white p-6 md:p-12 font-inter pt-20">
      <div className="max-w-7xl mx-auto space-y-8">
        <MultiCompare 
          candidates={candidates} 
          onShortlist={handleShortlist} 
          onExport={handleExport} 
        />

        <div className="p-8 rounded-2xl backdrop-blur-xl bg-white/5 border border-white/10">
          <h2 className="text-xl font-outfit font-semibold text-white mb-4">Batch Fairness & Ethics Audit</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-white/5 rounded-xl border border-white/10 text-center">
              <p className="text-sm text-gray-400">Disparate Impact Ratio (DIR)</p>
              <p className="text-2xl font-bold text-green-400 mt-1">0.92 (Pass)</p>
            </div>
            <div className="p-4 bg-white/5 rounded-xl border border-white/10 text-center">
              <p className="text-sm text-gray-400">Demographic Parity Gap</p>
              <p className="text-2xl font-bold text-white mt-1">0.05</p>
            </div>
            <div className="p-4 bg-white/5 rounded-xl border border-white/10 text-center">
              <p className="text-sm text-gray-400">Equal Opportunity Gap</p>
              <p className="text-2xl font-bold text-white mt-1">0.08</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Compare;
