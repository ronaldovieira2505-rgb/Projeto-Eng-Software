import { motion, Variants } from "motion/react";
import { ExternalLink, Blocks, FileText, Users, Database, MonitorPlay, Workflow, MessageSquare } from "lucide-react";

const MODULES = [
  { id: 1, name: "Projetos e Usuários", desc: "Controle de acesso (RBAC), equipes e sugestão inteligente de projetos.", icon: Users, url: "https://grupo1.azurewebsites.net", current: false, color: "text-indigo-400", bg: "bg-indigo-500/10", border: "border-indigo-500/20" },
  { id: 2, name: "Ingestão de Dados", desc: "Integração com GitHub, upload de arquivos e classificação automática.", icon: Database, url: "https://grupo2.azurewebsites.net", current: false, color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20" },
  { id: 3, name: "Módulo de Relatórios", desc: "Elaboração inteligente de relatórios textuais ABNT estruturados.", icon: FileText, url: "https://moduloderelatorios.azurewebsites.net", current: false, color: "text-cyan-400", bg: "bg-cyan-500/10", border: "border-cyan-500/20" },
  { id: 4, name: "Módulo de Apresentações", desc: "Sua Fábrica de PowerPoints! Geração automatizada de slides com IA.", icon: MonitorPlay, url: "#", current: true, color: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/20" },
  { id: 5, name: "Diagramas Técnicos", desc: "Engenharia reversa visual de código fonte para geração automatizada de arquitetura.", icon: Workflow, url: "https://grupo5.azurewebsites.net", current: false, color: "text-rose-400", bg: "bg-rose-500/10", border: "border-rose-500/20" },
  { id: 6, name: "Módulo de Consulta", desc: "Chatbot inteligente alimentado com os materiais do projeto.", icon: MessageSquare, url: "https://grupo6.azurewebsites.net", current: false, color: "text-violet-400", bg: "bg-violet-500/10", border: "border-violet-500/20" },
];

export function Modules() {
  const container: Variants = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } },
  };

  const itemVariant: Variants = {
    hidden: { opacity: 0, y: 20 },
    show: {
      opacity: 1,
      y: 0,
      transition: { type: "spring", stiffness: 300, damping: 24 },
    },
  };

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="w-full relative z-10">
      <motion.header variants={itemVariant} className="flex flex-col gap-4 mb-10">
        <h1 className="text-4xl font-light text-white tracking-tight flex items-center gap-4">
          Ecossistema <span className="font-semibold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-indigo-500">Mackenzie</span>
          <Blocks className="w-8 h-8 text-cyan-400" />
        </h1>
        <p className="text-zinc-400 text-lg font-light max-w-2xl">
          Plataforma de Documentação Inteligente de Projetos. Navegue pelos microsserviços que compõem este ecossistema distribuído de Engenharia de Software.
        </p>
      </motion.header>

      <motion.div variants={itemVariant} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {MODULES.map((mod) => (
          <a
            key={mod.id}
            href={mod.current ? undefined : mod.url}
            target={mod.current ? undefined : "_blank"}
            rel="noreferrer"
            className={`group flex flex-col gap-4 p-6 sm:p-8 rounded-[2rem] border border-white/[0.05] bg-[#0A0A0A]/40 backdrop-blur-xl shadow-2xl transition-all duration-500 ${mod.current ? 'cursor-default ring-1 ring-cyan-500/20' : 'cursor-pointer hover:-translate-y-2 hover:bg-white/[0.02] hover:border-cyan-500/20'}`}
          >
            <div className="flex items-start justify-between">
              <div className={`p-4 rounded-2xl border ${mod.bg} ${mod.color} ${mod.border}`}>
                <mod.icon className="w-7 h-7" />
              </div>
              {!mod.current && (
                <div className="p-2 rounded-full bg-white/[0.03] text-zinc-500 group-hover:bg-white/[0.1] group-hover:text-white transition-colors">
                  <ExternalLink className="w-4 h-4" />
                </div>
              )}
            </div>

            <div className="mt-4">
              <div className="flex items-center gap-3 mb-2">
                <h3 className="text-lg font-bold text-zinc-200 group-hover:text-white transition-colors tracking-tight">{mod.name}</h3>
                {mod.current && (
                  <span className="px-2 py-0.5 rounded-md bg-cyan-500/20 text-cyan-400 text-[9px] font-black uppercase tracking-widest border border-cyan-500/30">
                    Você está aqui
                  </span>
                )}
              </div>
              <p className="text-sm font-medium text-zinc-500 leading-relaxed group-hover:text-zinc-400 transition-colors">
                {mod.desc}
              </p>
            </div>
          </a>
        ))}
      </motion.div>
    </motion.div>
  );
}