import { useState, useCallback, useEffect } from 'react';

export function useImprovement() {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [trendingKeywords, setTrendingKeywords] = useState([]);
  const [knownCompanies, setKnownCompanies] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchCompanies = useCallback(async () => {
    try {
      // Mocked fetch
      // const res = await fetch('/api/improve/company-profiles');
      // const data = await res.json();
      setKnownCompanies(['Google', 'Amazon', 'Microsoft', 'Meta', 'Netflix', 'Apple']);
    } catch (err) {
      console.error(err);
    }
  }, []);

  useEffect(() => {
    fetchCompanies();
  }, [fetchCompanies]);

  const analyzeResume = async ({ fileId, domain, company, aiEnabled }) => {
    setIsLoading(true);
    setError(null);
    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockResult = {
        id: 'analysis_123',
        domain,
        company,
        atsScore: 68,
        passRateEstimate: 'Medium Chance',
        atsIssues: ['Inconsistent date formats', 'Missing address/location'],
        missingSections: ['Certifications', 'Projects'],
        bulletScore: 72,
        weakBullets: [
          'Worked on backend API using Node.js',
          'Helped the team with debugging'
        ],
        strongRewrites: [
          { text: 'Engineered scalable backend REST APIs using Node.js, improving response times by 20%', reason: 'Adds quantifiable metric and stronger action verb' },
          { text: 'Resolved 50+ critical bugs during beta phase, ensuring on-time product launch', reason: 'Quantifies contribution and business impact' }
        ],
        keywordGaps: ['Docker', 'AWS', 'CI/CD'],
        keywordScore: 80,
        quantificationScore: 35,
        generalSuggestions: [
          { id: 'g1', title: 'Add a summary', description: 'Include a 2-3 sentence professional summary at the top.', icon: '📝' },
          { id: 'g2', title: 'Standardize dates', description: 'Use MM/YYYY format consistently throughout.', icon: '📅' }
        ],
        domainSuggestions: [
          { id: 'd1', title: 'Highlight Cloud Skills', description: 'Move cloud technologies higher up in skills.', icon: '☁️', priority: 'High' }
        ],
        companySuggestions: company ? [
          { id: 'c1', title: 'Leadership Principles', description: `Incorporate more action verbs reflecting ${company}'s core values.`, icon: '🏢' }
        ] : [],
        priorityActions: [
          'Fix inconsistent date formats (ATS issue)',
          'Quantify your bullet points (current: 35%)',
          'Add missing Projects section'
        ]
      };
      
      setAnalysisResult(mockResult);
    } catch (err) {
      setError(err.message || 'Failed to analyze resume');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchTrendingKeywords = async (domain) => {
    try {
      // Mock API call
      setTrendingKeywords(['TypeScript', 'React', 'GraphQL', 'Next.js', 'Tailwind CSS', 'PostgreSQL']);
    } catch (err) {
      console.error(err);
    }
  };

  const submitFeedback = async (feedback) => {
    try {
      console.log('Feedback submitted:', feedback);
      // await fetch('/api/improve/feedback', { method: 'POST', body: JSON.stringify(feedback) })
    } catch (err) {
      console.error(err);
    }
  };

  return {
    analysisResult,
    trendingKeywords,
    knownCompanies,
    isLoading,
    error,
    analyzeResume,
    submitFeedback,
    fetchTrendingKeywords,
    fetchCompanies
  };
}
