'use client';

import { useEffect, type ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { useMe } from '@/lib/useMe';

/** Shows its children to admins only; anyone else is sent home. (The API refuses them too.) */
export function AdminOnly({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { data: me } = useMe();
  const allowed = me ? !me.auth_required || me.permissions.includes('admin') : false;

  useEffect(() => {
    if (me && !allowed) router.replace('/');
  }, [me, allowed, router]);

  return allowed ? <>{children}</> : null;
}
