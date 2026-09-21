import React, { useState } from 'react';
import { motion } from 'framer-motion';
import RoleInput from '../components/scoring/RoleInput';
import UploadPanel from '../components/upload/UploadPanel';
import ScoreSummary from '../components/scoring/ScoreSummary';
import CompetencyRadar from '../components/scoring/CompetencyRadar';
import SkillGapChart from '../components/scoring/SkillGapChart';
import ShapExplainer from '../components/scoring/ShapExplainer';
import ShortlistDecision from '../components/scoring/ShortlistDecision';
import toast from 'react-hot-toast';
import { analyzeApi } from '../api/client';

const Analyze = () => {
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [resumeFile, setResumeFile] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisError, setAnalysisError] = useState(null);

  const loadingSteps = ['Parsing resume...', 'Extracting skills...', 'Running XGBoost...', 'Computing SHAP...', 'Done!'];

  const handleAnalyze = async ({ role, jd }) => {
    if (!resumeFile) {
      toast.error('Please upload a resume first.');
      setStep(1);
      return;
    }
    setIsLoading(true);
    setAnalysisError(null);
    setStep(3);
    setLoadingStep(0);
    try {
      const { data } = await analyzeApi.analyze(resumeFile, jd, role);
      setAnalysisResult(data);
      setStep(4);
    } catch (error) {
      setAnalysisError(error.response?.data?.detail || 'Analysis failed. Please check the resume.');
      toast.error(error.response?.data?.detail || 'Analysis failed. Please check the resume.');
      setStep(2);
    } finally {
      setIsLoading(false);
    }
  };

  const displayData = analysisResult ? {
    score: analysisResult.fit_score,
    confidence: analysisResult.confidence,
    modelVersion: analysisResult.model_version,
    competencyScores: analysisResult.competency_scores,
    shapData: {
      features: [...(analysisResult.shap_top_positive || []), ...(analysisResult.shap_top_negative || [])]
        .filter((item) => !['jd_chars', 'jd_skill_count', 'required_years', 'resume_chars'].includes(item.feature))
        .filter((item, index, all) => all.findIndex(other => other.feature === item.feature) === index)
        .map((item) => ({ name: item.feature, contribution: item.value, evidence: '' })),
    },
  } : null;

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
              {analysisError && <div className="mb-4 rounded-xl border border-red-400/40 bg-red-500/10 p-4 text-sm text-red-200">{analysisError}</div>}
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
                      <p className="text-slate-400 text-sm mt-1">Model evidence, skill coverage, and review support.</p>
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
                          modelVersion={displayData.modelVersion} 
                        />
                    </div>
                    <div className="md:col-span-2">
                        <CompetencyRadar 
                          competencyScores={displayData.competencyScores} 
                        />
                    </div>

                    {/* Row 2: Skill Gap Chart */}
                    <div className="md:col-span-3 min-h-[300px]">
                        <SkillGapChart
                          matchedSkills={analysisResult.matched_skills}
                          missingSkills={analysisResult.missing_skills}
                          relatedSkills={analysisResult.related_skills}
                        />
                    </div>

                    {/* Row 3: SHAP Explainer & Shortlist Recommendation */}
                    <div className="md:col-span-2">
                        <ShapExplainer shapData={displayData.shapData} />
                    </div>
                    <div className="md:col-span-1">
                        <ShortlistDecision />
                    </div>

                    {/* Row 4: Fairness Audit */}
                    <div className="md:col-span-3 p-6 rounded-3xl backdrop-blur-xl bg-white/5 border border-white/10">
                        <h3 className="text-lg font-outfit font-bold text-white mb-4">Fairness & Algorithmic Audit</h3>
                        <p className="text-slate-300">Not computed for this model yet.</p>
                    </div>

                    {/* Row 5: Improvement Roadmap */}
                    <div className="md:col-span-3 p-6 rounded-3xl backdrop-blur-xl bg-white/5 border border-white/10">
                         <h3 className="text-lg font-outfit font-bold text-white mb-4">Improvement suggestions</h3>
                         {(analysisResult.improvement_suggestions || []).length ? (
                           <ul className="list-disc pl-5 text-gray-300 space-y-2 text-sm">
                             {analysisResult.improvement_suggestions.map((suggestion, index) => <li key={index}>{suggestion}</li>)}
                           </ul>
                         ) : <p className="text-slate-400 text-sm">No improvement suggestions were returned.</p>}
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
