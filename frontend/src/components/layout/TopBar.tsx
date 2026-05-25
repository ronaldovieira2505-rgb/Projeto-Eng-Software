import React from 'react';
import { 
  UploadCloud, 
  Users, 
  BarChart, 
  Presentation, 
  BookOpen, 
  Search,
  ExternalLink
} from 'lucide-react';

export function TopBar() {
  const navLinks = [
    {
      name: "Ingestão",
      icon: UploadCloud,
      url: "/", // Este é o projeto atual, logo leva para a home local
      isExternal: false
    },
    {
      name: "Projetos e Usuários",
      icon: Users,
      url: "SUBSTITUIR_URL_PROJETOS_E_USUARIOS",
      isExternal: true
    },
    {
      name: "Relatórios",
      icon: BarChart,
      url: "SUBSTITUIR_URL_RELATORIOS",
      isExternal: true
    },
    {
      name: "Apresentações",
      icon: Presentation,
      url: "SUBSTITUIR_URL_APRESENTACOES",
      isExternal: true
    },
    {
      name: "Diagramas e Doc. Técnicos",
      icon: BookOpen,
      url: "SUBSTITUIR_URL_DIAGRAMAS_E_DOCUMENTOS",
      isExternal: true
    },
    {
      name: "Consulta",
      icon: Search,
      url: "SUBSTITUIR_URL_CONSULTA",
      isExternal: true
    }
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-200 bg-white/90 backdrop-blur-md dark:border-gray-800 dark:bg-gray-950/90 shadow-sm">
      <div className="flex h-16 w-full items-center px-4 overflow-x-auto no-scrollbar">
        <nav className="flex items-center gap-2 sm:gap-6 min-w-max mx-auto">
          {navLinks.map((link, idx) => {
            const Icon = link.icon;
            // Se for o projeto atual (Ingestão), destacamos um pouco e não abre em nova guia
            const isActive = link.name === "Ingestão";

            return (
              <a
                key={idx}
                href={link.url}
                target={link.isExternal ? "_blank" : "_self"}
                rel={link.isExternal ? "noopener noreferrer" : ""}
                className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive 
                    ? "bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400" 
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white"
                }`}
                title={link.name}
              >
                <Icon className="h-4 w-4" />
                <span className="whitespace-nowrap">{link.name}</span>
                {link.isExternal && <ExternalLink className="h-3 w-3 opacity-50 ml-1" />}
              </a>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
