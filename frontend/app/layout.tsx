import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';
import { ReactQueryProvider } from '@/lib/providers';
import { ToastProvider } from '@/components/ToastProvider';
import { VersionFooter } from '@/components/VersionFooter';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: {
    template: '%s — CurricuLearn',
    default: 'CurricuLearn — Parent Dashboard',
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
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <ReactQueryProvider>
          <ToastProvider>{children}</ToastProvider>
          <VersionFooter />
        </ReactQueryProvider>
      </body>
    </html>
  );
}
