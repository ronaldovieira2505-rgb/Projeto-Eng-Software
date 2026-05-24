interface StatsCardProps {
  label: string;
  value: string | number;
  iconBg: string;
  icon: JSX.Element;
}

export function StatsCard({ label, value, iconBg, icon }: StatsCardProps) {
  return (
    <div className="bg-white rounded-xl p-5 shadow-sm flex items-center justify-between">
      <div>
        <p className="text-sm text-gray-500">{label}</p>
        <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
      </div>
      <div className={`h-12 w-12 rounded-xl ${iconBg} flex items-center justify-center`}>
        {icon}
      </div>
    </div>
  );
}
