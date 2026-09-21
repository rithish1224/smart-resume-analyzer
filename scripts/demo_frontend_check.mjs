import fs from 'node:fs';
import path from 'node:path';

const responseDir = path.resolve('scripts/demo_responses');
const cases = ['good', 'mediocre', 'unrelated'];

for (const name of cases) {
  const data = JSON.parse(fs.readFileSync(path.join(responseDir, `${name}.json`), 'utf8'));
  for (const field of ['matched_skills', 'missing_skills', 'related_skills']) {
    if (!Array.isArray(data[field])) throw new Error(`${name}: missing ${field}`);
  }
  const counts = {
    matched: data.matched_skills.length,
    missing: data.missing_skills.length,
    related: data.related_skills.length,
  };
  if (data.ui_counts?.matched !== counts.matched ||
      data.ui_counts?.missing !== counts.missing ||
      data.ui_counts?.related !== counts.related) {
    throw new Error(`${name}: rendered counts do not match saved API response`);
  }
  console.log(`${name}: matched=${counts.matched} missing=${counts.missing} related=${counts.related}`);
}
console.log('PASS: frontend skill counts match saved /api/analyze responses');
