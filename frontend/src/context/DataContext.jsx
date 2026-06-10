// @refresh reset
// src/context/DataContext.jsx

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useRef,
} from "react";

const DataContext = createContext(null);

export function DataProvider({ children }) {
  const [patients, setPatients] = useState(null);
  const [templates, setTemplates] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const templatesRef = useRef(null);
  const patientsQueryRef = useRef({});

  useEffect(() => {
    templatesRef.current = templates;
  }, [templates]);

  // ─────────────────────────────────────────────────────────────
  // Load Patients
  // ─────────────────────────────────────────────────────────────

  const refreshPatients = useCallback(async (filters = patientsQueryRef.current) => {
    try {
      patientsQueryRef.current = filters || {};

      const params = new URLSearchParams();
      Object.entries(patientsQueryRef.current).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== "") {
          params.set(key, String(value));
        }
      });

      const query = params.toString();
      const url = query ? `/patients?${query}` : "/patients";
      const res = await fetch(url);

      if (!res.ok) {
        throw new Error(`GET ${url} failed with status ${res.status}`);
      }

      const data = await res.json();

      setPatients(data);
      setError(null);
    } catch (err) {
      console.error("Failed to load patients:", err);
      setError(err.message);
      setPatients([]);
    }
  }, []);

  // ─────────────────────────────────────────────────────────────
  // Load Templates
  // ─────────────────────────────────────────────────────────────

  const refreshTemplates = useCallback(async () => {
    try {
      const res = await fetch("/api/data");

      if (!res.ok) {
        throw new Error(`GET /api/data → ${res.status}`);
      }

      const data = await res.json();

      setTemplates(data.templates || []);
    } catch (err) {
      console.error("Failed to load templates:", err);
      setTemplates([]);
    }
  }, []);

  useEffect(() => {
    Promise.all([
      refreshPatients(),
      refreshTemplates(),
    ]).finally(() => setLoading(false));
  }, [refreshPatients, refreshTemplates]);

  // ─────────────────────────────────────────────────────────────
  // Generate Patient ID
  // ─────────────────────────────────────────────────────────────

  const generatePatientId = useCallback(async () => {
    const res = await fetch("/patients/id");

    if (!res.ok) {
      throw new Error(`GET /patients/id → ${res.status}`);
    }

    const data = await res.json();

    return String(data);
  }, []);

  // ─────────────────────────────────────────────────────────────
  // Build Request Body
  // Matches FastAPI create endpoint
  // ─────────────────────────────────────────────────────────────

  function buildPatientJson(formData) {
  let formattedDob = "";

  if (formData.dob) {
    const [year, month, day] = formData.dob.split("-");
    formattedDob = `${day}-${month}-${year}`;
  }

  return {
    id: formData.id,
    name: formData.name,
    dob: formattedDob,
    number: formData.number,
    condition: formData.condition || "",
    is_active:
      formData.is_active === true ||
      formData.is_active === "true",
  };
}

  // ─────────────────────────────────────────────────────────────
  // Add Patient
  // POST /patients
  // ─────────────────────────────────────────────────────────────

  const addPatient = useCallback(
    async (formData) => {
      const body = buildPatientJson(formData);

      const res = await fetch("/patients", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const err = await res
          .json()
          .catch(() => ({}));

        throw new Error(
          err.detail || "Failed to add patient"
        );
      }

      await refreshPatients();
    },
    [refreshPatients]
  );

  // ─────────────────────────────────────────────────────────────
  // Update Patient
  // PATCH /patients/{id}
  // NOTE:
  // Backend implementation currently incomplete.
  // ─────────────────────────────────────────────────────────────

  const updatePatient = useCallback(
    async (formData) => {
      const body = buildPatientJson(formData);

      const res = await fetch(
        `/patients/${formData.id}`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(body),
        }
      );

      if (!res.ok) {
        const err = await res
          .json()
          .catch(() => ({}));

        throw new Error(
          err.detail || "Failed to update patient"
        );
      }

      await refreshPatients();
    },
    [refreshPatients]
  );

  // ─────────────────────────────────────────────────────────────
  // Delete Patient
  // DELETE /patients/{id}
  // ─────────────────────────────────────────────────────────────

  const deletePatient = useCallback(
    async (id) => {
      const res = await fetch(
        `/patients/${id}`,
        {
          method: "DELETE",
        }
      );

      if (!res.ok) {
        const err = await res
          .json()
          .catch(() => ({}));

        throw new Error(
          err.detail || "Failed to delete patient"
        );
      }

      await refreshPatients();
    },
    [refreshPatients]
  );

  // ─────────────────────────────────────────────────────────────
  // Get Patient Details
  // GET /patients/{id}
  // ─────────────────────────────────────────────────────────────

  const fetchPatientDetails = useCallback(
    async (id) => {
      const res = await fetch(
        `/patients/${id}`
      );

      if (!res.ok) {
        throw new Error(
          `Patient ${id} not found`
        );
      }

      return await res.json();
    },
    []
  );

  // ─────────────────────────────────────────────────────────────
  // Template Updates
  // ─────────────────────────────────────────────────────────────

  const updateTemplate = useCallback(
    async (week, message) => {
      const next = (templatesRef.current || []).map(
        (t) =>
          t.week === week
            ? { ...t, message }
            : t
      );

      setTemplates(next);

      await fetch("/api/templates", {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify({
          templates: next,
        }),
      });
    },
    []
  );

  const isLoaded =
    patients !== null &&
    templates !== null;

  return (
    <DataContext.Provider
      value={{
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
      }}
    >
      {children}
    </DataContext.Provider>
  );
}

export function useData() {
  const ctx = useContext(DataContext);

  if (!ctx) {
    throw new Error(
      "useData must be used inside <DataProvider>"
    );
  }

  return ctx;
}
