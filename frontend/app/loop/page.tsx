import type { Metadata } from 'next';
import { AdminOnly } from '@/components/admin/AdminOnly';
import { LoopConsole } from '@/components/loop/LoopConsole';

export const metadata: Metadata = { title: 'Loop console' };

export default function LoopPage() {
  return (
    <AdminOnly>
      <LoopConsole />
    </AdminOnly>
  );
}
