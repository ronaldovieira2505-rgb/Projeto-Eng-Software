import type { InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  helper?: string;
  icon?: React.ReactNode;
}

export function Input({ label, helper, icon, className = "", ...rest }: InputProps) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label className="text-sm font-medium text-zinc-300 ml-1">{label}</label>
      )}
      <div className="relative">
        {icon && (
          <span className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500">
            {icon}
          </span>
        )}
        <input
          className={`w-full rounded-xl border border-white/10 bg-white/[0.02] py-3 text-sm text-zinc-200
            placeholder:text-zinc-600 focus:border-cyan-500/50 focus:outline-none focus:ring-1 focus:ring-cyan-500/50 transition-all shadow-inner
            ${icon ? "pl-11 pr-4" : "px-4"}
            ${className}`}
          {...rest}
        />
      </div>
      {helper && <p className="text-xs text-zinc-500 ml-1">{helper}</p>}
    </div>
  );
}