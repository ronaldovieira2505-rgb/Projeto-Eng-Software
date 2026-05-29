import type { Page } from "../../App";

interface NavigationProps {
  activePage: Page;
  onNavigate: (page: Page) => void;
}

export function Navigation({ activePage, onNavigate }: NavigationProps) {
  const tabs: { id: Page; label: string }[] = [
    { id: "dashboard", label: "Dashboard" },
    { id: "create", label: "Nova Apresentação" },
    { id: "settings", label: "Configurações" },
    { id: "modules", label: "Ecossistema" },
  ];

  return (
    <nav className="flex gap-8 -mb-px mt-2">
      {tabs.map((tab) => {
        const isActive = activePage === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onNavigate(tab.id)}
            className={`py-4 border-b-2 text-sm font-medium transition-colors tracking-wide ${
              isActive
                ? "border-cyan-400 text-cyan-400"
                : "border-transparent text-zinc-500 hover:text-zinc-300 hover:border-zinc-700"
            }`}
          >
            {tab.label}
          </button>
        );
      })}
    </nav>
  );
}