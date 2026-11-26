'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api';
import { copy } from '@/lib/copy';

/** Ends the session, then a full load of the login page. Used by the parent shell and /welcome. */
export function SignOutButton({ className }: { className: string }) {
  const [leaving, setLeaving] = useState(false);

  async function signOut() {
    setLeaving(true);
    try {
      await apiClient.post('/auth/logout');
    } finally {
      window.location.assign('/login');
    }
  }

  return (
    <button type="button" onClick={signOut} disabled={leaving} className={className}>
      {leaving ? copy.login.signingOut : copy.login.signOut}
    </button>
  );
}
