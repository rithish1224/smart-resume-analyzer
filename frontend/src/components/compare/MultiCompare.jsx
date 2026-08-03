import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, Plus, ArrowUpDown, MoreHorizontal, UserCheck } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer } from 'recharts';

const MultiCompare = ({ candidates = [], onShortlist, onExport }) => {
  const [sortField, setSortField] = useState('score');
  const [sortAsc, setSortAsc] = useState(false);
  const [selected, setSelected] = useState([]);

  const handleSort = (field) => {
    if (sortField === field) setSortAsc(!sortAsc);
    else { setSortField(field); setSortAsc(false); }
  };

  const toggleSelect = (id) => {
    setSelected(prev => prev.includes(id) ? prev.filter(c => c !== id) : [...prev, id]);
  };

  const toggleAll = () => {
    setSelected(selected.length === candidates.length ? [] : candidates.map(c => c.id));
  };

  const sortedCandidates = [...candidates].sort((a, b) => {
    let valA = a[sortField];
    let valB = b[sortField];
    if (typeof valA === 'string') valA = valA.toLowerCase();
    if (typeof valB === 'string') valB = valB.toLowerCase();
    
    if (valA < valB) return sortAsc ? -1 : 1;
    if (valA > valB) return sortAsc ? 1 : -1;
    return 0;
  });

  const MiniRadar = ({ data }) => (
    <div className="w-16 h-16">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
          <PolarGrid stroke="#374151" strokeWidth={0.5} />
          <Radar dataKey="value" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.6} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );

  if (candidates.length === 0) {
    return (
      <div className="bg-[#0a0a1a]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-12 text-center text-white font-['Inter']">
        <UserCheck className="w-16 h-16 text-gray-500 mx-auto mb-4 opacity-50" />
        <h3 className="text-xl font-['Outfit'] font-semibold mb-2">No Candidates to Compare</h3>
        <p className="text-gray-400">Upload resumes in the Analyze tab to compare candidates here.</p>
      </div>
    );
  }

  return (
    <div className="bg-[#0a0a1a]/80 backdrop-blur-xl border border-white/10 rounded-2xl text-white font-['Inter'] shadow-xl overflow-hidden flex flex-col">
      {/* Toolbar */}
      <div className="p-6 border-b border-white/10 flex flex-wrap justify-between items-center gap-4 bg-white/5">
        <h2 className="text-2xl font-bold font-['Outfit']">Compare Candidates</h2>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors text-sm">
            <Plus className="w-4 h-4" /> Add Candidate
          </button>
          <button onClick={() => onExport(candidates)} className="flex items-center gap-2 px-4 py-2 bg-indigo-600 border border-indigo-500 rounded-lg hover:bg-indigo-700 transition-colors text-sm">
            <Download className="w-4 h-4" /> Export Comparison
          </button>
        </div>
      </div>

      {/* Bulk Actions */}
      <AnimatePresence>
        {selected.length > 0 && (
          <motion.div 
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="bg-indigo-900/40 border-b border-indigo-500/30 px-6 py-3 flex justify-between items-center"
          >
            <span className="text-sm font-semibold text-indigo-200">{selected.length} Selected</span>
            <div className="flex gap-3">
              <button onClick={() => onShortlist(selected)} className="px-3 py-1.5 bg-indigo-500 hover:bg-indigo-600 text-white text-xs rounded shadow transition-colors">
                Shortlist Selected
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left whitespace-nowrap">
          <thead className="bg-black/20 text-gray-400 text-sm border-b border-white/10">
            <tr>
              <th className="p-4 w-12"><input type="checkbox" checked={selected.length === candidates.length && candidates.length > 0} onChange={toggleAll} className="rounded border-gray-600 bg-gray-800" /></th>
              <th className="p-4 cursor-pointer hover:text-white" onClick={() => handleSort('name')}>Name <ArrowUpDown className="w-3 h-3 inline ml-1" /></th>
              <th className="p-4 cursor-pointer hover:text-white" onClick={() => handleSort('role')}>Role <ArrowUpDown className="w-3 h-3 inline ml-1" /></th>
              <th className="p-4 cursor-pointer hover:text-white" onClick={() => handleSort('score')}>Score <ArrowUpDown className="w-3 h-3 inline ml-1" /></th>
              <th className="p-4">Competency Radar</th>
              <th className="p-4 cursor-pointer hover:text-white" onClick={() => handleSort('match')}>Match % <ArrowUpDown className="w-3 h-3 inline ml-1" /></th>
              <th className="p-4">Action</th>
            </tr>
          </thead>
          <motion.tbody 
            initial="hidden" animate="show"
            variants={{ show: { transition: { staggerChildren: 0.05 } } }}
          >
            {sortedCandidates.map((c, i) => (
              <motion.tr 
                key={c.id} 
                variants={{ hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0 } }}
                className={`border-b border-white/5 hover:bg-white/5 transition-colors ${selected.includes(c.id) ? 'bg-indigo-500/10' : ''}`}
              >
                <td className="p-4"><input type="checkbox" checked={selected.includes(c.id)} onChange={() => toggleSelect(c.id)} className="rounded border-gray-600 bg-gray-800 text-indigo-500" /></td>
                <td className="p-4 font-medium">{c.name}</td>
                <td className="p-4 text-gray-300 text-sm">{c.role}</td>
                <td className="p-4">
                  <div className="flex items-center gap-2">
                    <div className="text-lg font-bold font-['Outfit'] text-indigo-400">{c.score}</div>
                    <div className="w-16 h-1.5 bg-gray-800 rounded-full overflow-hidden"><div className="h-full bg-indigo-500" style={{ width: `${c.score}%` }}></div></div>
                  </div>
                </td>
                <td className="p-4">
                  <MiniRadar data={c.radarData || [{subject:'A',value:80},{subject:'B',value:60},{subject:'C',value:90},{subject:'D',value:70}]} />
                </td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-xs ${c.match > 80 ? 'bg-green-500/20 text-green-400' : c.match > 60 ? 'bg-yellow-500/20 text-yellow-400' : 'bg-red-500/20 text-red-400'}`}>
                    {c.match}%
                  </span>
                </td>
                <td className="p-4">
                  <button className="p-2 hover:bg-white/10 rounded-lg text-gray-400 hover:text-white transition-colors">
                    <MoreHorizontal className="w-5 h-5" />
                  </button>
                </td>
              </motion.tr>
            ))}
          </motion.tbody>
        </table>
      </div>
    </div>
  );
};

export default MultiCompare;
