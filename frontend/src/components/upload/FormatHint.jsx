import React from 'react';

const FormatHint = () => {
  const formats = [
    { label: 'PDF', color: 'text-red-400 bg-red-500/10 border-red-500/20' },
    { label: 'DOCX', color: 'text-blue-400 bg-blue-500/10 border-blue-500/20' },
    { label: 'TXT', color: 'text-gray-400 bg-gray-500/10 border-gray-500/20' },
    { label: 'JPG', color: 'text-green-400 bg-green-500/10 border-green-500/20' },
    { label: 'PNG', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' }
  ];

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="flex flex-wrap justify-center gap-2">
        {formats.map(format => (
          <span 
            key={format.label}
            className={`px-3 py-1 text-xs font-medium rounded-full border ${format.color}`}
          >
            {format.label}
          </span>
        ))}
      </div>
      <p className="text-xs text-gray-400">
        Max 1 MB. Images must be clear and readable.
      </p>
    </div>
  );
};

export default FormatHint;
