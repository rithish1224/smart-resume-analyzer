import bands from './bands.json';

export const DECISION_BANDS = bands.thresholds;

export function getMatchBand(score) {
  if (score >= DECISION_BANDS.strong) return 'Strong';
  if (score >= DECISION_BANDS.possible) return 'Possible';
  return 'Weak';
}
