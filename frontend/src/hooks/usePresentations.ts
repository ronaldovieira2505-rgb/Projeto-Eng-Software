import { useState } from "react";
import type { Presentation, GenerateFromCommitsRequest } from "../types";
import { presentationsApi } from "../services/api";

// Dados mock para demonstração (substituir pela API real quando disponível)
const MOCK_PRESENTATIONS: Presentation[] = [
  {
    id: "1",
    title: "Sprint Review - Q2 2026",
    type: "Sprint Review",
    audience: "Tech Lead",
    status: "Publicada",
    createdAt: "2026-04-20",
    downloadUrl: "#",
  },
  {
    id: "2",
    title: "Arquitetura do Sistema",
    type: "Arquitetura Técnica",
    audience: "Tech Lead",
    status: "Pronta",
    createdAt: "2026-04-18",
    downloadUrl: "#",
  },
  {
    id: "3",
    title: "Roadmap de Produto",
    type: "Roadmap de Produto",
    audience: "Product Manager",
    status: "Rascunho",
    createdAt: "2026-04-15",
  },
];

const MOCK_STATS = {
  presentationsCreated: 24,
  commitsAnalyzed: 1247,
  hoursSaved: 48,
  approvalRate: 94,
};

export function usePresentations() {
  const [presentations, setPresentations] =
    useState<Presentation[]>(MOCK_PRESENTATIONS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generate(data: GenerateFromCommitsRequest): Promise<boolean> {
    setLoading(true);
    setError(null);

    // Placeholder de status "Gerando" enquanto a API processa
    const tempId = `temp-${Date.now()}`;
    const tempPresentation: Presentation = {
      id: tempId,
      title: data.title || "Nova Apresentação",
      type: data.presentation_type,
      audience: data.audience,
      status: "Gerando",
      createdAt: new Date().toISOString().split("T")[0],
    };
    setPresentations((prev) => [tempPresentation, ...prev]);

    try {
      const result = await presentationsApi.generateFromCommits(data);

      setPresentations((prev) =>
        prev.map((p) =>
          p.id === tempId
            ? {
                ...p,
                id: result.presentation_id,
                title: result.title,
                status: "Pronta",
                downloadUrl: result.download_url,
                shareUrl: result.share_url,
                slides: result.slides,
              }
            : p
        )
      );
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao gerar apresentação.");
      setPresentations((prev) => prev.filter((p) => p.id !== tempId));
      return false;
    } finally {
      setLoading(false);
    }
  }

  return {
    presentations,
    stats: MOCK_STATS,
    loading,
    error,
    generate,
  };
}
