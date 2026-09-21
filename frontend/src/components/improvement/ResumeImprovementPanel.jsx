import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import CompanyTargeting from './CompanyTargeting';
import ATSScoreCard from './ATSScoreCard';
import BulletImprover from './BulletImprover';
import KeywordAnalysis from './KeywordAnalysis';
import SuggestionPanel from './SuggestionPanel';
import FeedbackCollector from './FeedbackCollector';
import { useImprovement } from '../../hooks/useImprovement';
import DemoDataBanner from '../common/DemoDataBanner';

export default function ResumeImprovementPanel({ fileId }) {
  const { 
    analysisResult, 
    trendingKeywords, 
    knownCompanies, 
    isLoading, 
    analyzeResume, 
    submitFeedback,
    fetchTrendingKeywords
  } = useImprovement();

  const handleTargetingSubmit = async ({ domain, company, aiEnabled }) => {
    fetchTrendingKeywords(domain);
    await analyzeResume({ fileId, domain, company, aiEnabled });
  };

  return (
    <div className="max-w-6xl mx-auto py-8 space-y-8">
      <DemoDataBanner />
      <div className="text-center mb-10">
        <h1 className="text-4xl font-extrabold mb-3 bg-gradient-to-r from-indigo-400 via-violet-400 to-cyan-400 bg-clip-text text-transparent">
          📝 Resume Improvement Module
        </h1>
        <p className="text-lg text-gray-400">AI-powered truthful resume coaching</p>
      </div>

      {!analysisResult && (
        <div className="max-w-2xl mx-auto">
          <CompanyTargeting 
            onSubmit={handleTargetingSubmit} 
            isLoading={isLoading} 
            knownCompanies={knownCompanies} 
          />
        </div>
      )}

      {isLoading && !analysisResult && (
        <motion.div 
          initial={{ opacity: 0 }} 
          animate={{ opacity: 1 }} 
          className="max-w-2xl mx-auto p-6 rounded-2xl backdrop-blur-xl bg-white/5 border border-white/10 space-y-4"
        >
          <div className="h-8 bg-white/10 rounded w-1/3 animate-pulse" />
          <div className="h-4 bg-white/5 rounded w-full animate-pulse" />
          <div className="h-4 bg-white/5 rounded w-5/6 animate-pulse" />
          <div className="h-32 bg-white/5 rounded w-full animate-pulse mt-6" />
        </motion.div>
      )}

      <AnimatePresence>
        {analysisResult && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-8"
          >
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-1">
                <ATSScoreCard 
                  atsScore={analysisResult.atsScore} 
                  passRateEstimate={analysisResult.passRateEstimate} 
                  issues={analysisResult.atsIssues} 
                />
              </div>
              <div className="lg:col-span-2">
                <div className="p-6 rounded-2xl backdrop-blur-xl bg-amber-500/10 border border-amber-500/20 h-full flex flex-col justify-center">
                  <h3 className="text-amber-400 font-bold mb-2 flex items-center gap-2">
                    <span>⚠️</span> Missing Sections
                  </h3>
                  {analysisResult.missingSections?.length > 0 ? (
                    <ul className="list-disc pl-5 text-amber-200/80 space-y-1">
                      {analysisResult.missingSections.map((sec, i) => <li key={i}>{sec}</li>)}
                    </ul>
                  ) : (
                    <p className="text-amber-200/80">All standard sections are present.</p>
                  )}
                </div>
              </div>
            </div>

            <BulletImprover 
              bulletScore={analysisResult.bulletScore} 
              weakBullets={analysisResult.weakBullets} 
              strongRewrites={analysisResult.strongRewrites} 
            />

            <KeywordAnalysis 
              keywordGaps={analysisResult.keywordGaps} 
              keywordScore={analysisResult.keywordScore} 
              quantificationScore={analysisResult.quantificationScore} 
              trendingKeywords={trendingKeywords} 
              domain={analysisResult.domain} 
            />

            <SuggestionPanel 
              generalSuggestions={analysisResult.generalSuggestions} 
              domainSuggestions={analysisResult.domainSuggestions} 
              companySuggestions={analysisResult.companySuggestions} 
              company={analysisResult.company} 
              domain={analysisResult.domain} 
              priorityActions={analysisResult.priorityActions} 
            />

            <div className="max-w-md mx-auto">
              <FeedbackCollector 
                suggestions={[...analysisResult.generalSuggestions, ...analysisResult.domainSuggestions, ...(analysisResult.companySuggestions || [])]}
                onSubmit={submitFeedback}
                analysisId={analysisResult.id}
              />
            </div>
            
            <div className="flex flex-col items-center justify-center gap-4 mt-12 pb-8 text-sm text-gray-500">
              <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10">
                <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                Suggestions enhanced by: <span className="font-semibold text-gray-300">OpenAI GPT-4</span>
              </div>
              <p>⚠️ These suggestions are based on your actual resume content. We never suggest adding skills or experience you do not have.</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
