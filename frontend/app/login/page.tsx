import { Suspense } from 'react';
import { LoginForm } from '@/components/parent/LoginForm';

export default function LoginPage() {
  return (
    <Suspense>
      <LoginForm />
    </Suspense>
  );
}
