import { countsByStatus, listLeads } from '@/lib/leads';
import { getBands } from '@/lib/rules';
import { Triage } from './triage';

export const metadata = { title: 'Leads | LeadQ' };
export const dynamic = 'force-dynamic';

/**
 * Server component: the first paint already has the data, so there is no client fetch
 * waterfall and no loading skeleton on the path the operator uses every day.
 */
export default function DashboardPage() {
  return (
    <Triage
      initialLeads={listLeads({ sort: 'score', order: 'desc' })}
      initialCounts={countsByStatus()}
      bands={getBands()}
    />
  );
}
