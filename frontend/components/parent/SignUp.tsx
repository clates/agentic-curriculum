'use client';

import { useState, type FormEvent, type ReactNode } from 'react';
import { isAxiosError } from 'axios';
import { apiClient } from '@/lib/api';
import { copy } from '@/lib/copy';
import { primaryButton } from '@/components/parent/states';

const field =
  'mt-1 block min-h-11 w-full rounded-md border border-neutral-400 bg-white px-3 py-2 text-base focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600';
const linkButton =
  'text-primary-700 min-h-11 font-medium underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600';

/** What to tell the person for a refused call. A 400 may carry a plain sentence from the server. */
function problemFor(error: unknown, whenBad: (detail: unknown) => string): string {
  const response = isAxiosError(error) ? error.response : undefined;
  if (response?.status === 400) return whenBad(response.data?.detail);
  if (response?.status === 429) {
    const header = Number(response.headers?.['retry-after']);
    return copy.login.wait(Number.isFinite(header) && header > 0 ? Math.ceil(header) : 15);
  }
  return copy.login.couldNotReach;
}

function Page({ title, intro, children }: { title: string; intro: string; children: ReactNode }) {
  return (
    <div className="bg-background min-h-screen">
      <main id="main" className="mx-auto max-w-sm px-4 py-12">
        <p className="text-primary-700 text-xl font-semibold">{copy.app.name}</p>
        <h1 className="text-foreground mt-6 text-2xl font-semibold">{title}</h1>
        <p className="mt-2 text-neutral-700">{intro}</p>
        {children}
      </main>
    </div>
  );
}

function Field(props: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  autoComplete?: string;
  hint?: string;
  inputMode?: 'numeric';
  maxLength?: number;
}) {
  const id = `signup-${props.label.replace(/\W+/g, '-').toLowerCase()}`;
  return (
    <div>
      <label htmlFor={id} className="text-foreground block font-medium">
        {props.label}
      </label>
      {props.hint ? <p className="text-sm text-neutral-700">{props.hint}</p> : null}
      <input
        id={id}
        type={props.type ?? 'text'}
        autoComplete={props.autoComplete}
        inputMode={props.inputMode}
        maxLength={props.maxLength}
        autoCapitalize="none"
        autoCorrect="off"
        spellCheck={false}
        required
        value={props.value}
        onChange={(e) => props.onChange(e.target.value)}
        className={field}
      />
    </div>
  );
}

/** Family name, email, the password twice and an invite code. Hands the password up for the code step. */
export function CreateAccount({
  onRegistered,
  onBack,
}: {
  onRegistered: (email: string, password: string) => void;
  onBack: () => void;
}) {
  const [values, setValues] = useState({
    family: '',
    email: '',
    password: '',
    again: '',
    invite: '',
  });
  const [sending, setSending] = useState(false);
  const [problem, setProblem] = useState('');
  const set = (key: keyof typeof values) => (value: string) =>
    setValues((v) => ({ ...v, [key]: value }));

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (sending) return;
    if (values.password !== values.again) return setProblem(copy.signUp.mismatch);
    setSending(true);
    setProblem('');
    const email = values.email.trim();
    try {
      await apiClient.post('/auth/register', {
        email,
        password: values.password,
        family_name: values.family.trim(),
        invite_code: values.invite.trim().toUpperCase(),
      });
      onRegistered(email, values.password);
    } catch (error) {
      setProblem(
        problemFor(error, (detail) =>
          detail === 'invalid_invite'
            ? copy.signUp.badInvite
            : typeof detail === 'string'
              ? detail
              : copy.login.couldNotReach
        )
      );
      setSending(false);
    }
  }

  return (
    <Page title={copy.signUp.title} intro={copy.signUp.intro}>
      <form onSubmit={submit} className="mt-6 space-y-4" noValidate>
        <Field label={copy.signUp.familyName} value={values.family} onChange={set('family')} />
        <Field
          label={copy.signUp.email}
          type="email"
          autoComplete="email"
          value={values.email}
          onChange={set('email')}
        />
        <Field
          label={copy.signUp.password}
          type="password"
          autoComplete="new-password"
          hint={copy.signUp.passwordHint}
          value={values.password}
          onChange={set('password')}
        />
        <Field
          label={copy.signUp.passwordAgain}
          type="password"
          autoComplete="new-password"
          value={values.again}
          onChange={set('again')}
        />
        <Field label={copy.signUp.inviteCode} value={values.invite} onChange={set('invite')} />
        <div role="alert" className="min-h-6 text-neutral-900">
          {problem}
        </div>
        <button
          type="submit"
          disabled={sending || Object.values(values).some((v) => !v.trim())}
          className={`${primaryButton} w-full disabled:cursor-not-allowed disabled:opacity-60`}
        >
          {sending ? copy.signUp.submitting : copy.signUp.submit}
        </button>
      </form>
      <button type="button" onClick={onBack} className={`${linkButton} mt-6`}>
        {copy.signUp.haveAccount}
      </button>
    </Page>
  );
}

/** The 6-digit code from the email. The password is only held in memory, to confirm the email. */
export function CheckEmail({
  email,
  password,
  next,
}: {
  email: string;
  password: string;
  next: string;
}) {
  const [code, setCode] = useState('');
  const [sending, setSending] = useState(false);
  const [problem, setProblem] = useState('');
  const [resent, setResent] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (sending) return;
    setSending(true);
    setProblem('');
    setResent(false);
    try {
      await apiClient.post('/auth/verify', { email, code: code.trim(), password });
      window.location.assign(next); // a full load, so the new cookie is on the next request
    } catch (error) {
      setProblem(problemFor(error, () => copy.signUp.badCode));
      setSending(false);
    }
  }

  async function resend() {
    setProblem('');
    try {
      await apiClient.post('/auth/resend', { email });
      setResent(true);
    } catch (error) {
      setProblem(problemFor(error, () => copy.login.couldNotReach));
    }
  }

  return (
    <Page title={copy.signUp.checkTitle} intro={copy.signUp.checkIntro(email)}>
      <form onSubmit={submit} className="mt-6 space-y-4" noValidate>
        <Field
          label={copy.signUp.code}
          autoComplete="one-time-code"
          inputMode="numeric"
          maxLength={6}
          value={code}
          onChange={setCode}
        />
        <div role="alert" className="min-h-6 text-neutral-900">
          {problem}
        </div>
        <div role="status" className="min-h-6 text-neutral-900">
          {resent ? copy.signUp.resent : ''}
        </div>
        <button
          type="submit"
          disabled={sending || code.trim().length !== 6}
          className={`${primaryButton} w-full disabled:cursor-not-allowed disabled:opacity-60`}
        >
          {sending ? copy.signUp.confirming : copy.signUp.confirm}
        </button>
      </form>
      <button type="button" onClick={resend} className={`${linkButton} mt-6`}>
        {copy.signUp.resend}
      </button>
    </Page>
  );
}
