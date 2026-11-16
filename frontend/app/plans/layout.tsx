import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Weekly Plans',
};

export default function PlansLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
