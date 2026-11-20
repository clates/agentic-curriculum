import type { Metadata } from 'next';
import { ParentShell } from '@/components/parent/ParentShell';
import { copy } from '@/lib/copy';

export const metadata: Metadata = { title: copy.progress.title };

export default function ProgressLayout({ children }: { children: React.ReactNode }) {
  return <ParentShell>{children}</ParentShell>;
}
