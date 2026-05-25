import type { Page } from "../../App";

interface SidebarProps {
  activePage: Page;
  onNavigate: (page: Page) => void;
}

const NAV_ITEMS: { id: Page; label: string; icon: JSX.Element }[] = [
  {
    id: "dashboard",
    label: "Dashboard",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" className="h-[18px] w-[18px]">
        <rect x="3" y="3" width="7" height="7" rx="1.5" />
        <rect x="14" y="3" width="7" height="7" rx="1.5" />
        <rect x="3" y="14" width="7" height="7" rx="1.5" />
        <rect x="14" y="14" width="7" height="7" rx="1.5" />
      </svg>
    ),
  },
  {
    id: "create",
    label: "Criar Apresentação",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" className="h-[18px] w-[18px]">
        <rect x="3" y="3" width="18" height="14" rx="2" />
        <path d="M8 21h8M12 17v4" />
        <path d="M9 9l2 2 4-4" />
      </svg>
    ),
  },
  {
    id: "settings",
    label: "Configurações",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" className="h-[18px] w-[18px]">
        <circle cx="12" cy="12" r="3" />
        <path d="M12 2v3M12 19v3M4.22 4.22l2.12 2.12M17.66 17.66l2.12 2.12M2 12h3M19 12h3M4.22 19.78l2.12-2.12M17.66 6.34l2.12-2.12" />
      </svg>
    ),
  },
];

export function Sidebar({ activePage, onNavigate }: SidebarProps) {
  return (
    <aside className="w-56 min-w-[224px] bg-[#13151d] border-r border-[#1f2235] flex flex-col min-h-screen">
      {/* Brand */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-[#1f2235]">
        <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center flex-shrink-0">
          <svg viewBox="0 0 24 24" fill="white" className="h-4 w-4">
            <path d="M12 3C7.02 3 3 7.02 3 12s4.02 9 9 9 9-4.02 9-9-4.02-9-9-9zm0 4a2 2 0 110 4 2 2 0 010-4zm0 10c-2.67 0-5.01-1.33-6.4-3.36.03-2.12 4.27-3.29 6.4-3.29 2.12 0 6.37 1.17 6.4 3.29C17.01 15.67 14.67 17 12 17z" />
          </svg>
        </div>
        <span className="text-[15px] font-medium text-white tracking-tight">Mackenzie</span>
      </div>

      {/* Nav items */}
      <nav className="flex flex-col gap-0.5 px-2.5 pt-3 flex-1">
        {NAV_ITEMS.map((item) => {
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`
                flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-[13.5px] font-normal
                transition-all duration-150 text-left
                ${isActive
                  ? "bg-[#1a2640] text-blue-400"
                  : "text-gray-400 hover:bg-[#1a1d2e] hover:text-gray-200"
                }
              `}
            >
              <span className={isActive ? "text-blue-400" : "text-gray-500"}>
                {item.icon}
              </span>
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* Footer / Logout */}
      <div className="px-2.5 pb-5 pt-3 border-t border-[#1f2235] mt-auto">
        <button className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-[13px] text-gray-500 hover:text-gray-300 hover:bg-[#1a1d2e] transition-all duration-150">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" className="h-[18px] w-[18px]">
            <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" y1="12" x2="9" y2="12" />
          </svg>
          Sair
        </button>
      </div>
    </aside>
  );
}
