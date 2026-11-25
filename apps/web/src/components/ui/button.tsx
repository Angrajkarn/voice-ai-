'use client';

import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'btn inline-flex items-center justify-center whitespace-nowrap rounded-xl text-sm font-semibold normal-case shadow-none ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'btn-primary',
        destructive: 'btn-error',
        outline: 'btn-outline border-base-300 bg-transparent text-base-content hover:bg-primary hover:text-primary-content',
        secondary: 'btn-secondary',
        ghost: 'btn-ghost',
        link: 'btn-link',
        success: 'btn-success',
        warning: 'btn-warning',
      },
      size: {
        default: 'btn-md h-10 min-h-10 px-4',
        sm: 'btn-sm h-9 min-h-9 rounded-lg px-3',
        lg: 'btn-lg h-12 min-h-12 px-8',
        xl: 'btn-lg h-13 min-h-13 rounded-xl px-10 text-base',
        icon: 'btn-square btn-md h-10 min-h-10 w-10',
      },
    },
    defaultVariants: { variant: 'default', size: 'default' },
  },
);

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, loading = false, disabled, children, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button';
    return (
      <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} disabled={disabled || loading} aria-busy={loading} {...props}>
        {loading ? <><span className="loading loading-spinner loading-sm mr-2" aria-hidden="true" /><span>Loading...</span></> : children}
      </Comp>
    );
  },
);
Button.displayName = 'Button';

export { Button, buttonVariants };
