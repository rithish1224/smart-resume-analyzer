import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';

const UploadPanel = ({ onUploadComplete }) => {
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, uploading, success, error

  const onDrop = useCallback(acceptedFiles => {
    setError(null);
    if (acceptedFiles.length === 0) return;
    
    const selectedFile = acceptedFiles[0];
    
    if (selectedFile.size > 1048576) {
      setError('File too large. Maximum size is 1 MB.');
      setStatus('error');
      return;
    }
    
    setFile(selectedFile);
    setStatus('uploading');
    setProgress(0);
    
    // Simulate upload
    const interval = setInterval(() => {
      setProgress(p => {
        if (p >= 100) {
          clearInterval(interval);
          setStatus('success');
          setTimeout(() => {
            onUploadComplete?.(selectedFile);
          }, 1000);
          return 100;
        }
        return p + 10;
      });
    }, 200);
  }, [onUploadComplete]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({ 
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png']
    },
    maxFiles: 1
  });

  const getFileIconColor = (type) => {
    if (!type) return 'text-gray-400';
    if (type.includes('pdf')) return 'text-red-500';
    if (type.includes('word')) return 'text-blue-500';
    if (type.includes('image')) return 'text-green-500';
    return 'text-gray-400';
  };

  const isImage = file?.type?.startsWith('image/');

  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-white/5 border border-white/10 rounded-3xl backdrop-blur-xl">
      <motion.div
        {...getRootProps()}
        whileHover={{ scale: status === 'idle' ? 1.02 : 1 }}
        animate={{ scale: isDragActive ? 1.05 : 1 }}
        className={`relative overflow-hidden cursor-pointer rounded-2xl border-2 border-dashed p-10 flex flex-col items-center justify-center transition-colors
          ${isDragReject ? 'border-red-500/50 bg-red-500/5' : 
            isDragActive ? 'border-indigo-500/50 bg-indigo-500/5' : 
            'border-white/20 hover:border-indigo-500/30'}`}
      >
        <input {...getInputProps()} />
        
        {isDragActive && (
           <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-cyan-500/10 animate-pulse pointer-events-none" />
        )}

        <AnimatePresence mode="wait">
          {status === 'idle' && (
            <motion.div
              key="idle"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="text-center"
            >
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-white/5 flex items-center justify-center border border-white/10">
                <svg className="w-8 h-8 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <h3 className="text-xl font-medium text-white mb-2">Drag & drop your file here</h3>
              <p className="text-gray-400 text-sm">or click to browse from your computer</p>
            </motion.div>
          )}

          {(status === 'uploading' || status === 'success') && file && (
            <motion.div
              key="uploading"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="w-full max-w-md text-center"
            >
              <div className="flex items-center justify-center gap-4 mb-6">
                <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center border border-white/10">
                  <svg className={`w-6 h-6 ${getFileIconColor(file.type)}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div className="text-left flex-1 overflow-hidden">
                  <p className="text-white font-medium truncate">{file.name}</p>
                  <p className="text-gray-400 text-xs">{(file.size / 1024).toFixed(1)} KB</p>
                </div>
                {status === 'success' && (
                  <motion.div 
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center"
                  >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                    </svg>
                  </motion.div>
                )}
              </div>
              
              <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden mb-2">
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  className="h-full bg-indigo-500 rounded-full"
                />
              </div>
              <p className="text-xs text-indigo-400 font-medium">{progress}% Uploaded</p>
            </motion.div>
          )}

          {status === 'error' && (
            <motion.div
              key="error"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center"
            >
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/10 flex items-center justify-center text-red-500">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <h3 className="text-xl font-medium text-red-400 mb-2">Upload Failed</h3>
              <p className="text-gray-400 text-sm mb-4">{error}</p>
              <button 
                onClick={(e) => { e.stopPropagation(); setStatus('idle'); setError(null); }}
                className="px-4 py-2 rounded-lg bg-white/10 text-white text-sm hover:bg-white/20 transition-colors"
              >
                Try Again
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      <div className="mt-6 p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-200 text-sm">
        <p className="flex items-start gap-2">
          <svg className="w-5 h-5 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Upload PDF, DOCX, TXT, JPG, JPEG, or PNG files. Keep files under 1 MB for best results. For images, make sure the text is clear and readable.</span>
        </p>
      </div>

      {isImage && (
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-200 text-sm"
        >
          <p className="flex items-start gap-2">
            <svg className="w-5 h-5 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>For best OCR results, use clear, well-lit, high-resolution images.</span>
          </p>
        </motion.div>
      )}
    </div>
  );
};

export default UploadPanel;
