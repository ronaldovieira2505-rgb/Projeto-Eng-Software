import { useState } from "react";
import type { AppSettings } from "../types";
import { DEFAULT_SETTINGS } from "../types";

const STORAGE_KEY = "app_settings";

function loadSettings(): AppSettings {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    return raw ? { ...DEFAULT_SETTINGS, ...JSON.parse(raw) } : DEFAULT_SETTINGS;
  } catch {
    return DEFAULT_SETTINGS;
  }
}

export function useSettings() {
  const [settings, setSettings] = useState<AppSettings>(loadSettings);
  const [saved, setSaved] = useState(false);

  function update(partial: Partial<AppSettings>) {
    setSettings((prev) => ({ ...prev, ...partial }));
    setSaved(false);
  }

  function save() {
    // Nunca persiste chaves de API em localStorage (apenas na sessão)
    const { githubToken, openaiApiKey, ...safeSettings } = settings;
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(safeSettings));
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  }

  return { settings, update, save, saved };
}
