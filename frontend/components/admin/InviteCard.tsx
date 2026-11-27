'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { copy } from '@/lib/copy';

interface Invite {
  code: string;
  expires_at: string;
}

/** Makes an invite code and shows it once: the server keeps only a hash. */
export function InviteCard() {
  const [copied, setCopied] = useState(false);
  const make = useMutation({
    mutationFn: async () => (await apiClient.post<Invite>('/admin-api/invites')).data,
    onMutate: () => setCopied(false),
  });
  const invite = make.data;

  return (
    <Card className="mt-6">
      <h2 className="text-xl font-semibold text-neutral-900">{copy.admin.inviteTitle}</h2>
      <p className="mt-2 text-neutral-700">{copy.admin.inviteBody}</p>
      <Button className="mt-4 min-h-11" onClick={() => make.mutate()} disabled={make.isPending}>
        {copy.admin.inviteMake}
      </Button>
      {make.isError && (
        <p role="alert" className="mt-3 text-neutral-700">
          {copy.admin.inviteFailed}
        </p>
      )}
      {invite && (
        <div className="mt-4" data-testid="invite-result">
          <p className="text-2xl font-semibold tracking-widest text-neutral-900">{invite.code}</p>
          <p className="mt-1 text-sm text-neutral-700">{copy.admin.inviteShownOnce}</p>
          <p className="text-sm text-neutral-700">
            {copy.admin.inviteExpires(new Date(invite.expires_at).toLocaleDateString())}
          </p>
          <Button
            variant="secondary"
            className="mt-3 min-h-11"
            onClick={() =>
              navigator.clipboard
                .writeText(invite.code)
                .then(() => setCopied(true))
                .catch(() => setCopied(false))
            }
          >
            {copied ? copy.admin.inviteCopied : copy.admin.inviteCopy}
          </Button>
        </div>
      )}
    </Card>
  );
}
