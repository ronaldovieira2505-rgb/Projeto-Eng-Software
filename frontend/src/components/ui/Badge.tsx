import type { PresentationStatus } from "../../types";

const BADGE_STYLES: Record<PresentationStatus, string> = {
  Publicada: "bg-green-100 text-green-700",
  Pronta:    "bg-blue-100 text-blue-700",
  Rascunho:  "bg-gray-100 text-gray-600",
  Gerando:   "bg-yellow-100 text-yellow-700 animate-pulse",
};

interface BadgeProps {
  status: PresentationStatus;
}

export function Badge({ status }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${BADGE_STYLES[status]}`}
    >
      {status}
    </span>
  );
}
