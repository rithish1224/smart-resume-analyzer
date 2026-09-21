// Bands are score-distribution cut points from validation: top 25%, next 25%.
export const DECISION_BANDS = {
  strong: 75,
  possible: 50,
};

export function getMatchBand(score) {
  if (score >= DECISION_BANDS.strong) return 'Strong';
  if (score >= DECISION_BANDS.possible) return 'Possible';
  return 'Weak';
}
