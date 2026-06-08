// src/pages/templates/PregnancyTemplates.jsx

import { useState, useRef, useEffect } from "react";
import {
  ChevronDown, Save, RotateCcw, BookOpen,
  Link, CheckCircle2, Loader2, AlertCircle,
} from "lucide-react";
import { useTemplates } from "../../context/TemplatesContext";

export default function PregnancyTemplates() {
  const { pregnancy, loading, error, updatePregnancyTemplate } = useTemplates();

  const [selectedWeek, setSelectedWeek] = useState(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [searchText,   setSearchText]   = useState("");
  const dropdownRef = useRef(null);

  // Draft state
  const [draftMessage, setDraftMessage] = useState("");
  const [draftYtLink,  setDraftYtLink]  = useState("");
  const [isDirty,      setIsDirty]      = useState(false);
  const [saving,       setSaving]       = useState(false);
  const [saved,        setSaved]        = useState(false);
  const [saveError,    setSaveError]    = useState(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target))
        setDropdownOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const filteredWeeks = (pregnancy || []).filter((t) =>
    String(t.week).startsWith(searchText.trim()) ||
    `week ${t.week}`.includes(searchText.toLowerCase())
  );

  const handleSelectWeek = (week) => {
    const t = (pregnancy || []).find((t) => t.week === week);
    if (!t) return;
    setSelectedWeek(week);
    setDraftMessage(t.message);
    setDraftYtLink(t.yt_link || "");   // yt_link from FastAPI model
    setIsDirty(false);
    setSaved(false);
    setSaveError(null);
    setDropdownOpen(false);
    setSearchText("");
  };

  // Keep draft in sync if the selected week's data updates externally
  useEffect(() => {
    if (selectedWeek === null) return;
    const t = (pregnancy || []).find((t) => t.week === selectedWeek);
    if (t && !isDirty) {
      setDraftMessage(t.message);
      setDraftYtLink(t.yt_link || "");
    }
  }, [pregnancy, selectedWeek, isDirty]);

  const handleChange = (field, value) => {
    if (field === "message") setDraftMessage(value);
    if (field === "yt_link") setDraftYtLink(value);
    setIsDirty(true);
    setSaved(false);
    setSaveError(null);
  };

  const handleSave = async () => {
    if (!selectedWeek) return;
    setSaving(true);
    setSaveError(null);
    try {
      await updatePregnancyTemplate(selectedWeek, draftMessage, draftYtLink);
      setIsDirty(false);
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch (err) {
      setSaveError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    const t = (pregnancy || []).find((t) => t.week === selectedWeek);
    if (!t) return;
    setDraftMessage(t.message);
    setDraftYtLink(t.yt_link || "");
    setIsDirty(false);
    setSaveError(null);
  };

  if (loading) {
    return (
      <div className="flex items-center gap-3 text-slate-400 py-10">
        <Loader2 size={18} className="animate-spin" />
        <span className="text-sm">Loading templates…</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-rose-50 border border-rose-200 rounded-xl px-5 py-4 text-sm text-rose-700">
        <p className="font-semibold mb-1">Failed to load templates</p>
        <p className="font-mono text-xs">{error}</p>
        <p className="text-xs mt-1 text-rose-600">
          Make sure <code>uvicorn main:app --reload --port 8000</code> is running.
        </p>
      </div>
    );
  }

  const triggerLabel = selectedWeek ? `Week ${selectedWeek}` : "Select a week…";

  return (
    <div className="max-w-2xl">
      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">

        {/* Week dropdown */}
        <label className="block text-sm font-semibold text-slate-700 mb-1.5">
          Pregnancy Week
        </label>

        <div className="relative" ref={dropdownRef}>
          <button type="button"
            onClick={() => setDropdownOpen((o) => !o)}
            className="w-full flex items-center justify-between px-4 py-2.5
                       border border-slate-200 rounded-xl bg-white text-sm
                       text-slate-700 shadow-sm hover:border-teal-400
                       focus:outline-none focus:ring-2 focus:ring-teal-400 transition">
            <span className={selectedWeek ? "text-slate-800 font-medium" : "text-slate-400"}>
              {triggerLabel}
            </span>
            <ChevronDown size={16}
              className={`text-slate-400 transition-transform duration-200 ${dropdownOpen ? "rotate-180" : ""}`} />
          </button>

          {dropdownOpen && (
            <div className="absolute z-20 mt-1 w-full bg-white border border-slate-200
                            rounded-xl shadow-lg overflow-hidden">
              <div className="p-2 border-b border-slate-100">
                <input type="number" min="1" max="40" autoFocus
                  placeholder="Type week number (1–40)…"
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg
                             focus:outline-none focus:ring-2 focus:ring-teal-400 focus:border-transparent"
                />
              </div>
              <ul className="max-h-52 overflow-y-auto">
                {filteredWeeks.length > 0 ? (
                  filteredWeeks.map((t) => (
                    <li key={t.week}>
                      <button type="button"
                        onClick={() => handleSelectWeek(t.week)}
                        className={`w-full text-left px-4 py-2.5 text-sm transition-colors
                          hover:bg-teal-50 hover:text-teal-700
                          ${selectedWeek === t.week
                            ? "bg-teal-50 text-teal-700 font-semibold"
                            : "text-slate-700"}`}>
                        <span className="font-medium">Week {t.week}</span>
                        {t.message && (
                          <span className="ml-2 text-xs text-slate-400 truncate">
                            — {t.message.slice(0, 45)}{t.message.length > 45 ? "…" : ""}
                          </span>
                        )}
                      </button>
                    </li>
                  ))
                ) : (
                  <li className="px-4 py-3 text-sm text-slate-400">
                    No week found for "{searchText}".
                  </li>
                )}
              </ul>
            </div>
          )}
        </div>

        {/* Editor */}
        {selectedWeek !== null ? (
          <div className="mt-6 space-y-5">

            {/* Save error */}
            {saveError && (
              <div className="flex items-start gap-2 bg-rose-50 border border-rose-200
                              rounded-xl px-4 py-3 text-xs text-rose-700">
                <AlertCircle size={14} className="mt-0.5 flex-shrink-0" />
                <span>{saveError}</span>
              </div>
            )}

            {/* Message textarea */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-sm font-semibold text-slate-700 flex items-center gap-1.5">
                  <BookOpen size={14} className="text-teal-600" />
                  Message for Week {selectedWeek}
                </label>
                <span className="text-xs text-slate-400">{draftMessage.length} chars</span>
              </div>
              <textarea
                value={draftMessage}
                onChange={(e) => handleChange("message", e.target.value)}
                rows={7}
                className="w-full px-4 py-3 text-sm border border-slate-200 rounded-xl
                           bg-slate-50 text-slate-700 leading-relaxed resize-y
                           focus:outline-none focus:ring-2 focus:ring-teal-400
                           focus:border-transparent focus:bg-white transition"
              />
            </div>

            {/* YouTube link */}
            <div>
              <label className="text-sm font-semibold text-slate-700 flex items-center gap-1.5 mb-1.5">
                <Link size={14} className="text-indigo-500" />
                YouTube Link
                <span className="text-xs text-slate-400 font-normal">(optional)</span>
              </label>
              <input
                type="url"
                value={draftYtLink}
                onChange={(e) => handleChange("yt_link", e.target.value)}
                placeholder="https://youtube.com/watch?v=…"
                className="w-full px-4 py-2.5 text-sm border border-slate-200 rounded-xl
                           bg-slate-50 text-slate-700 focus:outline-none focus:ring-2
                           focus:ring-indigo-400 focus:border-transparent focus:bg-white transition"
              />
              {draftYtLink && (
                <a href={draftYtLink} target="_blank" rel="noopener noreferrer"
                  className="mt-1.5 inline-flex items-center gap-1 text-xs text-indigo-600
                             hover:text-indigo-800 hover:underline">
                  <Link size={11} /> Open link
                </a>
              )}
            </div>

            {/* Action buttons */}
            <div className="flex items-center gap-3 pt-1">
              <button onClick={handleSave} disabled={!isDirty || saving}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold
                  transition-all duration-150
                  ${isDirty && !saving
                    ? "bg-teal-600 hover:bg-teal-700 text-white shadow-sm"
                    : "bg-slate-100 text-slate-400 cursor-not-allowed"}`}>
                {saving
                  ? <Loader2 size={14} className="animate-spin" />
                  : <Save size={14} />}
                {saving ? "Saving…" : "Save"}
              </button>

              <button onClick={handleReset} disabled={!isDirty || saving}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold
                  transition-all duration-150 border
                  ${isDirty && !saving
                    ? "border-slate-200 text-slate-600 hover:bg-slate-50"
                    : "border-slate-100 text-slate-300 cursor-not-allowed"}`}>
                <RotateCcw size={14} />
                Reset
              </button>

              {saved && (
                <span className="flex items-center gap-1.5 text-sm text-teal-600 font-medium">
                  <CheckCircle2 size={15} />
                  Saved!
                </span>
              )}
            </div>

            {isDirty && (
              <p className="text-xs text-amber-500">You have unsaved changes.</p>
            )}
          </div>
        ) : (
          <div className="mt-6 flex flex-col items-center justify-center py-12 text-center
                          border-2 border-dashed border-slate-200 rounded-xl">
            <BookOpen size={32} className="text-slate-300 mb-3" />
            <p className="text-sm text-slate-400">
              Select a pregnancy week above to view and edit its template.
            </p>
          </div>
        )}
      </div>

      {/* Info card */}
      <div className="mt-4 bg-indigo-50 border border-indigo-100 rounded-xl px-5 py-4">
        <p className="text-xs font-semibold text-indigo-700 mb-1">How templates work</p>
        <p className="text-xs text-indigo-600 leading-relaxed">
          When sending a message to a pregnant patient, the system looks up their current
          pregnancy week (calculated from their due date) and sends the template for that week,
          including the YouTube link if one is set. All templates are saved in{" "}
          <span className="font-mono">templates_data.json</span> via the FastAPI backend.
        </p>
      </div>
    </div>
  );
}