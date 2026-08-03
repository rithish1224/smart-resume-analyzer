import { useState, useCallback } from 'react';

export const useUpload = () => {
  const [file, setFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFileId, setUploadedFileId] = useState(null);
  const [error, setError] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  const uploadFile = useCallback(async (selectedFile) => {
    if (!selectedFile) return;
    
    // Basic validation
    if (!selectedFile.name.endsWith('.pdf') && !selectedFile.name.endsWith('.docx')) {
      setError('Only PDF and DOCX files are supported');
      return;
    }
    if (selectedFile.size > 5 * 1024 * 1024) {
      setError('File size must be under 5MB');
      return;
    }

    setFile(selectedFile);
    setIsUploading(true);
    setError(null);
    setUploadProgress(0);

    try {
      // Simulate file upload with progress
      for (let i = 10; i <= 100; i += 20) {
        await new Promise(r => setTimeout(r, 200));
        setUploadProgress(i);
      }
      
      // Simulate backend response
      setUploadedFileId('res_' + Math.random().toString(36).substring(7));
      
    } catch (err) {
      setError('Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  }, []);

  const resetUpload = useCallback(() => {
    setFile(null);
    setUploadProgress(0);
    setUploadedFileId(null);
    setError(null);
    setIsUploading(false);
  }, []);

  return { file, uploadProgress, uploadedFileId, error, isUploading, uploadFile, resetUpload };
};
