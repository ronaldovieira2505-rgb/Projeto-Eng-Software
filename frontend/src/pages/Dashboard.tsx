import { StatsCard } from "../components/dashboard/StatsCard";
import { Badge } from "../components/ui/Badge";
import type { DashboardStats, Presentation } from "../types";

const STATS_CONFIG = (stats: DashboardStats) => [
  {
    label: "Apresentações Criadas",
    value: stats.presentationsCreated,
    iconBg: "bg-blue-100",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#2563EB" strokeWidth="2" className="h-6 w-6">
        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
        <polyline points="14 2 14 8 20 8" />
      </svg>
    ),
  },
  {
    label: "Commits Analisados",
    value: stats.commitsAnalyzed.toLocaleString("pt-BR"),
    iconBg: "bg-green-100",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#16A34A" strokeWidth="2" className="h-6 w-6">
        <circle cx="12" cy="12" r="4" />
        <line x1="2" y1="12" x2="8" y2="12" />
        <line x1="16" y1="12" x2="22" y2="12" />
      </svg>
    ),
  },
  {
    label: "Horas Economizadas",
    value: `${stats.hoursSaved}h`,
    iconBg: "bg-purple-100",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#7C3AED" strokeWidth="2" className="h-6 w-6">
        <circle cx="12" cy="12" r="10" />
        <polyline points="12 6 12 12 16 14" />
      </svg>
    ),
  },
  {
    label: "Taxa de Aprovação",
    value: `${stats.approvalRate}%`,
    iconBg: "bg-orange-100",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#EA580C" strokeWidth="2" className="h-6 w-6">
        <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
        <polyline points="17 6 23 6 23 12" />
      </svg>
    ),
  },
];

interface DashboardProps {
  presentations: Presentation[];
  stats: DashboardStats;
}

export function Dashboard({ presentations, stats }: DashboardProps) {
  return (
    <div className="flex flex-col gap-6">
      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {STATS_CONFIG(stats).map((card) => (
          <StatsCard key={card.label} {...card} />
        ))}
      </div>

      {/* Recent presentations */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Apresentações Recentes
        </h2>

        {presentations.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-8">
            Nenhuma apresentação criada ainda.
          </p>
        ) : (
          <div className="flex flex-col gap-3">
            {presentations.map((p) => (
              <div
                key={p.id}
                className="flex items-center justify-between p-4 rounded-lg border border-gray-100 hover:border-gray-200 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="h-9 w-9 rounded-lg bg-blue-50 flex items-center justify-center">
                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="#2563EB"
                      strokeWidth="2"
                      className="h-4 w-4"
                    >
                      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{p.title}</p>
                    <p className="text-xs text-gray-500">{p.audience}</p>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <span className="text-xs text-gray-400">{p.createdAt}</span>
                  <Badge status={p.status} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
