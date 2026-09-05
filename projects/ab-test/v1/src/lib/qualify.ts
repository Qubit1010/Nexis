import { getDb } from './db';
import { rescoreAll } from './leads';
import { getBands, listRules, replaceRules, setBands } from './rules';
import type { Bands, Rule, RuleInput } from '@/types';

export interface SaveRuleSetResult {
  rules: Rule[];
  bands: Bands;
  rescored: number;
}

/**
 * The one operation that couples the two tables: swapping the rule set invalidates every
 * stored score, so both happen inside a single transaction. A half-applied save would
 * leave leads scored by rules that no longer exist.
 */
export function saveRuleSet(inputs: RuleInput[], bands: Bands): SaveRuleSetResult {
  const db = getDb();
  db.exec('BEGIN IMMEDIATE');
  try {
    replaceRules(inputs);
    setBands(bands);
    const rescored = rescoreAll();
    db.exec('COMMIT');
    return { rules: listRules(), bands: getBands(), rescored };
  } catch (error) {
    db.exec('ROLLBACK');
    throw error;
  }
}
