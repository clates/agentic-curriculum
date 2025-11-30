import { HTMLAttributes, forwardRef } from 'react';

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'mastered' | 'developing' | 'not-started' | 'benched' | 'subject' | 'default' | 'warning' | 'success';
}

const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ variant = 'default', className = '', children, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium';
    
    const variants = {
      mastered: 'bg-sage-100 text-sage-700',
      developing: 'bg-secondary-100 text-secondary-700',
      'not-started': 'bg-neutral-100 text-neutral-600',
      benched: 'bg-cool-100 text-cool-700',
      subject: 'bg-primary-50 text-primary-700',
      default: 'bg-neutral-100 text-neutral-700',
      warning: 'bg-secondary-100 text-secondary-700 font-semibold',
      success: 'bg-sage-100 text-sage-700',
    };
    
    return (
      <span
        ref={ref}
        className={`${baseStyles} ${variants[variant]} ${className}`}
        {...props}
      >
        {children}
      </span>
    );
  }
);

Badge.displayName = 'Badge';

export { Badge };
export type { BadgeProps };
