import type { PresentationType } from "../../types";

interface TypeOption {
  id: PresentationType;
  label: string;
  description: string;
  icon: JSX.Element;
}

export const PRESENTATION_TYPES: TypeOption[] = [
  {
    id: "sprint_review",
    label: "Sprint Review",
    description: "Apresentação de entregas da sprint",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="h-5 w-5">
        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
        <polyline points="10 9 9 9 8 9" />
      </svg>
    ),
  },
  {
    id: "architecture",
    label: "Arquitetura Técnica",
    description: "Documentação de decisões arquiteturais",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="h-5 w-5">
        <polyline points="16 18 22 12 16 6" />
        <polyline points="8 6 2 12 8 18" />
      </svg>
    ),
  },
  {
    id: "roadmap",
    label: "Roadmap de Produto",
    description: "Visão de futuro e próximos passos",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="h-5 w-5">
        <rect x="2" y="7" width="20" height="14" rx="2" />
        <path d="M16 3v4M8 3v4M2 11h20" />
      </svg>
    ),
  },
  {
    id: "live_demo",
    label: "Live Demo",
    description: "Demonstração de funcionalidades",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="h-5 w-5">
        <path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6L12 2z" />
      </svg>
    ),
  },
];

interface PresentationTypeCardProps {
  option: TypeOption;
  selected: boolean;
  onSelect: (id: PresentationType) => void;
}

export function PresentationTypeCard({
  option,
  selected,
  onSelect,
}: PresentationTypeCardProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect(option.id)}
      className={`flex flex-col gap-2 p-4 rounded-xl border-2 text-left transition-all
        ${
          selected
            ? "border-blue-600 bg-blue-50"
            : "border-gray-200 bg-white hover:border-gray-300"
        }`}
    >
      <div className={`${selected ? "text-blue-600" : "text-gray-500"}`}>
        {option.icon}
      </div>
      <div>
        <p className={`font-medium text-sm ${selected ? "text-blue-700" : "text-gray-800"}`}>
          {option.label}
        </p>
        <p className="text-xs text-gray-500 mt-0.5">{option.description}</p>
      </div>
    </button>
  );
}
