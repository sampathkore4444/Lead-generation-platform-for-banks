// Input Component - Reusable
import React from 'react';
import clsx from 'clsx';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      label,
      error,
      hint,
      leftIcon,
      rightIcon,
      id,
      type = 'text',
      ...props
    },
    ref
  ) => {
    const inputId = id || props.name;

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            {label}
            {props.required && <span className="text-error ml-1">*</span>}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
              {leftIcon}
            </div>
          )}
          <input
            ref={ref}
            type={type}
            id={inputId}
            className={clsx(
              'block w-full px-4 py-2.5 text-base rounded-lg border transition-colors duration-200',
              'placeholder:text-gray-400',
              'focus:outline-none focus:ring-2 focus:ring-offset-0',
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              error
                ? 'border-error focus:border-error focus:ring-error/20'
                : 'border-gray-300 focus:border-primary-500 focus:ring-primary-500/20',
              className
            )}
            {...props}
          />
          {rightIcon && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-gray-400">
              {rightIcon}
            </div>
          )}
        </div>
        {error && <p className="mt-1 text-sm text-error">{error}</p>}
        {hint && !error && <p className="mt-1 text-sm text-gray-500">{hint}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';

// Select Component
interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: Array<{ value: string; label: string }>;
  placeholder?: string;
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, label, error, options, placeholder, id, ...props }, ref) => {
    const selectId = id || props.name;

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={selectId}
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            {label}
            {props.required && <span className="text-error ml-1">*</span>}
          </label>
        )}
        <select
          ref={ref}
          id={selectId}
          className={clsx(
            'block w-full px-4 py-2.5 text-base rounded-lg border transition-colors duration-200',
            'focus:outline-none focus:ring-2 focus:ring-offset-0',
            error
              ? 'border-error focus:border-error focus:ring-error/20'
              : 'border-gray-300 focus:border-primary-500 focus:ring-primary-500/20',
            className
          )}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {error && <p className="mt-1 text-sm text-error">{error}</p>}
      </div>
    );
  }
);

Select.displayName = 'Select';

// Checkbox Component
interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label: string;
  error?: string;
}

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, label, error, id, ...props }, ref) => {
    const checkboxId = id || props.name;

    return (
      <div className="w-full">
        <div className="flex items-start">
          <div className="flex items-center h-5">
            <input
              ref={ref}
              type="checkbox"
              id={checkboxId}
              className={clsx(
                'h-4 w-4 rounded border-gray-300 text-primary-500',
                'focus:ring-2 focus:ring-primary-500/20',
                error ? 'border-error' : '',
                className
              )}
              {...props}
            />
          </div>
          <div className="ml-3 text-sm">
            <label htmlFor={checkboxId} className="font-medium text-gray-700">
              {label}
            </label>
          </div>
        </div>
        {error && <p className="mt-1 text-sm text-error ml-7">{error}</p>}
      </div>
    );
  }
);

Checkbox.displayName = 'Checkbox';

export default Input;