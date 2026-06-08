// @refresh reset
// src/context/TemplatesContext.jsx
// Pregnancy message templates now come from FastAPI (/templates/pregnancy)
// Data is persisted in templates_data.json on the server

import { createContext, useContext, useState, useEffect, useCallback } from "react";

const TemplatesContext = createContext(null);

export function TemplatesProvider({ children }) {
  const [pregnancy,    setPregnancy]    = useState(null);  // array of 40 templates
  const [loading,      setLoading]      = useState(true);
  const [error,        setError]        = useState(null);

  // ── Load all pregnancy templates from FastAPI ────────────────────────────────
  const refresh = useCallback(async () => {
    try {
      const res = await fetch("/templates/pregnancy");
      if (!res.ok) throw new Error(`GET /templates/pregnancy → ${res.status}`);
      const data = await res.json(); // array of { week, message, yt_link }
      setPregnancy(data);
      setError(null);
    } catch (err) {
      console.error("Failed to load pregnancy templates:", err);
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    refresh().finally(() => setLoading(false));
  }, [refresh]);

  // ── Update a single week via PATCH /templates/pregnancy/{week} ──────────────
  const updatePregnancyTemplate = useCallback(async (week, message, yt_link) => {
    // Optimistic update
    setPregnancy((prev) =>
      (prev || []).map((t) => t.week === week ? { ...t, message, yt_link } : t)
    );

    const res = await fetch(`/templates/pregnancy/${week}`, {
      method:  "PATCH",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ message, yt_link }),
    });

    if (!res.ok) {
      // Revert on failure
      await refresh();
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Failed to save week ${week}`);
    }

    const data = await res.json();
    // Sync with what server actually saved
    setPregnancy((prev) =>
      (prev || []).map((t) => t.week === week ? data.template : t)
    );
  }, [refresh]);

  return (
    <TemplatesContext.Provider value={{
      pregnancy,
      loading,
      error,
      refresh,
      updatePregnancyTemplate,
    }}>
      {children}
    </TemplatesContext.Provider>
  );
}

export function useTemplates() {
  const ctx = useContext(TemplatesContext);
  if (!ctx) throw new Error("useTemplates must be used inside <TemplatesProvider>");
  return ctx;
}