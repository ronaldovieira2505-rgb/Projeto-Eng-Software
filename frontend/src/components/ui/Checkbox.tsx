interface CheckboxProps {
  label: string;
  description?: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

export function Checkbox({ label, description, checked, onChange }: CheckboxProps) {
  return (
    <div className="flex items-start gap-3 p-4 rounded-xl border border-white/10 bg-white/[0.02] hover:bg-white/[0.04] transition-colors cursor-pointer" onClick={() => onChange(!checked)}>
      <div className="flex items-center pt-0.5">
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          // O onClick na div pai já faz o trabalho, então paramos a propagação aqui
          onClick={(e) => e.stopPropagation()}
          className="h-4 w-4 rounded border-white/20 bg-zinc-900 text-cyan-500 focus:ring-cyan-500/50 cursor-pointer accent-cyan-500"
        />
      </div>
      <div className="flex flex-col">
        <span className="text-sm font-medium text-zinc-200">{label}</span>
        {description && (
          <span className="text-xs text-zinc-500 mt-0.5 leading-relaxed">{description}</span>
        )}
      </div>
    </div>
  );
}