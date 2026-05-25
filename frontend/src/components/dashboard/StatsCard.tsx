interface StatsCardProps {
  label: string;
  value: string | number;
  icon: JSX.Element;
  iconBg: string;
}

export function StatsCard({ label, value, icon, iconBg }: StatsCardProps) {
  return (
    <div className="bg-[#13151d] border border-[#1f2235] rounded-xl p-4 flex flex-col gap-3">
      <div className={`inline-flex items-center justify-center h-9 w-9 rounded-lg ${iconBg}`}>
        {icon}
      </div>
      <div>
        <p className="text-[22px] font-medium text-white leading-none mb-1">{value}</p>
        <p className="text-[11.5px] text-gray-500">{label}</p>
      </div>
    </div>
  );
}
