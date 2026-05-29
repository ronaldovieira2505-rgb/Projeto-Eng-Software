import {
  UploadCloud,
  Users,
  BarChart,
  Presentation,
  BookOpen,
  Search,
  LogOut,
  Hexagon
} from 'lucide-react';

export function Sidebar() {
  const navLinks = [
    { name: "Projetos e Usuários", icon: Users, url: "https://gerenciamento-projetos-users-e9fffgewdxe6gkfe.centralus-01.azurewebsites.net/#/login", isExternal: true },
    { name: "Ingestão", icon: UploadCloud, url: "https://mod2eng.azurewebsites.net/", isExternal: true },
    { name: "Relatórios", icon: BarChart, url: "https://moduloderelatorios.azurewebsites.net/", isExternal: true },
    { name: "Apresentações", icon: Presentation, url: "/", isExternal: false },
    { name: "Diagramas e Doc.", icon: BookOpen, url: "https://modulo5-interface-e-nuvem.azurewebsites.net/", isExternal: true },
    { name: "Consulta", icon: Search, url: "https://docai-frontend-7wym.onrender.com/", isExternal: true }
  ];

  return (
    <aside className="fixed top-0 left-0 h-screen w-64 bg-[#0A0A0A] border-r border-white/5 flex flex-col justify-between">
      {/* Topo / Logo */}
      <div className="p-6">
        <div className="flex items-center gap-3 mb-10">
          <Hexagon className="h-8 w-8 text-cyan-400" />
          <span className="text-xl font-semibold text-white tracking-wide">Mackenzie</span>
        </div>

        {/* Links do Ecossistema */}
        <nav className="flex flex-col gap-2">
          {navLinks.map((link, idx) => {
            const Icon = link.icon;
            const isActive = link.name === "Apresentações";

            return (
              <a
                key={idx}
                href={link.url}
                target={link.isExternal ? "_blank" : "_self"}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                  isActive 
                    ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20" 
                    : "text-zinc-400 hover:text-zinc-100 hover:bg-white/5 border border-transparent"
                }`}
              >
                <Icon className="h-5 w-5" />
                {link.name}
              </a>
            );
          })}
        </nav>
      </div>

      {/* Footer da Sidebar */}
      <div className="p-6 border-t border-white/5">
         <button className="flex items-center gap-3 text-sm font-medium text-zinc-500 hover:text-zinc-300 transition-colors w-full">
           <LogOut className="h-5 w-5" />
           Sair
         </button>
      </div>
    </aside>
  );
}