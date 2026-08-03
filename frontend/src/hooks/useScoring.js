import { useState, useCallback } from 'react';

export const useScoring = () => {
  const [fileId, setFileId] = useState(null);
  const [profile, setProfile] = useState(null);
  const [score, setScore] = useState(null);
  const [shapData, setShapData] = useState(null);
  const [skillGaps, setSkillGaps] = useState(null);
  const [fairness, setFairness] = useState(null);
  const [roadmap, setRoadmap] = useState(null);
  const [step, setStep] = useState('idle'); // idle, uploading, parsing, scoring, generating_roadmap, done
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const runScoringFlow = useCallback(async (uploadedFileId) => {
    setFileId(uploadedFileId);
    setStep('scoring');
    setIsLoading(true);
    setError(null);

    try {
      // Simulate SSE progress for /score endpoint
      await new Promise(r => setTimeout(r, 1000));
      setStep('parsing');
      
      await new Promise(r => setTimeout(r, 1500));
      
      // Mock result
      setProfile({ name: 'Alex Doe', role: 'Frontend Developer', parsedSkills: ['React', 'JavaScript', 'CSS'] });
      setScore(85);
      setShapData([{ feature: 'React Exp', contribution: 0.4 }, { feature: 'JS Skills', contribution: 0.3 }]);
      setSkillGaps([{ skill: 'TypeScript', gap: 'High' }, { skill: 'GraphQL', gap: 'Medium' }]);
      setFairness({ dir: 0.9, dp: 0.05, eo: { tprGap: 0.02, fprGap: 0.03 }, verdict: 'FAIR' });
      
      setStep('generating_roadmap');
      await new Promise(r => setTimeout(r, 1500));
      
      setRoadmap({
        provider: 'openai',
        milestones: [
          { timeframe: '30 Days', focus: 'TypeScript Basics', skills: [{ name: 'TS types', difficulty: 'Beginner', estimatedHours: 10, type: 'course' }] }
        ]
      });
      
      setStep('done');
    } catch (err) {
      setError('Scoring failed: ' + err.message);
      setStep('error');
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    fileId, profile, score, shapData, skillGaps, fairness, roadmap, step, isLoading, error, runScoringFlow
  };
};
