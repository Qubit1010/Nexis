import { getBands, listRules } from '@/lib/rules';
import { RuleEditor } from './rule-editor';

export const metadata = { title: 'Scoring rules | LeadQ' };
export const dynamic = 'force-dynamic';

export default function RulesPage() {
  return <RuleEditor initialRules={listRules()} initialBands={getBands()} />;
}
