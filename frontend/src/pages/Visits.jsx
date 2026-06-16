// src/pages/Visits.jsx
//
// Shows all visits across all patients in one table.
// API endpoints (update in VISIT_ENDPOINTS when finalised):
//   GET    /visits              → list all visits
//   PATCH  /visits/{visit_id}   → update a visit
//   DELETE /visits/{visit_id}   → delete a visit
//
// Clicking a patient name opens a read-only patient preview via GET /patients/{id}

import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  Eye, Pencil, Trash2, X, AlertCircle, Loader2,
  Search, ArrowUpDown, ArrowUp, ArrowDown, User, UserPlus
} from "lucide-react";
import { useData } from "../context/DataContext";

// ─── Helpers ──────────────────────────────────────────────────────────────────

function fmt(val, prefix = "") {
  if (val === null || val === undefined || val === "") return "—";
  return `${prefix}${val}`;
}

function visitDateTs(str) {
  if (!str) return 0;
  const parts = str.split("-");
  if (parts.length < 3) return 0;
  const [d, m, y] = parts;
  const year = y.length <= 2 ? 2000 + parseInt(y, 10) : parseInt(y, 10);
  return new Date(year, parseInt(m, 10) - 1, parseInt(d, 10)).getTime();
}

// Converts standard HTML <input type="date"> value (YYYY-MM-DD) → backend format (DD-MM-YYYY)
function toDDMMYYYY(isoDate) {
  if (!isoDate) return null;
  const parts = isoDate.split("-");
  if (parts.length !== 3) return isoDate;
  const [y, m, d] = parts;
  return `${d}-${m}-${y}`;
}

// Converts backend date format (DD-MM-YYYY) → HTML <input type="date"> value (YYYY-MM-DD)
function toYYYYMMDD(backendDate) {
  if (!backendDate) return "";
  const parts = backendDate.split("-");
  if (parts.length !== 3) return "";
  const [d, m, y] = parts;
  // Handle 2-digit years stored as DD-MM-YY (e.g. "15-07-25" → "2025-07-15")
  const fullYear = y.length === 2 ? `20${y}` : y;
  return `${fullYear}-${m}-${d}`;
}

// ─── Field wrapper ─────────────────────────────────────────────────────────────

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

// ─── Add Visit Modal ──────────────────────────────────────────────────────────

function AddVisitModal({ onSave, onClose, generateVisitId }) {
  // loadingId: true while we're fetching the next visit ID from the backend
  // idError:   true if the fetch failed — in that case the field becomes editable
  const [loadingId, setLoadingId] = useState(true);
  const [idError,   setIdError]   = useState(false);

  const [form, setForm] = useState({
    visit_id: "",
    patient_id: "",
    visit_date: "",
    diagnosis: "",
    prescription: "",
    notes: "",
    fees_paid: "",
    fees_pending: "",
    follow_up_date: "",
  });

  useEffect(() => {
    // We wrap everything in a plain async IIFE so the effect itself is synchronous.
    // Any rejection is caught here — React 18 will white-screen on unhandled rejections
    // inside effects, so the catch is mandatory.
    (async () => {
      try {
        if (typeof generateVisitId !== "function") {
          // Backend endpoint not wired up yet — let the user type the ID manually
          setIdError(true);
          return;
        }
        const id = await generateVisitId();
        const resolved =
          typeof id === "string" ? id : (id?.visit_id ?? id?.id ?? "");
        setForm((p) => ({ ...p, visit_id: resolved }));
      } catch (err) {
        // GET /visits/id failed (404, network error, etc.)
        // Don't crash — just let the user type the ID manually
        console.warn("Could not auto-generate visit ID:", err.message);
        setIdError(true);
      } finally {
        setLoadingId(false);
      }
    })();
  }, [generateVisitId]);

  const set = (key, value) => setForm((p) => ({ ...p, [key]: value }));

  const handleSubmit = async () => {
    // Mapping to Python Backend expectations (models/visit.py & converter.py)
    await onSave({
      id: form.visit_id,
      patient_id: form.patient_id, // Passed so context can route if needed
      date: toDDMMYYYY(form.visit_date), 
      diagnosis: form.diagnosis,
      prescription: form.prescription,
      notes: form.notes,
      fees_paid: form.fees_paid === "" ? 0 : Number(form.fees_paid),
      fees_pending: form.fees_pending === "" ? 0 : Number(form.fees_pending),
      follow_up_date: toDDMMYYYY(form.follow_up_date),
    });
  };

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/40 px-4 py-6 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg my-auto">
        
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <div>
            <h2 className="text-base font-bold text-slate-800">Add Visit</h2>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition">
            <X size={18} />
          </button>
        </div>

        <div className="px-6 py-5 space-y-4 max-h-[70vh] overflow-y-auto">
          <div className="grid grid-cols-2 gap-3">
            <Field
              label="Visit ID"
              error={idError ? "Auto-ID failed — enter manually" : undefined}
            >
              {loadingId ? (
                // Spinner while fetching the ID
                <div className="flex items-center gap-2 px-3 py-2 text-sm border border-slate-200 rounded-xl bg-slate-50 text-slate-400">
                  <Loader2 size={13} className="animate-spin" />
                  Generating…
                </div>
              ) : idError ? (
                // ID fetch failed — let the doctor type it
                <input
                  placeholder="Enter Visit ID"
                  value={form.visit_id}
                  onChange={(e) => set("visit_id", e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-amber-300 rounded-xl bg-amber-50
                             text-slate-700 focus:outline-none focus:ring-2 focus:ring-amber-400 transition"
                />
              ) : (
                // ID loaded successfully — read-only display
                <input
                  value={form.visit_id}
                  disabled
                  className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-slate-50 text-slate-500 cursor-not-allowed"
                />
              )}
            </Field>
            <Field label="Patient ID" required>
              <input placeholder="Enter Patient ID" value={form.patient_id} onChange={(e) => set("patient_id", e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-400 transition" />
            </Field>
          </div>

          <Field label="Visit Date" required>
            <input type="date" value={form.visit_date} onChange={(e) => set("visit_date", e.target.value)}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-400 transition" />
          </Field>

          <Field label="Diagnosis">
            <textarea placeholder="Enter diagnosis…" value={form.diagnosis} onChange={(e) => set("diagnosis", e.target.value)} rows={2}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white text-slate-700 resize-y focus:outline-none focus:ring-2 focus:ring-indigo-400 transition" />
          </Field>

          <Field label="Prescription">
            <textarea placeholder="Enter prescription…" value={form.prescription} onChange={(e) => set("prescription", e.target.value)} rows={2}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white text-slate-700 resize-y focus:outline-none focus:ring-2 focus:ring-indigo-400 transition" />
          </Field>

          <Field label="Notes">
            <textarea placeholder="Clinical notes…" value={form.notes} onChange={(e) => set("notes", e.target.value)} rows={2}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white text-slate-700 resize-y focus:outline-none focus:ring-2 focus:ring-indigo-400 transition" />
          </Field>

          <div className="grid grid-cols-2 gap-3">
            <Field label="Fees Paid (₹)">
              <input type="number" placeholder="0.00" value={form.fees_paid} onChange={(e) => set("fees_paid", e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-400 transition" />
            </Field>
            <Field label="Fees Pending (₹)">
              <input type="number" placeholder="0.00" value={form.fees_pending} onChange={(e) => set("fees_pending", e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-400 transition" />
            </Field>
          </div>

          <Field label="Follow-up Date">
            <input type="date" value={form.follow_up_date} onChange={(e) => set("follow_up_date", e.target.value)}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-400 transition" />
          </Field>
        </div>

        <div className="flex justify-end gap-3 px-6 py-4 border-t border-slate-100">
          <button onClick={onClose}
            className="px-4 py-2 text-sm font-semibold text-slate-600 border border-slate-200 rounded-xl hover:bg-slate-50 transition">
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={loadingId || (idError && !form.visit_id.trim())}
            className="flex items-center gap-2 px-5 py-2 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-sm transition disabled:opacity-50">
            {loadingId && <Loader2 size={13} className="animate-spin" />}
            Add Visit
          </button>
        </div>

      </div>
    </div>
  );
}

// ─── Visit Edit Form ──────────────────────────────────────────────────────────

function VisitEditModal({ visit, onSave, onClose }) {
  const [form, setForm] = useState({
    diagnosis:      visit.diagnosis      || "",
    prescription:   visit.prescription   || "",
    notes:          visit.notes          || "",
    fees_paid:      String(visit.fees_paid    ?? ""),
    fees_pending:   String(visit.fees_pending ?? ""),
    // visit.follow_up_date arrives as DD-MM-YYYY from backend; convert to YYYY-MM-DD for date input
    follow_up_date: toYYYYMMDD(visit.follow_up_date),
  });
  const [errors,      setErrors]      = useState({});
  const [saving,      setSaving]      = useState(false);
  const [serverError, setServerError] = useState(null);

  const set = (key, val) => {
    setForm((p) => ({ ...p, [key]: val }));
    setErrors((p) => ({ ...p, [key]: "" }));
  };

  const validate = () => {
    const e = {};
    if (form.fees_paid !== "" && isNaN(Number(form.fees_paid)))
      e.fees_paid = "Must be a number.";
    if (form.fees_pending !== "" && isNaN(Number(form.fees_pending)))
      e.fees_pending = "Must be a number.";
    return e;
  };

  const handleSubmit = async () => {
    const e = validate();
    if (Object.keys(e).length > 0) { setErrors(e); return; }
    setSaving(true);
    setServerError(null);
    try {
      await onSave(visit.visit_id, {
        diagnosis:      form.diagnosis,
        prescription:   form.prescription,
        notes:          form.notes,
        fees_paid:      form.fees_paid    !== "" ? parseFloat(form.fees_paid)    : null,
        fees_pending:   form.fees_pending !== "" ? parseFloat(form.fees_pending) : null,
        // Convert YYYY-MM-DD (date input) back to DD-MM-YYYY expected by visit_from_json_fmt
        follow_up_date: toDDMMYYYY(form.follow_up_date) || null,
      });
    } catch (err) {
      setServerError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/40 px-4 py-6 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg my-auto">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <div>
            <h2 className="text-base font-bold text-slate-800">Edit Visit</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Visit #{visit.visit_id} · {visit.visit_date} · {visit.patient_name}
            </p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition">
            <X size={18} />
          </button>
        </div>

        <div className="px-6 py-5 space-y-4 max-h-[70vh] overflow-y-auto">
          {serverError && (
            <div className="bg-rose-50 border border-rose-200 rounded-xl px-4 py-3 text-xs text-rose-700">
              {serverError}
            </div>
          )}

          <Field label="Diagnosis">
            <textarea value={form.diagnosis} onChange={(e) => set("diagnosis", e.target.value)}
              rows={3} placeholder="Enter diagnosis…"
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white
                         text-slate-700 resize-y focus:outline-none focus:ring-2
                         focus:ring-indigo-400 focus:border-transparent transition" />
          </Field>

          <Field label="Prescription">
            <textarea value={form.prescription} onChange={(e) => set("prescription", e.target.value)}
              rows={3} placeholder="Enter prescription…"
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white
                         text-slate-700 resize-y focus:outline-none focus:ring-2
                         focus:ring-indigo-400 focus:border-transparent transition" />
          </Field>

          <Field label="Notes">
            <textarea value={form.notes} onChange={(e) => set("notes", e.target.value)}
              rows={2} placeholder="Clinical notes…"
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white
                         text-slate-700 resize-y focus:outline-none focus:ring-2
                         focus:ring-indigo-400 focus:border-transparent transition" />
          </Field>

          <div className="grid grid-cols-2 gap-3">
            <Field label="Fees Paid (₹)" error={errors.fees_paid}>
              <input type="text" value={form.fees_paid}
                onChange={(e) => set("fees_paid", e.target.value)}
                placeholder="0.00" inputMode="decimal"
                className={`w-full px-3 py-2 text-sm border rounded-xl transition
                  focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent
                  ${errors.fees_paid ? "border-rose-300 bg-rose-50" : "border-slate-200 bg-white text-slate-700"}`}
              />
            </Field>
            <Field label="Fees Pending (₹)" error={errors.fees_pending}>
              <input type="text" value={form.fees_pending}
                onChange={(e) => set("fees_pending", e.target.value)}
                placeholder="0.00" inputMode="decimal"
                className={`w-full px-3 py-2 text-sm border rounded-xl transition
                  focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent
                  ${errors.fees_pending ? "border-rose-300 bg-rose-50" : "border-slate-200 bg-white text-slate-700"}`}
              />
            </Field>
          </div>

          <Field label="Follow-up Date">
            <input type="date" value={form.follow_up_date}
              onChange={(e) => set("follow_up_date", e.target.value)}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white
                         text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-400
                         focus:border-transparent transition" />
          </Field>
        </div>

        <div className="flex justify-end gap-3 px-6 py-4 border-t border-slate-100">
          <button onClick={onClose} disabled={saving}
            className="px-4 py-2 text-sm font-semibold text-slate-600 border border-slate-200
                       rounded-xl hover:bg-slate-50 transition disabled:opacity-50">
            Cancel
          </button>
          <button onClick={handleSubmit} disabled={saving}
            className="flex items-center gap-2 px-5 py-2 text-sm font-semibold text-white
                       bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-sm transition disabled:opacity-50">
            {saving && <Loader2 size={13} className="animate-spin" />}
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Visit Detail Row ──────────────────────────────────────────────────────────

function DRow({ label, value }) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-start gap-1 py-2.5
                    border-b border-slate-100 last:border-0">
      <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide
                       sm:w-44 flex-shrink-0">{label}</span>
      <span className="text-sm text-slate-800 whitespace-pre-wrap">{value ?? "—"}</span>
    </div>
  );
}

// ─── Visit Details Modal ───────────────────────────────────────────────────────

function VisitDetailsModal({ visit, onClose, onEdit, onDelete, onPatientClick }) {
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [deleting,      setDeleting]      = useState(false);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await onDelete(visit.visit_id);
    } catch (err) {
      setDeleting(false);
      setConfirmDelete(false);
      alert(`Delete failed: ${err.message}`);
    }
  };

  const hasPending = (visit.fees_pending ?? 0) > 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4 py-6 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-xl my-auto">
        <div className="flex items-start justify-between px-6 py-4 border-b border-slate-100">
          <div>
            <p className="text-xs text-slate-400 font-mono">Visit #{visit.visit_id}</p>
            <h2 className="text-base font-bold text-slate-800 mt-0.5">{visit.visit_date}</h2>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0 ml-4">
            <button onClick={() => onEdit(visit)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold
                         bg-indigo-50 text-indigo-600 hover:bg-indigo-100 rounded-lg transition">
              <Pencil size={12} /> Edit
            </button>
            {!confirmDelete ? (
              <button onClick={() => setConfirmDelete(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold
                           bg-rose-50 text-rose-600 hover:bg-rose-100 rounded-lg transition">
                <Trash2 size={12} /> Delete
              </button>
            ) : (
              <div className="flex items-center gap-2 bg-rose-50 border border-rose-200
                              rounded-xl px-3 py-1.5">
                <span className="text-xs text-rose-700 font-semibold">Confirm?</span>
                <button onClick={handleDelete} disabled={deleting}
                  className="text-xs font-bold text-white bg-rose-600 hover:bg-rose-700
                             px-2 py-1 rounded-lg transition disabled:opacity-50">
                  {deleting ? <Loader2 size={11} className="animate-spin" /> : "Yes"}
                </button>
                <button onClick={() => setConfirmDelete(false)}
                  className="text-xs font-semibold text-slate-600 hover:text-slate-800 transition">
                  No
                </button>
              </div>
            )}
            <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition ml-1">
              <X size={18} />
            </button>
          </div>
        </div>

        <div className="px-6 py-4 max-h-[70vh] overflow-y-auto">
          <div className="flex items-center gap-3 mb-4 bg-slate-50 border border-slate-200
                          rounded-xl px-4 py-3">
            <div className="w-9 h-9 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
              <User size={16} className="text-indigo-600" />
            </div>
            <div>
              <p className="text-[11px] text-slate-500 font-semibold uppercase tracking-wide">Patient</p>
              <button
                onClick={() => onPatientClick(visit.patient_id)}
                className="text-sm font-bold text-indigo-600 hover:text-indigo-800 hover:underline
                           transition text-left"
              >
                {visit.patient_name}
              </button>
              <p className="text-xs text-slate-400 font-mono">{visit.patient_id}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="bg-green-50 border border-green-200 rounded-xl px-4 py-3">
              <p className="text-[11px] font-semibold text-green-600 uppercase tracking-wide">Fees Paid</p>
              <p className="text-xl font-bold text-green-800 mt-0.5">
                {visit.fees_paid != null ? `₹${visit.fees_paid.toFixed(2)}` : "—"}
              </p>
            </div>
            <div className={`border rounded-xl px-4 py-3
              ${hasPending ? "bg-amber-50 border-amber-200" : "bg-slate-50 border-slate-200"}`}>
              <p className={`text-[11px] font-semibold uppercase tracking-wide
                ${hasPending ? "text-amber-600" : "text-slate-500"}`}>
                Fees Pending
              </p>
              <p className={`text-xl font-bold mt-0.5
                ${hasPending ? "text-amber-800" : "text-slate-800"}`}>
                {visit.fees_pending != null ? `₹${visit.fees_pending.toFixed(2)}` : "—"}
              </p>
            </div>
          </div>

          <DRow label="Diagnosis"    value={visit.diagnosis} />
          <DRow label="Prescription" value={visit.prescription} />
          <DRow label="Notes"        value={visit.notes} />
          <DRow label="Follow-up"    value={visit.follow_up_date || "None"} />
        </div>

        <div className="px-6 py-4 border-t border-slate-100 flex justify-end">
          <button onClick={onClose}
            className="px-4 py-2 text-sm font-semibold text-slate-600 border border-slate-200
                       rounded-xl hover:bg-slate-50 transition">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Patient Preview Modal (read-only) ────────────────────────────────────────

function PatientPreviewModal({ patientId, fetchPatientDetails, onClose }) {
  const [details,    setDetails]    = useState(null);
  const [loading,    setLoading]    = useState(true);
  const [fetchError, setFetchError] = useState(null);
  const fetched = useRef(false);

  useEffect(() => {
    if (fetched.current) return;
    fetched.current = true;
    fetchPatientDetails(patientId)
      .then(setDetails)
      .catch((err) => setFetchError(err.message))
      .finally(() => setLoading(false));
  }, [patientId, fetchPatientDetails]);

  const md = details?.metadata;

  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center bg-black/50 px-4 py-6 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg my-auto">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <div>
            <h2 className="text-base font-bold text-slate-800">{md?.name ?? "Patient Details"}</h2>
            <p className="text-xs text-slate-400 font-mono mt-0.5">ID: {patientId}</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition">
            <X size={18} />
          </button>
        </div>

        <div className="px-6 py-4 max-h-[65vh] overflow-y-auto">
          {loading ? (
            <div className="flex items-center gap-2 text-slate-400 py-8 justify-center">
              <Loader2 size={16} className="animate-spin" /> Loading…
            </div>
          ) : fetchError ? (
            <div className="bg-rose-50 border border-rose-100 rounded-xl px-4 py-3 text-sm text-rose-600">
              {fetchError}
            </div>
          ) : details ? (
            <>
              <DRow label="Patient ID"     value={md?.id} />
              <DRow label="Name"           value={md?.name} />
              <DRow label="Date of Birth"  value={md?.dob} />
              <DRow label="Contact"        value={md?.number} />
              <DRow label="Condition"      value={md?.condition} />
              <DRow label="Active Status"  value={md?.is_active ? "Active" : "Inactive"} />
            </>
          ) : null}
        </div>

        <div className="px-6 py-4 border-t border-slate-100 flex justify-end">
          <button onClick={onClose}
            className="px-4 py-2 text-sm font-semibold text-slate-600 border border-slate-200
                       rounded-xl hover:bg-slate-50 transition">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Sort Button ──────────────────────────────────────────────────────────────

function SortBtn({ sortKey, currentKey, sortDir, label, onClick }) {
  const active = currentKey === sortKey;
  return (
    <button onClick={() => onClick(sortKey)}
      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold
        border transition whitespace-nowrap
        ${active
          ? "bg-indigo-600 text-white border-indigo-600"
          : "bg-white text-slate-600 border-slate-200 hover:border-indigo-300"}`}>
      {active
        ? sortDir === "asc" ? <ArrowUp size={12} /> : <ArrowDown size={12} />
        : <ArrowUpDown size={12} className="text-slate-400" />}
      {label}
    </button>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

const PAGE_SIZE = 50;

export default function Visits() {
  const {
    fetchPatientDetails,
    visits,
    refreshVisits,
    getVisit,
    updateVisit,
    deleteVisit,
  } = useData();
  const navigate = useNavigate();

  const [loading,         setLoading]         = useState(true);
  const [fetchError,      setFetchError]      = useState(null);
  const [query,           setQuery]           = useState("");
  const [debouncedQuery,  setDebouncedQuery]  = useState("");
  const [sortKey,         setSortKey]         = useState("visit_date");
  const [sortDir,         setSortDir]         = useState("desc");
  const [page,            setPage]            = useState(0);

  // modal: null | { type: "view", visit } 
  //        | { type: "edit", visit } | { type: "patientPreview", patientId }
  const [modal, setModal] = useState(null);

  // ── Debounce the search query by 500ms ──
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
      setPage(0);
    }, 500);
    return () => clearTimeout(timer);
  }, [query]);

  // ── Load visits (with search + pagination) ──
  const loadVisits = useCallback(async () => {
    setLoading(true);
    try {
      await refreshVisits({
        size:   PAGE_SIZE,
        offset: page * PAGE_SIZE,
        search: debouncedQuery,
      });
      setFetchError(null);
    } catch (err) {
      setFetchError(err.message);
    } finally {
      setLoading(false);
    }
  }, [refreshVisits, page, debouncedQuery]);

  useEffect(() => { loadVisits(); }, [loadVisits]);

  // ── Update visit ─────────────────────────────────────────────────────────
  const handleUpdateVisit = async (visitId, changes) => {
    try {
      const existing = await getVisit(visitId);
      const payload = {
        ...existing,
        ...changes,
      };
      await updateVisit(visitId, payload);
      await loadVisits();
      setModal(null);
    } catch (err) {
      throw err;
    }
  };

  // ── Delete visit ─────────────────────────────────────────────────────────
  const handleDeleteVisit = async (visitId) => {
    await deleteVisit(visitId);
    await loadVisits();
    setModal(null);
  };

  const handleSort = (key) => {
    if (sortKey === key) setSortDir((d) => d === "asc" ? "desc" : "asc");
    else { setSortKey(key); setSortDir("desc"); }
  };

  // ── Filter + sort ────────────────────────────────────────────────────────
  const displayed = useMemo(() => {
    let list = [...visits];
    // Search is now handled server-side via the `search` param — no local filtering needed
    list.sort((a, b) => {
      let av, bv;
      if (sortKey === "visit_id")     { av = a.visit_id;              bv = b.visit_id; }
      if (sortKey === "visit_date")   { av = visitDateTs(a.visit_date); bv = visitDateTs(b.visit_date); }
      if (sortKey === "patient_name") { av = (a.patient_name || "").toLowerCase(); bv = (b.patient_name || "").toLowerCase(); }
      if (sortKey === "fees_pending") { av = a.fees_pending ?? 0;    bv = b.fees_pending ?? 0; }
      if (av < bv) return sortDir === "asc" ? -1 :  1;
      if (av > bv) return sortDir === "asc" ?  1 : -1;
      return 0;
    });
    return list;
  }, [visits, sortKey, sortDir]);

  return (
    <div>
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 tracking-tight">Visits</h1>
          <p className="mt-1 text-slate-500">All patient visits across the portal.</p>
        </div>
        <button
          onClick={() => navigate("/visits/add")}
          className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition"
        >
          <UserPlus size={16} />
          Add Visit
        </button>
      </div>

      {fetchError && (
        <div className="mb-4 bg-rose-50 border border-rose-200 rounded-xl px-4 py-3 text-sm text-rose-700">
          <p className="font-semibold">Could not load visits</p>
          <p className="font-mono text-xs mt-0.5">{fetchError}</p>
        </div>
      )}

      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-3 mb-5">
        <div className="relative flex-1 min-w-[200px]">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input type="text" placeholder="Search by visit ID, patient name or date…"
            value={query} onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2.5 text-sm border border-slate-200 rounded-xl
                       bg-white shadow-sm text-slate-700 placeholder-slate-400
                       focus:outline-none focus:ring-2 focus:ring-indigo-400
                       focus:border-transparent transition" />
        </div>

        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-xs text-slate-400 font-semibold flex items-center gap-1">
            <ArrowUpDown size={12} /> Sort:
          </span>
          <SortBtn sortKey="visit_date"   currentKey={sortKey} sortDir={sortDir} label="Date"         onClick={handleSort} />
          <SortBtn sortKey="patient_name" currentKey={sortKey} sortDir={sortDir} label="Patient"      onClick={handleSort} />
          <SortBtn sortKey="visit_id"     currentKey={sortKey} sortDir={sortDir} label="Visit ID"     onClick={handleSort} />
          <SortBtn sortKey="fees_pending" currentKey={sortKey} sortDir={sortDir} label="Fees Pending" onClick={handleSort} />
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wide">
              <tr>
                <th className="px-5 py-3 font-semibold">Visit ID</th>
                <th className="px-5 py-3 font-semibold">Patient Name</th>
                <th className="px-5 py-3 font-semibold">Visit Date</th>
                <th className="px-5 py-3 font-semibold">Fees Pending</th>
                <th className="px-5 py-3 font-semibold">Follow-up Date</th>
                <th className="px-5 py-3 font-semibold">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-5 py-12 text-center">
                    <Loader2 size={20} className="animate-spin text-indigo-400 mx-auto" />
                    <p className="text-sm text-slate-400 mt-2">Loading visits…</p>
                  </td>
                </tr>
              ) : displayed.length > 0 ? (
                displayed.map((v) => {
                  const hasPending = (v.fees_pending ?? 0) > 0;
                  return (
                    <tr key={v.visit_id} className="hover:bg-slate-50 transition-colors duration-100">
                      <td className="px-5 py-3.5 font-mono text-slate-500 text-xs">#{v.visit_id}</td>

                      {/* Patient name — clickable */}
                      <td className="px-5 py-3.5">
                        <button
                          onClick={() => setModal({ type: "patientPreview", patientId: v.patient_id })}
                          className="font-medium text-indigo-600 hover:text-indigo-800 hover:underline
                                     transition text-left"
                        >
                          {v.patient_name}
                        </button>
                        <p className="text-xs text-slate-400 font-mono">{v.patient_id}</p>
                      </td>

                      <td className="px-5 py-3.5 text-slate-600">{v.visit_date || "—"}</td>

                      {/* Fees pending badge */}
                      <td className="px-5 py-3.5">
                        {hasPending ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full
                                           text-xs font-semibold bg-amber-100 text-amber-700">
                            Yes · ₹{v.fees_pending.toFixed(2)}
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full
                                           text-xs font-semibold bg-green-100 text-green-700">
                            No
                          </span>
                        )}
                      </td>

                      <td className="px-5 py-3.5 text-slate-600">
                        {v.follow_up_date || (
                          <span className="text-slate-400">None</span>
                        )}
                      </td>

                      <td className="px-5 py-3.5">
                        <button onClick={() => setModal({ type: "view", visit: v })}
                          className="flex items-center gap-1.5 text-xs font-semibold
                                     text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50
                                     px-2.5 py-1.5 rounded-lg transition-colors">
                          <Eye size={13} /> View
                        </button>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={6} className="px-5 py-12 text-center text-slate-400 text-sm">
                    {query ? "No visits match your search." : "No visits found."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="px-5 py-3 border-t border-slate-100 bg-slate-50 text-xs text-slate-500
                        flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <span>Page {page + 1} · Showing {displayed.length} of up to {PAGE_SIZE} visits</span>
          <div className="flex items-center gap-2">
            <button onClick={() => setPage((p) => Math.max(0, p - 1))} disabled={page === 0}
              className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-600
                         font-semibold hover:border-indigo-300 disabled:opacity-50
                         disabled:cursor-not-allowed transition">
              Previous
            </button>
            <button onClick={() => setPage((p) => p + 1)}
              disabled={(visits || []).length < PAGE_SIZE}
              className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-600
                         font-semibold hover:border-indigo-300 disabled:opacity-50
                         disabled:cursor-not-allowed transition">
              Next
            </button>
          </div>
        </div>
      </div>

      {/* ── Modals ── */}

      {modal?.type === "view" && (
        <VisitDetailsModal
          visit={modal.visit}
          onClose={() => setModal(null)}
          onEdit={(v) => setModal({ type: "edit", visit: v })}
          onDelete={handleDeleteVisit}
          onPatientClick={(pid) => setModal({ type: "patientPreview", patientId: pid })}
        />
      )}

      {modal?.type === "edit" && (
        <VisitEditModal
          visit={modal.visit}
          onSave={handleUpdateVisit}
          onClose={() => setModal(null)}
        />
      )}

      {modal?.type === "patientPreview" && (
        <PatientPreviewModal
          patientId={modal.patientId}
          fetchPatientDetails={fetchPatientDetails}
          onClose={() => setModal(null)}
        />
      )}
    </div>
  );
}