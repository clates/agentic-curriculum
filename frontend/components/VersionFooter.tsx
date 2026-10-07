'use client';

import { useEffect, useState } from 'react';

const REPO_URL = 'https://github.com/clates/agentic-curriculum';

interface VersionInfo {
  sha: string;
  short_sha: string;
}

export function VersionFooter() {
  const [version, setVersion] = useState<VersionInfo | null>(null);

  useEffect(() => {
    fetch('/api/version')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => setVersion(data))
      .catch(() => setVersion(null));
  }, []);

  if (!version?.short_sha) return null;

  return (
    <footer className="py-2 text-center text-xs text-gray-400">
      {version.sha && version.sha !== 'unknown' ? (
        <a href={`${REPO_URL}/commit/${version.sha}`} target="_blank" rel="noreferrer">
          {version.short_sha}
        </a>
      ) : (
        <span>{version.short_sha}</span>
      )}
    </footer>
  );
}
