interface CheckboxProps {
  label: string;
  description?: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

export function Checkbox({ label, description, checked, onChange }: CheckboxProps) {
  return (
    <div className="flex items-start gap-3 p-4 rounded-lg border border-gray-200 bg-white">
      <div className="flex items-center pt-0.5">
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
        />
      </div>
      <div className="flex flex-col">
        <span className="text-sm font-medium text-gray-800">{label}</span>
        {description && (
          <span className="text-sm text-gray-500">{description}</span>
        )}
      </div>
    </div>
  );
}
