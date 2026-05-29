import { useState } from "react";
import { GitBranch, FileCode2, Link as LinkIcon, Loader2, Sparkles, AlertCircle } from "lucide-react";
interface CreatePresentationProps {
  onGenerate: (data: { repo_url: string; swagger_url?: string; file_paths?: string[] }) => Promise<boolean>;
  loading: boolean;
  error: string | null;
}

export function CreatePresentation({ onGenerate, loading, error }: CreatePresentationProps) {
  const [repoUrl, setRepoUrl] = useState("");
  const [swaggerUrl, setSwaggerUrl] = useState("");
  const [filePaths, setFilePaths] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Converte a string de ficheiros separados por vírgula num array
    const filesArray = filePaths
      .split(',')
      .map(p => p.trim())
      .filter(p => p.length > 0);

    await onGenerate({
      repo_url: repoUrl,
      swagger_url: swaggerUrl,
      file_paths: filesArray.length > 0 ? filesArray : undefined
    });
  };

  return (
    <div className="max-w-2xl mx-auto w-full animate-in fade-in slide-in-from-bottom-4 duration-500">

      <div className="mb-8">
        <h2 className="text-3xl font-light text-white tracking-tight flex items-center gap-3">
          Nova <span className="font-semibold text-cyan-400">Apresentação</span>
          <Sparkles className="w-6 h-6 text-cyan-400" />
        </h2>
        <p className="text-zinc-400 mt-2 text-lg font-light">
          Configure a IA para gerar os seus slides técnicos a partir do código fonte.
        </p>
      </div>

      <div className="bg-[#0A0A0A]/40 backdrop-blur-xl border border-white/[0.05] rounded-[2rem] p-8 shadow-2xl relative overflow-hidden">
        {/* Brilho de fundo (Efeito visual) */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/5 rounded-full blur-3xl -z-10 transform translate-x-1/2 -translate-y-1/2"></div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-6 relative z-10">

          {/* Campo: Repositório GitHub */}
          <div className="flex flex-col gap-2">
            <label htmlFor="repoUrl" className="text-sm font-medium text-zinc-300 ml-1">
              URL do Repositório (GitHub) <span className="text-cyan-400">*</span>
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-zinc-500">
                <GitBranch className="h-5 w-5" />
              </div>
              <input
                id="repoUrl"
                type="url"
                required
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                placeholder="https://github.com/usuario/projeto"
                className="w-full bg-white/[0.02] border border-white/10 rounded-xl py-3.5 pl-12 pr-4 text-zinc-200 placeholder:text-zinc-600 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all"
              />
            </div>
          </div>

          {/* Campo: Link do Swagger (US #025) */}
          <div className="flex flex-col gap-2">
            <label htmlFor="swaggerUrl" className="text-sm font-medium text-zinc-300 ml-1 flex items-center justify-between">
              <span>Link da Documentação (Swagger)</span>
              <span className="text-[10px] font-bold uppercase tracking-wider text-zinc-600 border border-white/10 px-2 py-0.5 rounded-md">Opcional</span>
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-zinc-500">
                <LinkIcon className="h-5 w-5" />
              </div>
              <input
                id="swaggerUrl"
                type="url"
                value={swaggerUrl}
                onChange={(e) => setSwaggerUrl(e.target.value)}
                placeholder="https://api.projeto.com/docs"
                className="w-full bg-white/[0.02] border border-white/10 rounded-xl py-3.5 pl-12 pr-4 text-zinc-200 placeholder:text-zinc-600 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all"
              />
            </div>
          </div>

          {/* Campo: Ficheiros Soltos (US #007) */}
          <div className="flex flex-col gap-2">
            <label htmlFor="filePaths" className="text-sm font-medium text-zinc-300 ml-1 flex items-center justify-between">
              <span>Caminhos de Ficheiros Específicos</span>
              <span className="text-[10px] font-bold uppercase tracking-wider text-zinc-600 border border-white/10 px-2 py-0.5 rounded-md">Opcional</span>
            </label>
            <div className="relative">
              <div className="absolute top-4 left-0 pl-4 flex items-start pointer-events-none text-zinc-500">
                <FileCode2 className="h-5 w-5" />
              </div>
              <textarea
                id="filePaths"
                value={filePaths}
                onChange={(e) => setFilePaths(e.target.value)}
                placeholder="Ex: docs/arquitetura.md, src/core/main.py"
                rows={3}
                className="w-full bg-white/[0.02] border border-white/10 rounded-xl py-3.5 pl-12 pr-4 text-zinc-200 placeholder:text-zinc-600 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all resize-none"
              />
            </div>
            <p className="text-xs text-zinc-500 ml-1 mt-1">
              Separe os caminhos por vírgulas. Deixe em branco para analisar todo o repositório.
            </p>
          </div>

          {/* Mensagem de Erro */}
          {error && (
            <div className="flex items-center gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <p>{error}</p>
            </div>
          )}

          {/* Botão de Submissão */}
          <button
            type="submit"
            disabled={loading || !repoUrl}
            className={`mt-4 w-full flex items-center justify-center gap-2 py-4 rounded-xl text-sm font-bold tracking-wide transition-all ${
              loading || !repoUrl
                ? "bg-zinc-800 text-zinc-500 cursor-not-allowed border border-white/5"
                : "bg-gradient-to-r from-cyan-500 to-blue-500 text-black hover:opacity-90 shadow-[0_0_20px_rgba(6,182,212,0.3)] hover:shadow-[0_0_25px_rgba(6,182,212,0.5)]"
            }`}
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                A PROCESSAR COM IA...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                GERAR APRESENTAÇÃO
              </>
            )}
          </button>

        </form>
      </div>
    </div>
  );
}