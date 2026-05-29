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
    { id: "modules", label: "Ecossistema" }, // A nossa nova aba aqui!
  ];

  return (
    <nav className="flex gap-6 -mb-px">
      {tabs.map((tab) => {
        const isActive = activePage === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onNavigate(tab.id)}
            className={`py-4 px-1 border-b-2 text-sm font-medium transition-colors ${
              isActive
                ? "border-amber-500 text-amber-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            {tab.label}
          </button>
        );
      })}
    </nav>
  );
}