import { StatsCard } from "../components/dashboard/StatsCard";
import { Badge } from "../components/ui/Badge";
import type { DashboardStats, Presentation } from "../types";
import { Sparkles } from "lucide-react";

const STATS_CONFIG = (stats: DashboardStats) => [
  {
    label: "Apresentações Criadas",
    value: stats.presentationsCreated,
    iconBg: "bg-cyan-500/10 border border-cyan-500/20",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#22d3ee" strokeWidth="2" className="h-6 w-6">
        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
        <polyline points="14 2 14 8 20 8" />
      </svg>
    ),
  },
  {
    label: "Commits Analisados",
    value: stats.commitsAnalyzed.toLocaleString("pt-BR"),
    iconBg: "bg-emerald-500/10 border border-emerald-500/20",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="2" className="h-6 w-6">
        <circle cx="12" cy="12" r="4" />
        <line x1="2" y1="12" x2="8" y2="12" />
        <line x1="16" y1="12" x2="22" y2="12" />
      </svg>
    ),
  },
  {
    label: "Horas Economizadas",
    value: `${stats.hoursSaved}h`,
    iconBg: "bg-purple-500/10 border border-purple-500/20",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#a78bfa" strokeWidth="2" className="h-6 w-6">
        <circle cx="12" cy="12" r="10" />
        <polyline points="12 6 12 12 16 14" />
      </svg>
    ),
  },
  {
    label: "Taxa de Aprovação",
    value: `${stats.approvalRate}%`,
    iconBg: "bg-amber-500/10 border border-amber-500/20",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#fbbf24" strokeWidth="2" className="h-6 w-6">
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
    <div className="flex flex-col gap-8 animate-in fade-in slide-in-from-bottom-4 duration-500">

      {/* Cabeçalho do Dashboard */}
      <div>
        <h2 className="text-3xl font-light text-white tracking-tight flex items-center gap-3">
          Visão <span className="font-semibold text-cyan-400">Geral</span>
        </h2>
        <p className="text-zinc-400 mt-2 text-lg font-light">
          Acompanhe as métricas de geração e as suas apresentações recentes.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">
        {STATS_CONFIG(stats).map((card) => (
          <div key={card.label} className="bg-[#0A0A0A]/40 backdrop-blur-xl border border-white/[0.05] rounded-2xl shadow-xl overflow-hidden transition-all hover:-translate-y-1 hover:border-cyan-500/20">
            <StatsCard {...card} />
          </div>
        ))}
      </div>

      {/* Recent presentations */}
      <div className="bg-[#0A0A0A]/40 backdrop-blur-xl border border-white/[0.05] rounded-[2rem] p-8 shadow-2xl relative overflow-hidden">
        {/* Brilho sutil */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/5 rounded-full blur-3xl -z-10 transform translate-x-1/2 -translate-y-1/2"></div>

        <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
          Apresentações Recentes
        </h2>

        {presentations.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 border border-dashed border-white/10 rounded-2xl bg-white/[0.01]">
            <Sparkles className="h-8 w-8 text-cyan-500/40 mb-3" />
            <p className="text-sm text-zinc-500 text-center">
              Nenhuma apresentação criada ainda.
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {presentations.map((p) => (
              <div
                key={p.id}
                className="group flex items-center justify-between p-4 rounded-xl border border-white/5 bg-white/[0.01] hover:bg-white/[0.03] hover:border-cyan-500/30 transition-all"
              >
                <div className="flex items-center gap-4">
                  <div className="h-10 w-10 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="#22d3ee"
                      strokeWidth="2"
                      className="h-5 w-5"
                    >
                      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-zinc-200 group-hover:text-cyan-400 transition-colors">{p.title}</p>
                    <p className="text-xs text-zinc-500">{p.audience}</p>
                  </div>
                </div>

                <div className="flex items-center gap-5">
                  <span className="text-xs text-zinc-500 font-medium">{p.createdAt}</span>
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