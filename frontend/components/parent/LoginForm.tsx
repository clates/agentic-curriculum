'use client';

import { useEffect, useRef, useState, type FormEvent } from 'react';
import { useSearchParams } from 'next/navigation';
import { isAxiosError } from 'axios';
import { apiClient } from '@/lib/api';
import { NEW_FAMILY_LANDING, safeNext } from '@/lib/auth';
import { copy } from '@/lib/copy';
import { primaryButton } from '@/components/parent/states';
import { CheckEmail, CreateAccount, WrongEmail } from '@/components/parent/SignUp';

type Problem =
  | { kind: 'wrong' }
  | { kind: 'wait'; seconds: number }
  | { kind: 'failed' }
  | { kind: 'busy' }
  | null;

const MESSAGES = {
  wrong: copy.login.wrong,
  busy: copy.login.busy,
  failed: copy.login.couldNotReach,
};

const field =
  'mt-1 block min-h-11 w-full rounded-md border border-neutral-400 bg-white px-3 py-2 text-base focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600';

/** The default landing page when a login is needed: username, password, and a calm way in. */
export function LoginForm() {
  const asked = useSearchParams().get('next');
  const next = safeNext(asked);
  // After confirming the email: the page they were sent from, else a new family's welcome page.
  const nextAfterVerify = safeNext(asked, NEW_FAMILY_LANDING);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [visible, setVisible] = useState(false);
  const [sending, setSending] = useState(false);
  const [waiting, setWaiting] = useState(false);
  const [step, setStep] = useState<'signin' | 'create' | 'code' | 'wrongEmail'>('signin');
  const [problem, setProblem] = useState<Problem>(null);
  const usernameRef = useRef<HTMLInputElement>(null);
  const passwordRef = useRef<HTMLInputElement>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    usernameRef.current?.focus();
    return () => {
      if (timer.current) clearTimeout(timer.current);
    };
  }, []);

  async function submit(event?: FormEvent) {
    event?.preventDefault();
    if (sending || waiting) return;
    setSending(true);
    setProblem(null);
    try {
      await apiClient.post('/auth/login', { username: username.trim(), password });
      // A full page load so the new cookie is on the very next request.
      window.location.assign(next);
      return;
    } catch (error) {
      const response = isAxiosError(error) ? error.response : undefined;
      const status = response?.status;
      if (status === 403 && response?.data?.detail === 'email_not_verified') {
        setStep('code'); // the password stays in this component: confirming the email needs it
      } else if (status === 401) {
        setProblem({ kind: 'wrong' });
        setPassword('');
        passwordRef.current?.focus();
      } else if (status === 429) {
        const header = Number(response?.headers?.['retry-after']);
        const seconds = Number.isFinite(header) && header > 0 ? Math.ceil(header) : 15;
        setProblem({ kind: 'wait', seconds });
        setPassword('');
        setWaiting(true);
        timer.current = setTimeout(() => {
          setWaiting(false);
          passwordRef.current?.focus();
        }, seconds * 1000);
      } else if (status === 503) {
        setProblem({ kind: 'busy' });
      } else {
        setProblem({ kind: 'failed' });
      }
    }
    setSending(false);
  }

  const message =
    problem?.kind === 'wait'
      ? copy.login.wait(problem.seconds)
      : problem
        ? MESSAGES[problem.kind]
        : null;

  if (step === 'create')
    return (
      <CreateAccount
        onRegistered={(email, typed) => {
          setUsername(email);
          setPassword(typed);
          setStep('code');
        }}
        onBack={() => setStep('signin')}
      />
    );
  if (step === 'code')
    return (
      <CheckEmail
        email={username.trim()}
        password={password}
        next={nextAfterVerify}
        onWrongEmail={() => {
          setPassword('');
          setStep('wrongEmail');
        }}
      />
    );
  if (step === 'wrongEmail') return <WrongEmail onBack={() => setStep('signin')} />;

  return (
    <div className="bg-background min-h-screen">
      <main id="main" className="mx-auto max-w-sm px-4 py-12">
        <p className="text-primary-700 text-xl font-semibold">{copy.app.name}</p>
        <h1 className="text-foreground mt-6 text-2xl font-semibold">{copy.login.title}</h1>
        <p className="mt-2 text-neutral-700">{copy.login.intro}</p>

        <form onSubmit={submit} className="mt-6 space-y-4" noValidate>
          <div>
            <label htmlFor="login-username" className="text-foreground block font-medium">
              {copy.login.username}
            </label>
            <input
              id="login-username"
              ref={usernameRef}
              name="username"
              type="text"
              autoComplete="username"
              autoCapitalize="none"
              autoCorrect="off"
              spellCheck={false}
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={field}
            />
          </div>
          <div>
            <label htmlFor="login-password" className="text-foreground block font-medium">
              {copy.login.password}
            </label>
            <div className="flex gap-2">
              <input
                id="login-password"
                ref={passwordRef}
                name="password"
                type={visible ? 'text' : 'password'}
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                aria-describedby={message ? 'login-message' : undefined}
                className={field}
              />
              <button
                type="button"
                onClick={() => setVisible((v) => !v)}
                aria-pressed={visible}
                aria-label={visible ? copy.login.hideLabel : copy.login.showLabel}
                className="mt-1 min-h-11 min-w-16 rounded-md border border-neutral-400 bg-white px-3 text-neutral-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
              >
                {visible ? copy.login.hide : copy.login.show}
              </button>
            </div>
          </div>

          <div id="login-message" role="alert" className="min-h-6 text-neutral-900">
            {message}
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              type="submit"
              disabled={sending || waiting || !username.trim() || !password}
              className={`${primaryButton} w-full disabled:cursor-not-allowed disabled:opacity-60`}
            >
              {sending ? copy.login.submitting : copy.login.submit}
            </button>
            {problem?.kind === 'failed' || problem?.kind === 'busy' ? (
              <button
                type="button"
                onClick={() => submit()}
                disabled={sending}
                className="min-h-11 w-full rounded-md border border-neutral-400 bg-white px-6 py-3 font-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
              >
                {copy.login.retry}
              </button>
            ) : null}
          </div>
        </form>
        <button
          type="button"
          onClick={() => setStep('create')}
          className="text-primary-700 mt-6 min-h-11 font-medium underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
        >
          {copy.login.createLink}
        </button>
      </main>
    </div>
  );
}
