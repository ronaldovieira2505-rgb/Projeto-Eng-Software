import { StatsCard } from "../components/dashboard/StatsCard";
import { Badge } from "../components/ui/Badge";
import type { DashboardStats, Presentation } from "../types";

const STATS_CONFIG = (stats: DashboardStats) => [
  {
    label: "Apresentações Criadas",
    value: stats.presentationsCreated,
    iconBg: "bg-blue-900/40",
    iconColor: "#60a5fa",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="1.75" className="h-5 w-5">
        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
        <polyline points="14 2 14 8 20 8" />
      </svg>
    ),
  },
  {
    label: "Commits Analisados",
    value: stats.commitsAnalyzed.toLocaleString("pt-BR"),
    iconBg: "bg-green-900/40",
    iconColor: "#4ade80",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#4ade80" strokeWidth="1.75" className="h-5 w-5">
        <circle cx="12" cy="12" r="4" />
        <line x1="2" y1="12" x2="8" y2="12" />
        <line x1="16" y1="12" x2="22" y2="12" />
      </svg>
    ),
  },
  {
    label: "Horas Economizadas",
    value: `${stats.hoursSaved}h`,
    iconBg: "bg-purple-900/40",
    iconColor: "#c084fc",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#c084fc" strokeWidth="1.75" className="h-5 w-5">
        <circle cx="12" cy="12" r="10" />
        <polyline points="12 6 12 12 16 14" />
      </svg>
    ),
  },
  {
    label: "Taxa de Aprovação",
    value: `${stats.approvalRate}%`,
    iconBg: "bg-orange-900/40",
    iconColor: "#fb923c",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#fb923c" strokeWidth="1.75" className="h-5 w-5">
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
    <div className="flex flex-col gap-8">

      {/* Page header */}
      <div>
        <h1 className="text-2xl font-medium text-white mb-1.5">
          Módulo de{" "}
          <span className="text-blue-400">Apresentações</span>{" "}
          <span className="inline-flex items-center justify-center w-7 h-7 rounded-md bg-[#1a2640] text-sm ml-1 align-middle">🎯</span>
        </h1>
        <p className="text-sm text-gray-500 max-w-xl leading-relaxed">
          Geração automatizada de slides para Sprint Reviews, Onboarding e clientes a partir de modelos.
          Navegue pelas funcionalidades disponíveis.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {STATS_CONFIG(stats).map((card) => (
          <StatsCard key={card.label} {...card} />
        ))}
      </div>

      {/* Feature cards */}
      <div>
        <p className="text-[11px] font-medium tracking-widest text-gray-600 uppercase mb-3">
          Funcionalidades
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {FEATURE_CARDS.map((card) => (
            <button
              key={card.title}
              onClick={() => onNavigate?.(card.page)}
              className="group relative text-left bg-[#13151d] border border-[#1f2235] rounded-xl p-5
                         hover:border-[#2e3355] hover:bg-[#161824] transition-all duration-200"
            >
              {/* External link icon */}
              <svg
                viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"
                className="h-3.5 w-3.5 absolute top-4 right-4 text-gray-700 group-hover:text-gray-500 transition-colors"
              >
                <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6" />
                <polyline points="15 3 21 3 21 9" />
                <line x1="10" y1="14" x2="21" y2="3" />
              </svg>

              {/* Icon */}
              <div className={`inline-flex items-center justify-center h-11 w-11 rounded-xl mb-4 ${card.iconBg}`}>
                {card.icon}
              </div>

              <h3 className="text-[13.5px] font-medium text-gray-200 mb-1.5">
                {card.title}
              </h3>
              <p className="text-[12px] text-gray-500 leading-relaxed">
                {card.description}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Recent presentations */}
      {presentations.length > 0 && (
        <div>
          <p className="text-[11px] font-medium tracking-widest text-gray-600 uppercase mb-3">
            Apresentações Recentes
          </p>
          <div className="bg-[#13151d] rounded-xl border border-[#1f2235] overflow-hidden">
            {presentations.map((p, idx) => (
              <div
                key={p.id}
                className={`flex items-center justify-between px-5 py-4 hover:bg-[#161824] transition-colors
                  ${idx < presentations.length - 1 ? "border-b border-[#1f2235]" : ""}`}
              >
                <div className="flex items-center gap-3">
                  <div className="h-8 w-8 rounded-lg bg-blue-950/60 border border-blue-900/40 flex items-center justify-center flex-shrink-0">
                    <svg viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="1.75" className="h-4 w-4">
                      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-[13px] font-medium text-gray-200">{p.title}</p>
                    <p className="text-[11.5px] text-gray-600">{p.audience}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-[11.5px] text-gray-600">{p.createdAt}</span>
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
