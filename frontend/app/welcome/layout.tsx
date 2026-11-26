import type { Metadata } from 'next';
import { copy } from '@/lib/copy';

export const metadata: Metadata = { title: copy.welcome.title };

export default function WelcomeLayout({ children }: { children: React.ReactNode }) {
  return children;
}
