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
          <label className="mb-2 block text-sm font-medium text-neutral-700">{label}</label>
        )}
        <input
          ref={ref}
          className={`text-foreground focus:border-primary-500 focus:ring-primary-100 w-full rounded-sm border-2 border-neutral-300 bg-white px-4 py-3 text-base focus:ring-3 focus:outline-none disabled:cursor-not-allowed disabled:bg-neutral-50 ${
            error ? 'border-danger-500 focus:border-danger-500 focus:ring-danger-100' : ''
          } ${className} `}
          {...props}
        />
        {helperText && !error && <p className="mt-1 text-sm text-neutral-500">{helperText}</p>}
        {error && <p className="text-danger-600 mt-1 text-sm">{error}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };
export type { InputProps };
