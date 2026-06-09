// @refresh reset
// src/context/DataContext.jsx
//
// Patient fields: id · name · dob · number · condition · is_active
// All other fields (age, last_visit, follow_up_date, fees, notes) removed.

import { createContext, useContext, useState, useEffect, useCallback, useRef } from "react";

const DataContext = createContext(null);

export function DataProvider({ children }) {
  const [patients,  setPatients]  = useState(null);
  const [templates, setTemplates] = useState(null);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState(null);

  const templatesRef = useRef(null);
  useEffect(() => { templatesRef.current = templates; }, [templates]);

  // ── Load patients ───────────────────────────────────────────────────────────
  const refreshPatients = useCallback(async () => {
    try {
      const res = await fetch("/patient/view/md");
      if (!res.ok) throw new Error(`GET /patient/view/md → ${res.status}`);
      setPatients(await res.json());
      setError(null);
    } catch (err) {
      console.error("Failed to load patients:", err);
      setError(err.message);
      setPatients([]);
    }
  }, []);

  // ── Load templates (from Express) ───────────────────────────────────────────
  const refreshTemplates = useCallback(async () => {
    try {
      const res = await fetch("/api/data");
      if (!res.ok) throw new Error(`GET /api/data → ${res.status}`);
      const data = await res.json();
      setTemplates(data.templates || []);
    } catch (err) {
      console.error("Failed to load templates:", err);
      setTemplates([]);
    }
  }, []);

  useEffect(() => {
    Promise.all([refreshPatients(), refreshTemplates()])
      .finally(() => setLoading(false));
  }, [refreshPatients, refreshTemplates]);

  // ── Generate Patient ID (GET /patient/id) ───────────────────────────────────
  // Called by the Add Patient button before opening the form.
  // Returns the generated ID string, or throws on failure.
  const generatePatientId = useCallback(async () => {
    const res = await fetch("/patient/id");
    if (!res.ok) throw new Error(`GET /patient/id → ${res.status}`);
    const data = await res.json();
    // FastAPI returns { patient_id: "100123" }
    return String(data.patient_id);
  }, []);

  // ── Build Patient JSON (POST / PATCH body) ──────────────────────────────────
  // Maps the flat form object the page sends into the Patient schema
  // the FastAPI backend expects.
  //
  // Patient schema (FastAPI):
  //   metadata: { id, name, dob, number, condition, is_active }
  //
  // NOTE: visits, follow_up_date, total_fees_paid, fees_unpaid, notes are
  // kept as empty/zero so the backend doesn't reject the request. Remove
  // them here once the backend schema is updated to not require them.
  function buildPatientJson(formData, existingVisits = []) {
    return {
      metadata: {
        id:         formData.id,
        name:       formData.name,
        dob:        formData.dob         || "",
        number:     formData.number,
        condition:  formData.condition   || "",
        is_active:  formData.is_active,
      },
      visits:          existingVisits,
      follow_up_date:  null,
      total_fees_paid: 0,
      fees_unpaid:     0,
      notes:           "",
    };
  }

  // ── Add patient (POST /patient/add/det) ─────────────────────────────────────
  const addPatient = useCallback(async (formData) => {
    const body = buildPatientJson({
      ...formData,
      is_active: formData.is_active === "true" || formData.is_active === true,
    });
    const res = await fetch("/patient/add/det", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(body),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to add patient");
    }
    await refreshPatients();
  }, [refreshPatients]);

  // ── Update patient (PATCH /patient/edit/det/{id}) ───────────────────────────
  const updatePatient = useCallback(async (formData) => {
    // Preserve existing visits if available on the formData
    const body = buildPatientJson(
      {
        ...formData,
        is_active: formData.is_active === "true" || formData.is_active === true,
      },
      formData.visits || []
    );
    const res = await fetch(`/patient/edit/det/${formData.id}`, {
      method:  "PATCH",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(body),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to update patient");
    }
    await refreshPatients();
  }, [refreshPatients]);

  // ── Delete patient (DELETE /patient/remove/{id}) ────────────────────────────
  const deletePatient = useCallback(async (id) => {
    const res = await fetch(`/patient/remove/${id}`, { method: "DELETE" });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to delete patient");
    }
    await refreshPatients();
  }, [refreshPatients]);

  // ── Fetch full patient details (GET /patient/view/det/{id}) ────────────────
  const fetchPatientDetails = useCallback(async (id) => {
    const res = await fetch(`/patient/view/det/${id}`);
    if (!res.ok) throw new Error(`Patient ${id} not found`);
    return res.json();
  }, []);

  // ── Update template (Express) ───────────────────────────────────────────────
  const updateTemplate = useCallback(async (week, message) => {
    const next = (templatesRef.current || []).map((t) =>
      t.week === week ? { ...t, message } : t
    );
    setTemplates(next);
    await fetch("/api/templates", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ templates: next }),
    });
  }, []);

  const isLoaded = patients !== null && templates !== null;

  return (
    <DataContext.Provider value={{
      patients,
      templates,
      loading,
      error,
      isLoaded,
      refreshPatients,
      generatePatientId,
      addPatient,
      updatePatient,
      deletePatient,
      fetchPatientDetails,
      updateTemplate,
    }}>
      {children}
    </DataContext.Provider>
  );
}

export function useData() {
  const ctx = useContext(DataContext);
  if (!ctx) throw new Error("useData must be used inside <DataProvider>");
  return ctx;
}