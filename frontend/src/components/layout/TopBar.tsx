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
      name: "Projetos e Usuários",
      icon: Users,
      url: "https://grupo1.azurewebsites.net",
      isExternal: true
    },
    {
      name: "Ingestão",
      icon: UploadCloud,
      url: "https://grupo2.azurewebsites.net",
      isExternal: true
    },
    {
      name: "Relatórios",
      icon: BarChart,
      url: "https://moduloderelatorios.azurewebsites.net",
      isExternal: true
    },
    {
      name: "Apresentações",
      icon: Presentation,
      url: "/", // O SEU PROJETO ESTÁ AQUI
      isExternal: false
    },
    {
      name: "Diagramas e Doc. Técnicos",
      icon: BookOpen,
      url: "https://grupo5.azurewebsites.net",
      isExternal: true
    },
    {
      name: "Consulta",
      icon: Search,
      url: "https://grupo6.azurewebsites.net",
      isExternal: true
    }
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-200 bg-white/90 backdrop-blur-md shadow-sm">
      <div className="flex h-16 w-full items-center px-4 overflow-x-auto no-scrollbar">
        <nav className="flex items-center gap-2 sm:gap-6 min-w-max mx-auto">
          {navLinks.map((link, idx) => {
            const Icon = link.icon;

            // O destaque azul agora é exclusivo do SEU módulo
            const isActive = link.name === "Apresentações";

            return (
              <a
                key={idx}
                href={link.url}
                target={link.isExternal ? "_blank" : "_self"}
                rel={link.isExternal ? "noopener noreferrer" : ""}
                className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-amber-50 text-amber-700"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
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