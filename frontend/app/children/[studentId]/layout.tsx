import type { Metadata } from 'next';
import { ParentShell } from '@/components/parent/ParentShell';
import { copy } from '@/lib/copy';

export const metadata: Metadata = { title: copy.childPage.tabTitle };

export default function ChildLayout({ children }: { children: React.ReactNode }) {
  return <ParentShell>{children}</ParentShell>;
}
