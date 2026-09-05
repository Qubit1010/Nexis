import type { Scoreboard as ScoreboardData, VersionStat } from '../types.ts';

type Props = { data: ScoreboardData | null; loading: boolean };

function pct(value: number | null): string {
  return value === null ? '-' : `${Math.round(value * 100)}%`;
}

/**
 * The signature element. A shared 0-100% axis with the good-rate as a bar, the 95% Wilson
 * interval as a whisker, and the point estimate as a tick.
 *
 * The whole reason the whisker exists: one good rating out of one produces a bar at 100% and
 * a whisker spanning roughly 21% to 100%. Without the whisker that version looks like a
 * breakthrough. With it, it visibly looks like what it is, which is not yet evidence.
 */
function Gauge({ stat }: { stat: VersionStat }) {
  if (stat.rated === 0) {
    return (
      <div className="gauge thin">
        <span className="axis-note">no ratings yet</span>
      </div>
    );
  }

  const rate = stat.goodRate ?? 0;
  const low = stat.wilsonLow ?? 0;
  const high = stat.wilsonHigh ?? 0;

  return (
    <div
      className={`gauge${stat.enoughData ? '' : ' thin'}`}
      role="img"
      aria-label={`Good rate ${pct(stat.goodRate)}, 95% confidence interval ${pct(low)} to ${pct(high)}, based on ${stat.rated} ratings`}
    >
      <div className="bar" style={{ transform: `scaleX(${rate})` }} />
      <div
        className="whisker"
        style={{ left: `${low * 100}%`, width: `${Math.max(0, (high - low) * 100)}%` }}
      />
      <div className="point" style={{ left: `calc(${rate * 100}% - 1.5px)` }} />
    </div>
  );
}

export function Scoreboard({ data, loading }: Props) {
  if (loading) {
    return (
      <section className="scoreboard" aria-busy="true">
        <div className="skeleton" />
        <div className="skeleton" />
        <div className="skeleton short" />
      </section>
    );
  }

  if (!data) return null;

  const anyRatings = data.totals.rated > 0;

  return (
    <section className="scoreboard">
      <h2>Is the prompt getting better?</h2>
      <p className="lede">
        One row per prompt version, newest first. The bar is the share of drafts you marked good.
        The whisker is the 95% confidence interval on that share, so you can see how much of the
        bar is real and how much is small-sample luck. A version needs {data.totals.minSample}{' '}
        ratings before it is treated as evidence rather than a hint.
      </p>

      {!anyRatings ? (
        <div className="empty">
          <h3>Nothing rated yet</h3>
          <p>
            This table fills in as you rate drafts. Rate a few under the current prompt, change
            the prompt on the Prompt tab, rate a few more, and the two versions will line up here
            for comparison.
          </p>
          <p>
            {data.totals.drafts} draft{data.totals.drafts === 1 ? '' : 's'} generated so far across{' '}
            {data.totals.versions} prompt version{data.totals.versions === 1 ? '' : 's'}.
          </p>
        </div>
      ) : (
        <div className="table-scroll">
          <table className="ledger">
            <thead>
              <tr>
                <th>Version</th>
                <th style={{ minWidth: 240 }}>Good rate, with 95% interval</th>
                <th className="num">Good</th>
                <th className="num">Bad</th>
                <th className="num">Rated</th>
                <th className="num">Drafts</th>
                <th className="num">Kept</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {data.versions.map((stat) => (
                <tr key={stat.promptVersionId} className={stat.isActive ? 'active' : undefined}>
                  <td className="version-cell">
                    <div className="v">v{stat.version}</div>
                    <div className="label">{stat.label}</div>
                  </td>
                  <td>
                    <Gauge stat={stat} />
                  </td>
                  <td className="num">{stat.good}</td>
                  <td className="num">{stat.bad}</td>
                  <td className="num">{stat.rated}</td>
                  <td className="num">{stat.drafts}</td>
                  <td className="num" title="Median share of words kept from the model's draft">
                    {stat.medianKeepRatio === null ? '-' : pct(stat.medianKeepRatio)}
                  </td>
                  <td>
                    {stat.rated === 0 ? (
                      <span className="flag">unrated</span>
                    ) : stat.enoughData ? (
                      <span style={{ fontFamily: 'var(--font-num)', fontSize: 12 }}>
                        {pct(stat.wilsonLow)}-{pct(stat.wilsonHigh)}
                      </span>
                    ) : (
                      <span className="flag">
                        not enough data ({stat.rated}/{data.totals.minSample})
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="reading-note">
        <strong>How to read this honestly.</strong> These numbers are observational, not an
        experiment. Different versions were rated on different enquiries, so a difference in good
        rate can come from an easier batch of enquiries rather than a better prompt. Two things
        make a comparison trustworthy: enough ratings that the whiskers stop overlapping, and
        re-drafting the same enquiry under both versions so the input is held constant. The{' '}
        <strong>Kept</strong> column is a second, quieter signal: the median share of the model's
        words that survived your editing. A prompt whose drafts you barely touch is working,
        whether or not you remembered to click anything.
      </div>
    </section>
  );
}
