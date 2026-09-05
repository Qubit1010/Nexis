import type { Band } from '@/types';
import styles from './score-meter.module.css';

interface Props {
  score: number;
  band: Band;
  compact?: boolean;
}

/**
 * The signature reading. Position (heat rule), quantity (number) and length (bar) all
 * encode the same score, so it survives a glance, a screen reader and a colour-blind eye.
 */
export function ScoreMeter({ score, band, compact = false }: Props) {
  const classes = [styles.wrap, styles[band], compact ? styles.compact : ''].join(' ');

  return (
    <div className={classes}>
      <span className={styles.heat} aria-hidden="true" />
      <div className={styles.body}>
        <span className={styles.value}>{score}</span>
        <span className={styles.track} aria-hidden="true">
          <span className={styles.fill} style={{ width: score + '%' }} />
        </span>
        <span className={styles.bandLabel}>{band}</span>
      </div>
      <span className="sr-only">
        Score {score} out of 100, {band}
      </span>
    </div>
  );
}
