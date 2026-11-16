import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Progress Map',
};

export default function ProgressLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
