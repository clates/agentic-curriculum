import type { Metadata } from 'next';
import { LoopConsole } from '@/components/loop/LoopConsole';

export const metadata: Metadata = { title: 'Loop console' };

export default function LoopPage() {
  return <LoopConsole />;
}
