import { motion, Variants } from "motion/react";
import { ExternalLink, Blocks, FileText, Users, Database, MonitorPlay, Workflow, MessageSquare } from "lucide-react";

const MODULES = [
  { id: 1, name: "Projetos e Usuários", desc: "Controle de acesso (RBAC), equipes e sugestão inteligente de projetos.", icon: Users, url: "https://grupo1.azurewebsites.net", current: false, color: "text-indigo-600", bg: "bg-indigo-50", border: "border-indigo-100" },
  { id: 2, name: "Ingestão de Dados", desc: "Integração com GitHub, upload de arquivos e classificação automática.", icon: Database, url: "https://grupo2.azurewebsites.net", current: false, color: "text-emerald-600", bg: "bg-emerald-50", border: "border-emerald-100" },
  { id: 3, name: "Módulo de Relatórios", desc: "Elaboração inteligente de relatórios textuais ABNT estruturados.", icon: FileText, url: "https://moduloderelatorios.azurewebsites.net", current: false, color: "text-cyan-600", bg: "bg-cyan-50", border: "border-cyan-100" },
  { id: 4, name: "Módulo de Apresentações", desc: "Sua Fábrica de PowerPoints! Geração automatizada de slides com IA.", icon: MonitorPlay, url: "#", current: true, color: "text-amber-600", bg: "bg-amber-50", border: "border-amber-100" },
  { id: 5, name: "Diagramas Técnicos", desc: "Engenharia reversa visual de código fonte para geração automatizada de arquitetura.", icon: Workflow, url: "https://grupo5.azurewebsites.net", current: false, color: "text-rose-600", bg: "bg-rose-50", border: "border-rose-100" },
  { id: 6, name: "Módulo de Consulta", desc: "Chatbot inteligente alimentado com os materiais do projeto.", icon: MessageSquare, url: "https://grupo6.azurewebsites.net", current: false, color: "text-violet-600", bg: "bg-violet-50", border: "border-violet-100" },
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
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="w-full"
    >
      <motion.header variants={itemVariant} className="flex flex-col gap-4 mb-8">
        <h1 className="text-3xl font-semibold text-gray-900 flex items-center gap-3">
          <Blocks className="w-8 h-8 text-amber-500" />
          Ecossistema Mackenzie
        </h1>
        <p className="text-gray-500 text-base max-w-3xl">
          Plataforma de Documentação Inteligente de Projetos. Navegue pelos microsserviços que compõem este ecossistema distribuído de Engenharia de Software.
        </p>
      </motion.header>

      <motion.div variants={itemVariant} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {MODULES.map((mod) => (
          <a
            key={mod.id}
            href={mod.current ? undefined : mod.url}
            target={mod.current ? undefined : "_blank"}
            rel="noreferrer"
            className={`group flex flex-col gap-4 p-6 rounded-xl border bg-white shadow-sm transition-all duration-300 ${mod.current ? 'cursor-default ring-2 ring-amber-400 border-transparent' : 'cursor-pointer hover:-translate-y-1 hover:shadow-md border-gray-200'}`}
          >
            <div className="flex items-start justify-between">
              <div className={`p-3 rounded-lg border ${mod.bg} ${mod.color} ${mod.border}`}>
                <mod.icon className="w-6 h-6" />
              </div>
              {!mod.current && (
                <div className="p-1.5 rounded-full bg-gray-50 text-gray-400 group-hover:bg-gray-100 group-hover:text-gray-600 transition-colors">
                  <ExternalLink className="w-4 h-4" />
                </div>
              )}
            </div>

            <div className="mt-2">
              <div className="flex items-center gap-3 mb-1.5">
                <h3 className="text-base font-bold text-gray-900">{mod.name}</h3>
                {mod.current && (
                  <span className="px-2 py-0.5 rounded text-amber-700 bg-amber-100 text-[10px] font-bold uppercase tracking-wide">
                    Você está aqui
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-500 leading-relaxed">
                {mod.desc}
              </p>
            </div>
          </a>
        ))}
      </motion.div>
    </motion.div>
  );
}