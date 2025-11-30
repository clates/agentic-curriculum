import { InputHTMLAttributes, forwardRef } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, className = '', ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-neutral-700 mb-2">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={`
            w-full px-4 py-3 
            bg-white border-2 border-neutral-300 
            rounded-sm text-base text-foreground
            focus:outline-none focus:border-primary-500 focus:ring-3 focus:ring-primary-100
            disabled:bg-neutral-50 disabled:cursor-not-allowed
            ${error ? 'border-danger-500 focus:border-danger-500 focus:ring-danger-100' : ''}
            ${className}
          `}
          {...props}
        />
        {helperText && !error && (
          <p className="mt-1 text-sm text-neutral-500">{helperText}</p>
        )}
        {error && (
          <p className="mt-1 text-sm text-danger-600">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };
export type { InputProps };
