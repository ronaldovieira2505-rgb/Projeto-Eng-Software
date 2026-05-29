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

const FEATURE_CARDS = [
  {
    title: "Gerar Apresentação",
    description: "Crie slides a partir de texto livre, commits do GitHub ou releases do repositório.",
    iconBg: "bg-orange-950/60 border border-orange-900/40",
    iconColor: "#f97316",
    page: "create" as const,
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#f97316" strokeWidth="1.75" className="h-6 w-6">
        <rect x="3" y="3" width="18" height="14" rx="2" />
        <path d="M8 21h8M12 17v4" />
        <path d="M9 9l2 2 4-4" />
      </svg>
    ),
  },
  {
    title: "Importar do GitHub",
    description: "Extrai commits, pull requests e releases para gerar slides de Sprint Review.",
    iconBg: "bg-blue-950/60 border border-blue-900/40",
    iconColor: "#60a5fa",
    page: "create" as const,
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="1.75" className="h-6 w-6">
        <circle cx="12" cy="12" r="4" />
        <line x1="2" y1="12" x2="8" y2="12" />
        <line x1="16" y1="12" x2="22" y2="12" />
        <line x1="12" y1="2" x2="12" y2="8" />
        <line x1="12" y1="16" x2="12" y2="22" />
      </svg>
    ),
  },
  {
    title: "Exportar .pptx",
    description: "Converte slides gerados pela IA em arquivos PowerPoint prontos para download.",
    iconBg: "bg-purple-950/60 border border-purple-900/40",
    iconColor: "#a855f7",
    page: "create" as const,
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#a855f7" strokeWidth="1.75" className="h-6 w-6">
        <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
        <polyline points="7 10 12 15 17 10" />
        <line x1="12" y1="15" x2="12" y2="3" />
      </svg>
    ),
  },
  {
    title: "Resumir Conteúdo",
    description: "Transforma textos longos em bullets objetivos prontos para slides.",
    iconBg: "bg-teal-950/60 border border-teal-900/40",
    iconColor: "#2dd4bf",
    page: "create" as const,
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#2dd4bf" strokeWidth="1.75" className="h-6 w-6">
        <line x1="8" y1="6" x2="21" y2="6" />
        <line x1="8" y1="12" x2="21" y2="12" />
        <line x1="8" y1="18" x2="21" y2="18" />
        <line x1="3" y1="6" x2="3.01" y2="6" />
        <line x1="3" y1="12" x2="3.01" y2="12" />
        <line x1="3" y1="18" x2="3.01" y2="18" />
      </svg>
    ),
  },
  {
    title: "Melhorar Slides",
    description: "Refina apresentações existentes adaptando tom e linguagem para diferentes audiências.",
    iconBg: "bg-green-950/60 border border-green-900/40",
    iconColor: "#4ade80",
    page: "create" as const,
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#4ade80" strokeWidth="1.75" className="h-6 w-6">
        <path d="M12 20h9" />
        <path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z" />
      </svg>
    ),
  },
  {
    title: "Templates",
    description: "Gerencie e aplique templates de marca personalizados nas apresentações.",
    iconBg: "bg-red-950/60 border border-red-900/40",
    iconColor: "#f87171",
    page: "settings" as const,
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#f87171" strokeWidth="1.75" className="h-6 w-6">
        <rect x="3" y="3" width="18" height="18" rx="2" />
        <path d="M3 9h18M9 21V9" />
      </svg>
    ),
  },
];

interface DashboardProps {
  presentations: Presentation[];
  stats: DashboardStats;
  onNavigate?: (page: "dashboard" | "create" | "settings") => void;
}

export function Dashboard({ presentations, stats, onNavigate }: DashboardProps) {
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
        </div>
      )}
    </div>
  );
}