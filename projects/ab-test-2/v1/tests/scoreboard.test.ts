import { beforeEach, describe, expect, it } from 'vitest';

import type { Db } from '../server/db.ts';
import {
  createEnquiry,
  createPromptVersion,
  insertDraft,
  openDb,
  updateDraft,
} from '../server/db.ts';
import { MIN_SAMPLE, buildScoreboard, wilsonInterval } from '../server/scoreboard.ts';

describe('wilsonInterval', () => {
  it('returns null with no trials', () => {
    expect(wilsonInterval(0, 0)).toBeNull();
  });

  it('does NOT report certainty from a single success', () => {
    // The entire reason this function exists. A naive rate would say 100%.
    const interval = wilsonInterval(1, 1);
    expect(interval).not.toBeNull();
    expect(interval?.low).toBeLessThan(0.5);
    expect(interval?.high).toBeCloseTo(1, 5);
  });

  it('does not collapse at zero successes either', () => {
    const interval = wilsonInterval(0, 1);
    expect(interval?.low).toBeCloseTo(0, 5);
    expect(interval?.high).toBeGreaterThan(0.5);
  });

  it('narrows as the sample grows at a constant rate', () => {
    const small = wilsonInterval(8, 10);
    const large = wilsonInterval(80, 100);
    const smallWidth = (small?.high ?? 0) - (small?.low ?? 0);
    const largeWidth = (large?.high ?? 0) - (large?.low ?? 0);
    expect(largeWidth).toBeLessThan(smallWidth);
  });

  it('stays inside [0, 1]', () => {
    for (const [good, total] of [
      [0, 1],
      [1, 1],
      [0, 3],
      [3, 3],
      [50, 100],
    ] as Array<[number, number]>) {
      const interval = wilsonInterval(good, total);
      expect(interval?.low).toBeGreaterThanOrEqual(0);
      expect(interval?.high).toBeLessThanOrEqual(1);
    }
  });

  it('brackets the point estimate', () => {
    const interval = wilsonInterval(7, 10);
    expect(interval?.low).toBeLessThanOrEqual(0.7);
    expect(interval?.high).toBeGreaterThanOrEqual(0.7);
  });
});

describe('buildScoreboard', () => {
  let db: Db;

  beforeEach(() => {
    db = openDb(':memory:');
  });

  function addRatedDraft(
    enquiryId: number,
    promptVersionId: number,
    rating: 'good' | 'bad' | null,
  ): number {
    const draft = insertDraft(db, {
      enquiryId,
      promptVersionId,
      provider: 'stub',
      model: 'claude-opus-5',
      generatedText: 'one two three four five',
      inputTokens: null,
      outputTokens: null,
      latencyMs: 5,
    });
    if (rating !== null) updateDraft(db, draft.id, { rating });
    return draft.id;
  }

  it('reports a seeded database with no drafts as entirely unrated', () => {
    const board = buildScoreboard(db);
    expect(board.versions).toHaveLength(1);
    expect(board.versions[0]?.drafts).toBe(0);
    expect(board.versions[0]?.rated).toBe(0);
    expect(board.versions[0]?.goodRate).toBeNull();
    expect(board.versions[0]?.wilsonLow).toBeNull();
    expect(board.versions[0]?.enoughData).toBe(false);
    expect(board.totals.minSample).toBe(MIN_SAMPLE);
  });

  it('attributes ratings to the prompt version that produced the draft, not the active one', () => {
    const enquiry = createEnquiry(db, 'Subject', 'Body');
    const v1 = db.prepare('SELECT id FROM prompt_versions WHERE version = 1').get() as {
      id: number;
    };

    addRatedDraft(enquiry.id, v1.id, 'good');
    addRatedDraft(enquiry.id, v1.id, 'good');

    // Change the prompt AFTER those ratings. v1's numbers must not move.
    const v2 = createPromptVersion(db, 'A different prompt entirely', 'v2');
    addRatedDraft(enquiry.id, v2.id, 'bad');

    const board = buildScoreboard(db);
    const stat1 = board.versions.find((version) => version.version === 1);
    const stat2 = board.versions.find((version) => version.version === 2);

    expect(stat1?.good).toBe(2);
    expect(stat1?.bad).toBe(0);
    expect(stat1?.goodRate).toBe(1);
    expect(stat2?.good).toBe(0);
    expect(stat2?.bad).toBe(1);
    expect(stat2?.goodRate).toBe(0);
  });

  it('flags a version as inconclusive until it reaches the minimum sample', () => {
    const enquiry = createEnquiry(db, 'Subject', 'Body');
    const v1 = db.prepare('SELECT id FROM prompt_versions WHERE version = 1').get() as {
      id: number;
    };

    for (let i = 0; i < MIN_SAMPLE - 1; i += 1) addRatedDraft(enquiry.id, v1.id, 'good');
    expect(buildScoreboard(db).versions[0]?.enoughData).toBe(false);

    addRatedDraft(enquiry.id, v1.id, 'good');
    const stat = buildScoreboard(db).versions[0];
    expect(stat?.rated).toBe(MIN_SAMPLE);
    expect(stat?.enoughData).toBe(true);
    // Even at the threshold the interval must stay honest about the remaining uncertainty.
    expect(stat?.wilsonLow).toBeLessThan(1);
  });

  it('ignores unrated drafts in the rate but still counts them as drafts', () => {
    const enquiry = createEnquiry(db, 'Subject', 'Body');
    const v1 = db.prepare('SELECT id FROM prompt_versions WHERE version = 1').get() as {
      id: number;
    };

    addRatedDraft(enquiry.id, v1.id, 'good');
    addRatedDraft(enquiry.id, v1.id, null);
    addRatedDraft(enquiry.id, v1.id, null);

    const stat = buildScoreboard(db).versions[0];
    expect(stat?.drafts).toBe(3);
    expect(stat?.rated).toBe(1);
    expect(stat?.goodRate).toBe(1);
  });

  it('computes a median keep ratio from edited drafts only', () => {
    const enquiry = createEnquiry(db, 'Subject', 'Body');
    const v1 = db.prepare('SELECT id FROM prompt_versions WHERE version = 1').get() as {
      id: number;
    };

    const a = addRatedDraft(enquiry.id, v1.id, 'good');
    const b = addRatedDraft(enquiry.id, v1.id, 'good');
    addRatedDraft(enquiry.id, v1.id, 'good'); // never edited, must not count

    // generated text is five words; change one, then change four
    updateDraft(db, a, { editedText: 'one two three four X', editDistance: 1, editBaseWords: 5 });
    updateDraft(db, b, { editedText: 'a b c d e', editDistance: 5, editBaseWords: 5 });

    const stat = buildScoreboard(db).versions[0];
    expect(stat?.editedCount).toBe(2);
    // ratios are 0.8 and 0.0, so the median of two values is their mean
    expect(stat?.medianKeepRatio).toBeCloseTo(0.4, 5);
  });

  it('totals across every version', () => {
    const enquiry = createEnquiry(db, 'Subject', 'Body');
    const v1 = db.prepare('SELECT id FROM prompt_versions WHERE version = 1').get() as {
      id: number;
    };
    addRatedDraft(enquiry.id, v1.id, 'good');
    const v2 = createPromptVersion(db, 'Second', 'two');
    addRatedDraft(enquiry.id, v2.id, null);

    const board = buildScoreboard(db);
    expect(board.totals).toMatchObject({
      enquiries: 1,
      drafts: 2,
      rated: 1,
      versions: 2,
    });
  });
});
