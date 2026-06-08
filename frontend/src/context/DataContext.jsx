// @refresh reset
// src/context/DataContext.jsx
//
// Patients now come from the FastAPI backend (/patient/*)
// Templates still come from the Node.js/Express backend (/api/*)

import { createContext, useContext, useState, useEffect, useCallback, useRef } from "react";

const DataContext = createContext(null);

// ─── Helpers ──────────────────────────────────────────────────────────────────

// Auto-generate next 6-digit patient ID from existing list
function nextPatientId(patients) {
  const nums = patients
    .map((p) => parseInt(p.id, 10))
    .filter((n) => !isNaN(n) && n >= 100000 && n <= 999999);
  const next = nums.length > 0 ? Math.max(...nums) + 1 : 100001;
  return String(Math.min(next, 999999));
}

export function DataProvider({ children }) {
  const [patients,  setPatients]  = useState(null);
  const [templates, setTemplates] = useState(null);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState(null);

  const templatesRef = useRef(null);
  useEffect(() => { templatesRef.current = templates; }, [templates]);

  // ── Load patients from FastAPI ──────────────────────────────────────────────
  const refreshPatients = useCallback(async () => {
    try {
      const res = await fetch("/patient/view/md");
      if (!res.ok) throw new Error(`GET /patient/view/md → ${res.status}`);
      const data = await res.json(); // array of PatientMetaData JSON
      setPatients(data);
      setError(null);
    } catch (err) {
      console.error("Failed to load patients:", err);
      setError(err.message);
      setPatients([]);
    }
  }, []);

  // ── Load templates from Express ─────────────────────────────────────────────
  const refreshTemplates = useCallback(async () => {
    try {
      const res  = await fetch("/api/data");
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

  // ── Add patient (POST /patient/add/det with full Patient JSON) ──────────────
  const addPatient = useCallback(async (formData) => {
    // Build Patient JSON from form fields using exact variable names
    const id = formData.id || nextPatientId(patients || []);

    const patientJson = {
      metadata: {
        id:         id,
        name:       formData.name,
        age:        parseInt(formData.age, 10) || 0,
        number:     formData.number,
        is_active:  formData.is_active,
        last_visit: formData.last_visit || "",
      },
      visits:          [],
      follow_up_date:  formData.follow_up_date  || null,
      total_fees_paid: parseFloat(formData.total_fees_paid) || 0,
      fees_unpaid:     parseFloat(formData.fees_unpaid)     || 0,
      notes:           formData.notes || "",
    };

    const res = await fetch("/patient/add/det", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(patientJson),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to add patient");
    }
    await refreshPatients();
  }, [patients, refreshPatients]);

  // ── Update patient (PATCH /patient/edit/det/{id}) ───────────────────────────
  const updatePatient = useCallback(async (formData) => {
    const patientJson = {
      metadata: {
        id:         formData.id,
        name:       formData.name,
        age:        parseInt(formData.age, 10) || 0,
        number:     formData.number,
        is_active:  formData.is_active,
        last_visit: formData.last_visit || "",
      },
      visits:          formData.visits          || [],
      follow_up_date:  formData.follow_up_date  || null,
      total_fees_paid: parseFloat(formData.total_fees_paid) || 0,
      fees_unpaid:     parseFloat(formData.fees_unpaid)     || 0,
      notes:           formData.notes || "",
    };

    const res = await fetch(`/patient/edit/det/${formData.id}`, {
      method:  "PATCH",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(patientJson),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to update patient");
    }
    await refreshPatients();
  }, [refreshPatients]);

  // ── Delete patient (DELETE /patient/remove/{id}) ────────────────────────────
  const deletePatient = useCallback(async (id) => {
    const res = await fetch(`/patient/remove/${id}`, { method: "DELETE" });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to delete patient");
    }
    await refreshPatients();
  }, [refreshPatients]);

  // ── View full patient details (GET /patient/view/det/{id}) ──────────────────
  const fetchPatientDetails = useCallback(async (id) => {
    const res = await fetch(`/patient/view/det/${id}`);
    if (!res.ok) throw new Error(`Patient ${id} not found`);
    return res.json(); // full Patient JSON
  }, []);

  // ── Template mutations (still on Express) ───────────────────────────────────
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