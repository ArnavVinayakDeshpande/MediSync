// @refresh reset
// src/context/DataContext.jsx

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";

const DataContext = createContext(null);

const API = "";

export function DataProvider({ children }) {
  const [patients, setPatients] = useState([]);
  const [visits,   setVisits]   = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [error,    setError]    = useState(null);

  // --------------------------------------------------
  // Generic Request Helper
  // --------------------------------------------------

  const request = useCallback(async (url, options = {}) => {
    const res = await fetch(`${API}${url}`, {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
    });

    if (!res.ok) {
      let err = {};
      try { err = await res.json(); } catch {}
      throw new Error(err.detail || `${options.method || "GET"} ${url} failed (${res.status})`);
    }

    if (res.status === 204) return null;

    try { return await res.json(); } catch { return null; }
  }, []);

  // --------------------------------------------------
  // Patients
  // --------------------------------------------------

  const refreshPatients = useCallback(async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== "")
          params.append(key, value);
      });
      const url = params.toString() ? `/patients?${params}` : "/patients";
      const data = await request(url);
      setPatients(data || []);
      setError(null);
    } catch (err) {
      setError(err.message);
      setPatients([]);
    }
  }, [request]);

  const generatePatientId = useCallback(async () => {
    return await request("/patients/id");
  }, [request]);

  const addPatient = useCallback(async (patient) => {
    await request("/patients", {
      method: "POST",
      body: JSON.stringify(patient),
    });
    await refreshPatients();
  }, [request, refreshPatients]);

  const updatePatient = useCallback(async (patient) => {
    await request(`/patients/${patient.id}`, {
      method: "PATCH",
      body: JSON.stringify(patient),
    });
    await refreshPatients();
  }, [request, refreshPatients]);

  const deletePatient = useCallback(async (patientId) => {
    // delete the patient's visits first, then the patient
    await request(`/visits?patient_id=${patientId}`, { method: "DELETE" });
    await request(`/patients/${patientId}`,           { method: "DELETE" });
    await refreshPatients();
  }, [request, refreshPatients]);

  const getPatient = useCallback(async (patientId) => {
    return await request(`/patients/${patientId}`);
  }, [request]);

  // --------------------------------------------------
  // Visits
  // --------------------------------------------------

  const refreshVisits = useCallback(async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== "")
          params.append(key, value);
      });
      const url = params.toString() ? `/visits?${params}` : "/visits";
      const data = await request(url);
      setVisits(data || []);
      setError(null);
      return data || [];
    } catch (err) {
      setError(err.message);
      setVisits([]);
      return [];
    }
  }, [request]);

  // Calls GET /visits/id  →  backend returns the next auto-generated visit ID.
  // The response can be either a plain string ("V001") or an object ({ "id": "V001" }).
  // AddVisitModal in Visits.jsx handles both shapes.
  const generateVisitId = useCallback(async () => {
    return await request("/visits/id");
  }, [request]);

  const getVisit = useCallback(async (visitId) => {
    return await request(`/visits/${visitId}`);
  }, [request]);

  const addVisit = useCallback(async (visitData) => {
    await request("/visits", {
      method: "POST",
      body: JSON.stringify(visitData),
    });
    await refreshVisits();
  }, [request, refreshVisits]);

  const updateVisit = useCallback(async (visitId, visitData) => {
    await request(`/visits/${visitId}`, {
      method: "PATCH",
      body: JSON.stringify(visitData),
    });
    await refreshVisits();
  }, [request, refreshVisits]);

  const deleteVisit = useCallback(async (visitId) => {
    await request(`/visits/${visitId}`, { method: "DELETE" });
    await refreshVisits();
  }, [request, refreshVisits]);

  // --------------------------------------------------
  // Patient Details  (patient metadata + their visits)
  // --------------------------------------------------

  const fetchPatientDetails = useCallback(async (patientId) => {
    const [patient, patientVisits] = await Promise.all([
      request(`/patients/${patientId}`),
      request(`/visits?patient_id=${patientId}`),
    ]);
    return {
      metadata: patient,
      visits:   patientVisits || [],
    };
  }, [request]);

  // --------------------------------------------------
  // Initial Load
  // --------------------------------------------------

  useEffect(() => {
    Promise.all([refreshPatients(), refreshVisits()])
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [refreshPatients, refreshVisits]);

  return (
    <DataContext.Provider
      value={{
        loading,
        error,

        patients,
        visits,

        refreshPatients,
        generatePatientId,
        getPatient,
        addPatient,
        updatePatient,
        deletePatient,

        refreshVisits,
        generateVisitId,
        getVisit,
        addVisit,
        updateVisit,
        deleteVisit,

        fetchPatientDetails,
      }}
    >
      {children}
    </DataContext.Provider>
  );
}

export function useData() {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error("useData must be used inside <DataProvider>");
  }
  return context;
}