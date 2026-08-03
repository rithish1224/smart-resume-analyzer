import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function FeedbackCollector({ suggestions = [], onSubmit, analysisId }) {
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [helpful, setHelpful] = useState(true);
  const [actedOn, setActedOn] = useState(new Set());
  const [comments, setComments] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const toggleActed = (id) => {
    const next = new Set(actedOn);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setActedOn(next);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      analysisId,
      rating,
      helpful,
      actedOn: Array.from(actedOn),
      comments
    });
    setSubmitted(true);
  };

  if (submitted) {
    return (
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="p-6 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-center"
      >
        <div className="text-4xl mb-3">🎉</div>
        <h3 className="text-xl font-bold text-emerald-400 mb-2">Thank you!</h3>
        <p className="text-emerald-200/80 text-sm">Your feedback helps our AI learn and improve recommendations.</p>
      </motion.div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 rounded-2xl backdrop-blur-xl bg-[#111122] border border-white/10"
    >
      <h3 className="text-lg font-semibold text-gray-200 mb-4">How did we do?</h3>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <p className="text-sm text-gray-400 mb-2">Rate these suggestions</p>
          <div className="flex gap-2">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                onClick={() => setRating(star)}
                onMouseEnter={() => setHoverRating(star)}
                onMouseLeave={() => setHoverRating(0)}
                className="text-2xl focus:outline-none transition-transform hover:scale-110"
              >
                <span className={(hoverRating || rating) >= star ? "text-amber-400" : "text-gray-600"}>
                  ★
                </span>
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/5">
          <span className="text-sm text-gray-300">Were these suggestions helpful?</span>
          <button
            type="button"
            onClick={() => setHelpful(!helpful)}
            className={`w-12 h-6 rounded-full p-1 transition-colors ${helpful ? 'bg-indigo-500' : 'bg-gray-600'}`}
          >
            <motion.div
              className="w-4 h-4 bg-white rounded-full"
              animate={{ x: helpful ? 24 : 0 }}
            />
          </button>
        </div>

        {suggestions.length > 0 && (
          <div>
            <p className="text-sm text-gray-400 mb-3">Which suggestions did you act on?</p>
            <div className="space-y-2 max-h-32 overflow-y-auto pr-2 custom-scrollbar">
              {suggestions.map((s) => (
                <label key={s.id} className="flex items-start gap-3 cursor-pointer group">
                  <input 
                    type="checkbox"
                    checked={actedOn.has(s.id)}
                    onChange={() => toggleActed(s.id)}
                    className="mt-1 shrink-0 w-4 h-4 rounded border-gray-600 text-indigo-500 focus:ring-indigo-500 bg-gray-800"
                  />
                  <span className="text-sm text-gray-300 group-hover:text-white transition-colors">
                    {s.title}
                  </span>
                </label>
              ))}
            </div>
          </div>
        )}

        <div>
          <textarea
            className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-sm text-white placeholder-gray-500 focus:ring-2 focus:ring-indigo-500 outline-none resize-none"
            rows="3"
            placeholder="Any comments? (optional)"
            value={comments}
            onChange={(e) => setComments(e.target.value)}
          />
        </div>

        <button
          type="submit"
          disabled={!rating}
          className="w-full py-3 rounded-xl bg-white/10 hover:bg-white/20 text-white font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Submit Feedback
        </button>
        <p className="text-center text-xs text-gray-500">🤖 Your feedback helps our AI learn and improve recommendations</p>
      </form>
    </motion.div>
  );
}
