// src/pages/AddVisit.jsx

import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { AlertCircle, Loader2, ArrowLeft, Search } from "lucide-react";
import { useData } from "../context/DataContext";

function toDDMMYYYY(isoDate) {
  if (!isoDate) return null;
  const parts = isoDate.split("-");
  if (parts.length !== 3) return isoDate;
  const [y, m, d] = parts;
  return `${d}-${m}-${y}`;
}

function Field({ label, required, error, children }) {
  return (
    <div>
      <label className="block text-xs font-semibold text-slate-600 mb-1">
        {label}{required && <span className="text-rose-500 ml-0.5">*</span>}
      </label>
      {children}
      {error && (
        <p className="mt-1 text-xs text-rose-500 flex items-center gap-1">
          <AlertCircle size={11} />{error}
        </p>
      )}
    </div>
  );
}

export default function AddVisit() {
  const navigate = useNavigate();
  const { addVisit, generateVisitId, refreshVisits } = useData();

  const [loadingId, setLoadingId] = useState(true);
  const [idError,   setIdError]   = useState(false);
  const [saving,    setSaving]    = useState(false);
  const [serverError, setServerError] = useState(null);

  const [form, setForm] = useState({
    visit_id: "",
    patient_id: "",
    patient_name: "",
    visit_date: "",
    diagnosis: "",
    prescription: "",
    notes: "",
    fees_paid: "",
    fees_pending: "",
    follow_up_date: "",
  });

  const { searchPatients } = useData();
  const [patientResults, setPatientResults] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [searching, setSearching] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    const timer = setTimeout(async () => {
      if (!form.patient_name.trim()) {
        setPatientResults([]);
        setSearching(false);
        return;
      }
      setSearching(true);
      const results = await searchPatients(form.patient_name, 10);
      setPatientResults(results);
      setSearching(false);
    }, 200);
    return () => clearTimeout(timer);
  }, [form.patient_name, searchPatients]);

  const handleSelectPatient = (patient) => {
    setForm((p) => ({ ...p, patient_id: patient.id, patient_name: patient.name }));
    setShowDropdown(false);
  };

  const handlePatientSearchChange = (e) => {
    set("patient_name", e.target.value);
    setShowDropdown(true);
  };

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        if (typeof generateVisitId !== "function") {
          setIdError(true);
          return;
        }
        const id = await generateVisitId();
        const resolved =
          typeof id === "string" ? id : (id?.visit_id ?? id?.id ?? "");
        if (!cancelled) setForm((p) => ({ ...p, visit_id: resolved }));
      } catch (err) {
        console.warn("Could not auto-generate visit ID:", err.message);
        if (!cancelled) setIdError(true);
      } finally {
        if (!cancelled) setLoadingId(false);
      }
    })();
    return () => { cancelled = true; };
  }, [generateVisitId]);

  const set = (key, value) => setForm((p) => ({ ...p, [key]: value }));

  const handleSubmit = async () => {
    setSaving(true);
    setServerError(null);
    try {
      await addVisit({
        id: form.visit_id,
        patient_id: form.patient_id,
        date: toDDMMYYYY(form.visit_date),
        diagnosis: form.diagnosis,
        prescription: form.prescription,
        notes: form.notes,
        fees_paid: form.fees_paid === "" ? 0 : Number(form.fees_paid),
        fees_pending: form.fees_pending === "" ? 0 : Number(form.fees_pending),
        follow_up_date: toDDMMYYYY(form.follow_up_date),
      });
      await refreshVisits();
      navigate("/visits");
    } catch (err) {
      setServerError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-lg mx-auto">
      <button onClick={() => navigate("/visits")}
        className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-indigo-600
                   font-semibold mb-4 transition">
        <ArrowLeft size={15} /> Back to Visits
      </button>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-100">
        <div className="px-6 py-4 border-b border-slate-100">
          <h1 className="text-lg font-bold text-slate-800">Add Visit</h1>
        </div>

        <div className="px-6 py-5 space-y-4">
          {serverError && (
            <div className="bg-rose-50 border border-rose-200 rounded-xl px-4 py-3 text-xs text-rose-700 font-medium">
              {serverError}
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <Field
              label="Visit ID"
              error={idError ? "Auto-ID failed — enter manually" : undefined}
            >
              {loadingId ? (
                <div className="flex items-center gap-2 px-3 py-2 text-sm border border-slate-200
                                rounded-xl bg-slate-50 text-slate-400">
                  <Loader2 size={13} className="animate-spin" />
                  Generating…
                </div>
              ) : idError ? (
                <input
                  placeholder="Enter Visit ID"
                  value={form.visit_id}
                  onChange={(e) => set("visit_id", e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-amber-300 rounded-xl bg-amber-50
                             text-slate-700 focus:outline-none focus:ring-2 focus:ring-amber-400 transition"
                />
              ) : (
                <input
                  value={form.visit_id}
                  disabled
                  className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl
                             bg-slate-50 text-slate-500 cursor-not-allowed"
                />
              )}
            </Field>

            <Field label="Patient ID" required>
              <input
                placeholder="Enter Patient ID"
                value={form.patient_id}
                onChange={(e) => set("patient_id", e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white
                           text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-400 transition"
              />
            </Field>

            <div className="relative" ref={dropdownRef}>
              <Field label="Patient Name" required>
                <input
                  placeholder="Type to search patients..."
                  value={form.patient_name}
                  onChange={handlePatientSearchChange}
                  onFocus={() => setShowDropdown(true)}
                  className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white
                             text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-400 transition"
                />
              </Field>

              {showDropdown && form.patient_name.trim() !== "" && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-slate-200 rounded-xl shadow-lg max-h-60 overflow-y-auto">
                  {searching ? (
                    <div className="flex items-center gap-2 px-4 py-3 text-sm text-slate-500">
                      <Loader2 size={14} className="animate-spin" /> Searching...
                    </div>
                  ) : patientResults.length > 0 ? (
                    <ul className="py-1">
                      {patientResults.map((p) => (
                        <li key={p.id}>
                          <button
                            type="button"
                            onClick={() => handleSelectPatient(p)}
                            className="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-indigo-50 hover:text-indigo-700 transition"
                          >
                            {p.name} - {p.id}
                          </button>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <div className="px-4 py-3 text-sm text-slate-500">No patients found.</div>
                  )}
                </div>
              )}
            </div>
          </div>

          <Field label="Visit Date" required>
            <input type="date" value={form.visit_date}
              onChange={(e) => set("visit_date", e.target.value)}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white
                         text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-400 transition" />
          </Field>

          <Field label="Diagnosis">
            <textarea placeholder="Enter diagnosis…" value={form.diagnosis}
              onChange={(e) => set("diagnosis", e.target.value)} rows={2}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white
                         text-slate-700 resize-y focus:outline-none focus:ring-2 focus:ring-indigo-400 transition" />
          </Field>

          <Field label="Prescription">
            <textarea placeholder="Enter prescription…" value={form.prescription}
              onChange={(e) => set("prescription", e.target.value)} rows={2}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white
                         text-slate-700 resize-y focus:outline-none focus:ring-2 focus:ring-indigo-400 transition" />
          </Field>

          <Field label="Notes">
            <textarea placeholder="Clinical notes…" value={form.notes}
              onChange={(e) => set("notes", e.target.value)} rows={2}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white
                         text-slate-700 resize-y focus:outline-none focus:ring-2 focus:ring-indigo-400 transition" />
          </Field>

          <div className="grid grid-cols-2 gap-3">
            <Field label="Fees Paid (₹)">
              <input type="number" placeholder="0.00" value={form.fees_paid}
                onChange={(e) => set("fees_paid", e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white
                           text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-400 transition" />
            </Field>
            <Field label="Fees Pending (₹)">
              <input type="number" placeholder="0.00" value={form.fees_pending}
                onChange={(e) => set("fees_pending", e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white
                           text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-400 transition" />
            </Field>
          </div>

          <Field label="Follow-up Date">
            <input type="date" value={form.follow_up_date}
              onChange={(e) => set("follow_up_date", e.target.value)}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white
                         text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-400 transition" />
          </Field>
        </div>

        <div className="flex justify-end gap-3 px-6 py-4 border-t border-slate-100">
          <button onClick={() => navigate("/visits")}
            className="px-4 py-2 text-sm font-semibold text-slate-600 border border-slate-200
                       rounded-xl hover:bg-slate-50 transition">
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={saving || loadingId || (idError && !form.visit_id.trim())}
            className="flex items-center gap-2 px-5 py-2 text-sm font-semibold text-white
                       bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-sm transition disabled:opacity-50">
            {saving && <Loader2 size={13} className="animate-spin" />}
            Add Visit
          </button>
        </div>
      </div>
    </div>
  );
}
