interface StatsCardProps {
  label: string;
  value: string | number;
  icon: JSX.Element;
  iconBg: string;
}

export function StatsCard({ label, value, icon, iconBg }: StatsCardProps) {
  return (
    <div className="bg-transparent rounded-xl p-5 flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-zinc-400">{label}</p>
        <p className="text-3xl font-bold text-white mt-1">{value}</p>
      </div>
      <div className={`h-12 w-12 rounded-xl ${iconBg} flex items-center justify-center`}>
        {icon}
      </div>
      <div>
        <p className="text-[22px] font-medium text-white leading-none mb-1">{value}</p>
        <p className="text-[11.5px] text-gray-500">{label}</p>
      </div>
    </div>
  );
}