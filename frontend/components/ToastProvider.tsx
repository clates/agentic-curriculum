'use client';

import { createContext, useContext, useState, useCallback, ReactNode } from 'react';

type ToastType = 'success' | 'error' | 'info';

interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

interface ToastContextType {
  showToast: (message: string, type?: ToastType) => void;
}

const STYLE: Record<ToastType, { bg: string; icon: string }> = {
  success: { bg: 'bg-green-600', icon: 'M5 13l4 4L19 7' },
  error: { bg: 'bg-red-600', icon: 'M6 18L18 6M6 6l12 12' },
  info: { bg: 'bg-blue-600', icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
};

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((message: string, type: ToastType = 'success') => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 5000);
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div
        className="fixed right-4 bottom-4 z-50 space-y-2"
        role="region"
        aria-live="polite"
        aria-label="Notifications"
      >
        {toasts.map((toast) => (
          <div
            key={toast.id}
            role="alert"
            className={`min-w-80 transform rounded-lg px-4 py-3 text-white shadow-lg transition-all duration-300 ease-in-out ${STYLE[toast.type].bg}`}
          >
            <div className="flex items-start space-x-3">
              <svg
                className="mt-0.5 h-5 w-5 flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d={STYLE[toast.type].icon}
                />
              </svg>
              <p className="flex-1 text-sm font-medium">{toast.message}</p>
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
