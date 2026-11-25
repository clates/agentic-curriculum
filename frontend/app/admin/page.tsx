import type { Metadata } from 'next';
import Link from 'next/link';
import { AdminOnly } from '@/components/admin/AdminOnly';
import { Card } from '@/components/ui/Card';
import { copy } from '@/lib/copy';

export const metadata: Metadata = { title: copy.admin.title };

export default function AdminPage() {
  return (
    <AdminOnly>
      <main id="main" className="mx-auto max-w-3xl px-4 py-8">
        <h1 className="mb-6 text-3xl font-semibold text-neutral-900">{copy.admin.title}</h1>
        <Card>
          <h2 className="text-xl font-semibold text-neutral-900">{copy.admin.loopTitle}</h2>
          <p className="mt-2 text-neutral-700">{copy.admin.loopBody}</p>
          <Link
            href="/loop"
            className="text-primary-700 mt-4 inline-flex min-h-11 items-center underline"
          >
            {copy.admin.loopTitle}
          </Link>
        </Card>
      </main>
    </AdminOnly>
  );
}
