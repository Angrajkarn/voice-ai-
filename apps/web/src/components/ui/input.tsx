'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  label?: string;
  helperText?: string;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, error, label, helperText, id, ...props }, ref) => {
    const generatedId = React.useId();
    const inputId = id || generatedId;
    const errorId = `${inputId}-error`;
    const helperId = `${inputId}-helper`;

    return (
      <div className="w-full">
        {label && <label htmlFor={inputId} className="mb-1.5 block text-sm font-medium text-base-content">{label}</label>}
        <input
          type={type}
          id={inputId}
          className={cn('input input-bordered h-11 w-full rounded-xl border-base-300 bg-base-100 text-base-content placeholder:text-base-content/40 focus:input-primary', error && 'input-error', className)}
          ref={ref}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={error ? errorId : helperText ? helperId : undefined}
          {...props}
        />
        {error && <p id={errorId} className="mt-1.5 text-sm text-error" role="alert">{error}</p>}
        {helperText && !error && <p id={helperId} className="mt-1.5 text-sm text-base-content/60">{helperText}</p>}
      </div>
    );
  },
);
Input.displayName = 'Input';

export { Input };
