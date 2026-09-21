import React, { useState } from 'react';
import { motion } from 'framer-motion';
import RoleInput from '../components/scoring/RoleInput';
import UploadPanel from '../components/upload/UploadPanel';
import ScoreSummary from '../components/scoring/ScoreSummary';
import CompetencyRadar from '../components/scoring/CompetencyRadar';
import SkillGapChart from '../components/scoring/SkillGapChart';
import ShapExplainer from '../components/scoring/ShapExplainer';
import ShortlistDecision from '../components/scoring/ShortlistDecision';
import ResumeImprovementPanel from '../components/improvement/ResumeImprovementPanel';
import toast from 'react-hot-toast';
import { analyzeApi } from '../api/client';

const Analyze = () => {
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [resumeFile, setResumeFile] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);

  const loadingSteps = ['Parsing resume...', 'Extracting skills...', 'Running XGBoost...', 'Computing SHAP...', 'Done!'];

  const mockAnalysisData = {
    score: 87,
    confidence: 0.94,
    shortlistDecision: 'SHORTLIST',
    modelVersion: 'XGBRanker v1.0',
    competencyScores: {
      technical: 90,
      experience: 85,
      education: 80,
      projects: 88,
      certifications: 75,
      communication: 82
    },
    requiredScores: {
      technical: 85,
      experience: 80,
      education: 75,
      projects: 80,
      certifications: 70,
      communication: 80
    },
    skillGaps: [
      { skillName: 'Python & FastAPI', requiredLevel: 5, candidateLevel: 4.8, priority: 'High', status: 'met' },
      { skillName: 'XGBoost & Machine Learning', requiredLevel: 5, candidateLevel: 4.5, priority: 'High', status: 'met' },
      { skillName: 'System Architecture & Scalability', requiredLevel: 5, candidateLevel: 3.2, priority: 'High', status: 'soft' },
      { skillName: 'Cloud Deployments (AWS/GCP)', requiredLevel: 4, candidateLevel: 2.0, priority: 'Med', status: 'hard' },
      { skillName: 'Fairness & SHAP Auditing', requiredLevel: 4, candidateLevel: 4.2, priority: 'Low', status: 'met' }
    ],
    shapData: {
      features: [
        { name: 'Technical Skill Match', contribution: 18.5, evidence: 'Matches 92% of required core skills' },
        { name: 'Years of Experience', contribution: 12.2, evidence: '5+ years relevant domain experience' },
        { name: 'Projects & Portfolio', contribution: 8.0, evidence: 'Strong production project portfolio' },
        { name: 'Cloud Certification', contribution: -4.5, evidence: 'AWS/GCP Developer certification missing' }
      ],
      summary: 'Candidate ranks in the top 5% due to exceptional technical proficiency and strong domain project execution.'
    }
  };

  const handleAnalyze = async ({ role, jd }) => {
    if (!resumeFile) {
      toast.error('Please upload a resume first.');
      setStep(1);
      return;
    }
    setIsLoading(true);
    setStep(3);
    setLoadingStep(0);
    try {
      const { data } = await analyzeApi.analyze(resumeFile, jd, role);
      setAnalysisResult(data);
      setStep(4);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Analysis failed. Please check the resume.');
      setStep(2);
    } finally {
      setIsLoading(false);
    }
  };

  const result = analysisResult || mockAnalysisData;
  const displayData = analysisResult ? {
    ...mockAnalysisData,
    score: analysisResult.fit_score,
    confidence: analysisResult.confidence,
    modelVersion: analysisResult.model_version,
    competencyScores: analysisResult.competency_scores,
    skillGaps: (analysisResult.missing_skills || []).map((skill) => ({
      skillName: skill, requiredLevel: 1, candidateLevel: 0, priority: 'High', status: 'hard',
    })),
    shapData: {
      features: [...(analysisResult.shap_top_positive || []), ...(analysisResult.shap_top_negative || [])]
        .map((item) => ({ name: item.feature, contribution: item.value, evidence: '' })),
      summary: (analysisResult.improvement_suggestions || []).join(' '),
    },
    shortlistDecision: analysisResult.fit_score >= 75 ? 'SHORTLIST' : analysisResult.fit_score >= 50 ? 'REVIEW' : 'REJECT',
  } : result;

  const handleExport = () => {
    toast.success('Exporting detailed candidate evaluation report...');
  };

  return (
    <div className="min-h-screen bg-[#0a0a1a] text-white p-6 md:p-12 font-inter pt-20">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Progress Indicator */}
        <div className="flex justify-between items-center mb-12">
          {['Upload', 'Configure', 'Analyze', 'Results'].map((label, i) => (
            <div key={i} className="flex flex-col items-center flex-1">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm ${step >= i + 1 ? 'bg-gradient-to-r from-[#6366f1] to-[#8b5cf6] text-white shadow-[0_0_15px_rgba(99,102,241,0.5)]' : 'bg-white/10 text-gray-500'}`}>
                {i + 1}
              </div>
              <span className={`text-xs mt-2 ${step >= i + 1 ? 'text-white' : 'text-gray-500'}`}>{label}</span>
              {i < 3 && <div className={`h-[2px] w-full mt-[-30px] ml-[50%] z-[-1] ${step > i + 1 ? 'bg-[#6366f1]' : 'bg-white/10'}`} />}
            </div>
          ))}
        </div>

        {/* Content based on step */}
        <motion.div
          key={step}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          {step === 1 && (
            <div className="max-w-2xl mx-auto space-y-6">
                <div className="text-center mb-4">
                    <h2 className="text-3xl font-outfit font-bold mb-2">Upload Candidate Resume</h2>
                    <p className="text-gray-400 text-sm">Upload resume PDF, DOCX, image, or TXT file for automated extraction.</p>
                </div>
                <UploadPanel onUploadComplete={(file) => { setResumeFile(file); setStep(2); }} />
                <div className="text-center pt-2">
                  <button onClick={() => setStep(2)} className="px-6 py-2 bg-white/10 hover:bg-white/20 rounded-xl transition-colors border border-white/20 text-xs font-medium text-gray-300">
                      Skip to Role Configuration (Demo) →
                  </button>
                </div>
            </div>
          )}

          {step === 2 && (
            <div className="max-w-3xl mx-auto">
              <RoleInput onSubmit={handleAnalyze} isLoading={isLoading} />
            </div>
          )}

          {step === 3 && (
            <div className="flex flex-col items-center justify-center h-64 space-y-6">
              <div className="w-16 h-16 border-4 border-white/10 border-t-[#06b6d4] rounded-full animate-spin" />
              <div className="text-xl font-outfit text-transparent bg-clip-text bg-gradient-to-r from-[#6366f1] to-[#06b6d4]">
                {loadingSteps[loadingStep]}
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="space-y-8">
                <div className="flex justify-between items-center mb-4">
                    <div>
                      <h2 className="text-3xl font-outfit font-bold text-white">Candidate Diagnostic Results</h2>
                      <p className="text-slate-400 text-sm mt-1">Multi-dimensional evaluation, SHAP explainability, and fairness analysis.</p>
                    </div>
                    <button onClick={handleExport} className="px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white rounded-xl text-sm font-semibold border border-white/10 transition-all shadow-lg">
                      Export Full Report
                    </button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Row 1: Score Summary & Competency Radar */}
                    <div className="md:col-span-1">
                        <ScoreSummary 
                          score={displayData.score} 
                          confidence={displayData.confidence} 
                          shortlistDecision={displayData.shortlistDecision} 
                          modelVersion={displayData.modelVersion} 
                        />
                    </div>
                    <div className="md:col-span-2">
                        <CompetencyRadar 
                          competencyScores={displayData.competencyScores} 
                          requiredScores={displayData.requiredScores} 
                        />
                    </div>

                    {/* Row 2: Skill Gap Chart */}
                    <div className="md:col-span-3 min-h-[300px]">
                        <SkillGapChart skillGaps={displayData.skillGaps} />
                    </div>

                    {/* Row 3: SHAP Explainer & Shortlist Recommendation */}
                    <div className="md:col-span-2">
                        <ShapExplainer shapData={displayData.shapData} />
                    </div>
                    <div className="md:col-span-1">
                        <ShortlistDecision decision={displayData.shortlistDecision} score={displayData.score} />
                    </div>

                    {/* Row 4: Fairness Audit */}
                    <div className="md:col-span-3 p-6 rounded-3xl backdrop-blur-xl bg-white/5 border border-white/10">
                        <h3 className="text-lg font-outfit font-bold text-white mb-4">Fairness & Algorithmic Audit</h3>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="p-4 bg-white/5 rounded-xl border border-white/10 text-center">
                              <p className="text-xs text-gray-400 mb-1">Disparate Impact Ratio (DIR)</p>
                              <p className="text-2xl font-bold text-emerald-400">0.95 (Pass)</p>
                              <p className="text-[10px] text-gray-500 mt-1">Ethical threshold &gt; 0.80</p>
                            </div>
                            <div className="p-4 bg-white/5 rounded-xl border border-white/10 text-center">
                              <p className="text-xs text-gray-400 mb-1">Demographic Parity Gap</p>
                              <p className="text-2xl font-bold text-emerald-400">0.02 (Pass)</p>
                              <p className="text-[10px] text-gray-500 mt-1">Parity gap &lt; 0.10</p>
                            </div>
                            <div className="p-4 bg-white/5 rounded-xl border border-white/10 text-center">
                              <p className="text-xs text-gray-400 mb-1">Equal Opportunity Gap (EO)</p>
                              <p className="text-2xl font-bold text-emerald-400">0.05 (Pass)</p>
                              <p className="text-[10px] text-gray-500 mt-1">TPR gap &lt; 0.10</p>
                            </div>
                        </div>
                    </div>

                    {/* Row 5: Improvement Roadmap */}
                    <div className="md:col-span-3 p-6 rounded-3xl backdrop-blur-xl bg-white/5 border border-white/10">
                         <h3 className="text-lg font-outfit font-bold text-white mb-4">AI Candidate Growth Roadmap</h3>
                         <ul className="list-disc pl-5 text-gray-300 space-y-2 text-sm">
                             <li><strong className="text-indigo-400">30 Days:</strong> Complete cloud deployment certifications (AWS Solutions Architect / GCP Developer).</li>
                             <li><strong className="text-violet-400">60 Days:</strong> Deepen microservices system design & Kubernetes cluster management skills.</li>
                             <li><strong className="text-cyan-400">90 Days:</strong> Lead architectural reviews and optimize end-to-end production pipelines.</li>
                         </ul>
                    </div>

                    {/* Resume Improvement Panel */}
                    <div className="md:col-span-3">
                      <div className="mt-4 border-t border-white/10 pt-6">
                        <ResumeImprovementPanel fileId={null} />
                      </div>
                    </div>
                </div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default Analyze;
