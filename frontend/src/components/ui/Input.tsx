import type { InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  helper?: string;
  icon?: React.ReactNode;
}

export function Input({ label, helper, icon, className = "", ...rest }: InputProps) {
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label className="text-sm font-medium text-gray-700">{label}</label>
      )}
      <div className="relative">
        {icon && (
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
            {icon}
          </span>
        )}
        <input
          className={`w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900
            placeholder:text-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500
            ${icon ? "pl-10" : ""}
            ${className}`}
          {...rest}
        />
      </div>
      {helper && <p className="text-xs text-gray-500">{helper}</p>}
    </div>
  );
}
