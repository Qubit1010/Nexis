import { IntakeForm } from './intake-form';
import styles from './form.module.css';

export const metadata = {
  title: 'Start a project | LeadQ',
  description: 'Tell us what you need and we will come back to you.',
};

/**
 * The public intake. One editorial column, numbered questions, no card and no hero
 * gradient. It is the first impression the business makes, so it reads as a considered
 * questionnaire rather than a lead-capture modal.
 */
export default function IntakePage() {
  return (
    <main className={styles.page} id="main">
      <div className={styles.column}>
        <header className={styles.masthead}>
          <p className="eyebrow">New project enquiry</p>
          <h1 className={styles.title}>Tell us what you are trying to build.</h1>
          <p className={styles.standfirst}>
            Five questions, about two minutes. The more specific you are about the outcome
            you want, the more useful our first reply will be.
          </p>
        </header>

        <hr className="rule-line" />

        <IntakeForm />

        <footer className={styles.footer}>
          <p className="muted">
            We read every submission ourselves. Nothing here is shared with anyone else.
          </p>
        </footer>
      </div>
    </main>
  );
}
