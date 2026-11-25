import type { Metadata } from 'next';
import { Andika, Recursive } from 'next/font/google';
import './globals.css';
import { ReactQueryProvider } from '@/lib/providers';
import { ToastProvider } from '@/components/ToastProvider';
import { VersionFooter } from '@/components/VersionFooter';
import { copy } from '@/lib/copy';

// Recursive for everything the parent reads. Andika for anything the child reads: it was made for
// beginning readers (single-story a and g, plain i and l). next/font downloads both at build time
// and serves them from this site, so no page asks a font service for anything.
const recursive = Recursive({
  variable: '--font-recursive',
  subsets: ['latin'],
});

const andika = Andika({
  variable: '--font-andika',
  weight: ['400', '700'],
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: {
    template: `%s — ${copy.app.name}`,
    default: `${copy.app.name} — Parent Dashboard`,
  },
  description: 'Homeschool curriculum planning made simple',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${recursive.variable} ${andika.variable} antialiased`}>
        <ReactQueryProvider>
          <ToastProvider>{children}</ToastProvider>
          <VersionFooter />
        </ReactQueryProvider>
      </body>
    </html>
  );
}
