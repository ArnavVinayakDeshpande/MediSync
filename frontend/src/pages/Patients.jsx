// src/pages/Patients.jsx

import { useState, useMemo, useRef, useEffect } from "react";
import {
  Search, UserPlus, Eye, Pencil, Trash2, X, AlertCircle,
  ArrowUpDown, Filter, ChevronDown, ArrowUp, ArrowDown, Loader2,
  History,
} from "lucide-react";
import { useData } from "../context/DataContext";

// ─── Constants ────────────────────────────────────────────────────────────────

const CONDITIONS = [
  "Normal Pregnancy", "High Risk Pregnancy", "Gestatational Diabetes",
  "Gestatational Hypertension", "Preeclamsia", "Placenta Previa",
  "Preterm Labour", "Multiple Pregnancy", "Intrauterine Growth Restriction",
  "Post Term Pregnancy", "HyperMesis Gravidarum", "PCOS", "Endometriosis",
  "Uterine Fibroids", "Adenomyosis", "Ovarian Cyst", "Menstrual Disorder",
  "Amenorrhea", "Dysmenorrhea", "Abnormal Uterine Bleeding",
  "Pelvic Inflammatory Disease", "Vaginitis", "Cervicitis", "Infertility",
  "Menopausal Symptoms", "None",
];

const PREGNANCY_CONDITIONS = new Set([
  "Normal Pregnancy", "High Risk Pregnancy", "Gestatational Diabetes",
  "Gestatational Hypertension", "Preeclamsia", "Placenta Previa",
  "Preterm Labour", "Multiple Pregnancy", "Intrauterine Growth Restriction",
  "Post Term Pregnancy", "HyperMesis Gravidarum",
]);

const PAGE_SIZE = 50;

// ─── Helpers ──────────────────────────────────────────────────────────────────

// Backend returns DD-MM-YYYY; display as DD/MM/YYYY
function fmtDOB(str) {
  if (!str) return "—";
  return str.replace(/-/g, "/");  // "15-07-2025" → "15/07/2025"
}

// <input type="date"> value (YYYY-MM-DD) → backend format (DD-MM-YYYY)
function toDDMMYYYY(isoDate) {
  if (!isoDate) return "";
  const parts = isoDate.split("-");
  if (parts.length !== 3) return isoDate;
  const [y, m, d] = parts;
  return `${d}-${m}-${y}`;
}

// Backend format (DD-MM-YYYY) → <input type="date"> value (YYYY-MM-DD)
function toYYYYMMDD(backendDate) {
  if (!backendDate) return "";
  const parts = backendDate.split("-");
  if (parts.length !== 3) return "";
  const [d, m, y] = parts;
  const fullYear = y.length === 2 ? `20${y}` : y;
  return `${fullYear}-${m}-${d}`;
}

// Parse DD-MM-YY or DD-MM-YYYY → timestamp for sorting
function visitDateTs(str) {
  if (!str) return 0;
  const parts = str.split("-");
  if (parts.length < 3) return 0;
  const [d, m, y] = parts;
  const year = y.length <= 2 ? 2000 + parseInt(y, 10) : parseInt(y, 10);
  return new Date(year, parseInt(m, 10) - 1, parseInt(d, 10)).getTime();
}

// ─── Badges ───────────────────────────────────────────────────────────────────

function ActiveBadge({ active }) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold
      ${active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-600"}`}>
      {active ? "Active" : "Inactive"}
    </span>
  );
}

function ConditionBadge({ condition }) {
  const isPregnancy = PREGNANCY_CONDITIONS.has(condition);
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold
      ${isPregnancy ? "bg-rose-100 text-rose-700" : "bg-slate-100 text-slate-600"}`}>
      {condition || "—"}
    </span>
  );
}

// ─── Field wrapper ─────────────────────────────────────────────────────────────

function Field({ label, required, error, hint, children }) {
  return (
    <div>
      <label className="block text-xs font-semibold text-slate-600 mb-1">
        {label}
        {required && <span className="text-rose-500 ml-0.5">*</span>}
        {hint   && <span className="ml-1 text-slate-400 font-normal">{hint}</span>}
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

// ─────────────────────────────────────────────────────────────────────────────
//  Patient Form  (Add & Edit)
// ─────────────────────────────────────────────────────────────────────────────

const EMPTY_FORM = {
  id: "", name: "", dob: "", number: "", condition: "", is_active: "",
};

function PatientForm({ title, initial, isEdit, idIsGenerated, patients, onSave, onClose }) {
  const [form,        setForm]        = useState({ ...initial });
  const [errors,      setErrors]      = useState({});
  const [saving,      setSaving]      = useState(false);
  const [serverError, setServerError] = useState(null);

  const set = (key, val) => {
    setForm((p) => ({ ...p, [key]: val }));
    setErrors((p) => ({ ...p, [key]: "" }));
  };

  const validate = () => {
    const e = {};
    if (!isEdit && !idIsGenerated && form.id.trim() !== "") {
      if (!/^\d{6}$/.test(form.id.trim())) e.id = "Must be exactly 6 digits.";
      else if (patients.some((p) => p.id === form.id.trim())) e.id = "This ID already exists.";
    }
    if (!form.name.trim())   e.name   = "Name is required.";
    if (!form.number.trim()) e.number = "Contact number is required.";
    else if (!/^\d{10}$/.test(form.number.trim())) e.number = "Must be 10 digits.";
    if (form.is_active === "") e.is_active = "Please select a status.";
    return e;
  };

  const handleSubmit = async () => {
    const e = validate();
    if (Object.keys(e).length > 0) { setErrors(e); return; }
    setSaving(true);
    setServerError(null);
    try {
      await onSave({
        ...form,
        // Convert YYYY-MM-DD (date input) → DD-MM-YYYY expected by patient_from_json_fmt
        dob: toDDMMYYYY(form.dob),
        is_active: form.is_active === "true" || form.is_active === true,
      });
    } catch (err) {
      setServerError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const idLocked = isEdit || idIsGenerated;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4 py-6 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg my-auto">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <h2 className="text-base font-bold text-slate-800">{title}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition">
            <X size={18} />
          </button>
        </div>

        <div className="px-6 py-5 space-y-4 max-h-[70vh] overflow-y-auto">
          {serverError && (
            <div className="bg-rose-50 border border-rose-200 rounded-xl px-4 py-3 text-xs text-rose-700 font-medium">
              {serverError}
            </div>
          )}

          <Field label="Patient ID" error={errors.id}
            hint={idIsGenerated ? "(auto-generated)" : !isEdit ? "(auto-generated if blank)" : undefined}>
            <div className="relative">
              <input type="text" inputMode="numeric" maxLength={6}
                value={form.id}
                onChange={(e) => set("id", e.target.value.replace(/\D/g, "").slice(0, 6))}
                placeholder={idLocked ? "" : "6-digit number"}
                disabled={idLocked}
                className={`w-full px-3 py-2 text-sm border rounded-xl transition
                  focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent
                  ${idLocked ? "bg-slate-100 text-slate-500 border-slate-200 cursor-not-allowed font-mono"
                    : errors.id ? "border-rose-300 bg-rose-50 text-slate-700"
                    : "border-slate-200 bg-white text-slate-700"}`}
              />
              {idIsGenerated && (
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-bold
                                 bg-teal-100 text-teal-700 px-2 py-0.5 rounded-full">
                  Generated
                </span>
              )}
            </div>
          </Field>

          <div className="grid grid-cols-2 gap-3">
            <Field label="Name" required error={errors.name}>
              <input type="text" value={form.name} onChange={(e) => set("name", e.target.value)}
                placeholder="Full name"
                className={`w-full px-3 py-2 text-sm border rounded-xl transition
                  focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent
                  ${errors.name ? "border-rose-300 bg-rose-50" : "border-slate-200 bg-white text-slate-700"}`}
              />
            </Field>
            <Field label="Contact Number" required error={errors.number}>
              <input type="tel" value={form.number} inputMode="numeric"
                onChange={(e) => set("number", e.target.value.replace(/\D/g, "").slice(0, 10))}
                placeholder="10-digit number"
                className={`w-full px-3 py-2 text-sm border rounded-xl transition
                  focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent
                  ${errors.number ? "border-rose-300 bg-rose-50" : "border-slate-200 bg-white text-slate-700"}`}
              />
            </Field>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Field label="Date of Birth">
              <input type="date" value={form.dob} onChange={(e) => set("dob", e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white
                           text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-400
                           focus:border-transparent transition"
              />
            </Field>
            <Field label="Active Status" required error={errors.is_active}>
              <select value={form.is_active} onChange={(e) => set("is_active", e.target.value)}
                className={`w-full px-3 py-2 text-sm border rounded-xl bg-white text-slate-700
                  focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent transition
                  ${errors.is_active ? "border-rose-300 bg-rose-50" : "border-slate-200"}`}>
                <option value="">Select…</option>
                <option value="true">Active</option>
                <option value="false">Inactive</option>
              </select>
            </Field>
          </div>

          <Field label="Condition">
            <select value={form.condition} onChange={(e) => set("condition", e.target.value)}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl bg-white
                         text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-400
                         focus:border-transparent transition">
              <option value="">Select condition…</option>
              {CONDITIONS.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
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
            {isEdit ? "Save Changes" : "Add Patient"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
//  Visit History — used inside ViewDetailsModal
// ─────────────────────────────────────────────────────────────────────────────

// A single row label + value inside the expanded visit card
function VRow({ label, value }) {
  if (!value && value !== 0) return null;
  return (
    <div className="flex flex-col sm:flex-row sm:items-start gap-0.5 sm:gap-3">
      <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide sm:w-32 flex-shrink-0">
        {label}
      </span>
      <span className="text-sm text-slate-800 whitespace-pre-wrap">{value}</span>
    </div>
  );
}

// One visit entry — collapsed shows date + pending badge, expanded shows full details
function VisitCard({ visit }) {
  const [open, setOpen] = useState(false);
  const hasPending = visit.fees_pending > 0;

  return (
    <div className={`border rounded-xl overflow-hidden
      ${hasPending ? "border-amber-200" : "border-slate-200"}`}>

      {/* ── Clickable header ── */}
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className={`w-full flex items-center justify-between px-4 py-3 text-left
          transition-colors hover:bg-slate-50
          ${open ? "bg-slate-50" : "bg-white"}`}
      >
        <div className="flex items-center gap-3 min-w-0">
          <span className="text-sm font-semibold text-slate-800 truncate">
            {visit.visit_date || "—"}
          </span>
          <span className="text-xs text-slate-400 font-mono">#{visit.visit_id}</span>
          {hasPending && (
            <span className="flex-shrink-0 text-[11px] font-bold bg-amber-100 text-amber-700
                             px-2 py-0.5 rounded-full">
              ₹{visit.fees_pending} pending
            </span>
          )}
          {visit.follow_up_date && (
            <span className="flex-shrink-0 text-[11px] font-medium bg-indigo-50 text-indigo-600
                             px-2 py-0.5 rounded-full">
              Follow-up: {visit.follow_up_date}
            </span>
          )}
        </div>
        <ChevronDown
          size={15}
          className={`text-slate-400 flex-shrink-0 ml-2 transition-transform duration-200
            ${open ? "rotate-180" : ""}`}
        />
      </button>

      {/* ── Expanded details ── */}
      {open && (
        <div className="px-4 py-4 border-t border-slate-100 bg-slate-50/60 space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-white border border-slate-200 rounded-lg px-3 py-2">
              <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wide">Fees Paid</p>
              <p className="text-base font-bold text-slate-800 mt-0.5">
                {visit.fees_paid != null ? `₹${visit.fees_paid.toFixed(2)}` : "—"}
              </p>
            </div>
            <div className={`border rounded-lg px-3 py-2
              ${hasPending ? "bg-amber-50 border-amber-200" : "bg-white border-slate-200"}`}>
              <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wide">Fees Pending</p>
              <p className={`text-base font-bold mt-0.5
                ${hasPending ? "text-amber-700" : "text-slate-800"}`}>
                {visit.fees_pending != null ? `₹${visit.fees_pending.toFixed(2)}` : "—"}
              </p>
            </div>
          </div>
          <VRow label="Diagnosis"    value={visit.diagnosis} />
          <VRow label="Prescription" value={visit.prescription} />
          <VRow label="Notes"        value={visit.notes} />
          <VRow label="Follow-up"    value={visit.follow_up_date || "None"} />
        </div>
      )}
    </div>
  );
}

// Visits section rendered at the bottom of ViewDetailsModal
function VisitsSection({ visits }) {
  const sorted = [...(visits || [])].sort(
    (a, b) => visitDateTs(b.visit_date) - visitDateTs(a.visit_date)
  );

  return (
    <div className="mt-6">
      {/* Section divider */}
      <div className="flex items-center gap-2 mb-3">
        <History size={15} className="text-indigo-500 flex-shrink-0" />
        <h3 className="text-sm font-bold text-slate-700">
          Visit History
          <span className="ml-2 text-xs font-normal text-slate-400">
            {sorted.length} {sorted.length === 1 ? "visit" : "visits"}
          </span>
        </h3>
      </div>

      {sorted.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-8 border-2 border-dashed
                        border-slate-200 rounded-xl text-slate-400">
          <p className="text-sm">No visits recorded yet.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {sorted.map((v) => (
            <VisitCard key={v.visit_id} visit={v} />
          ))}
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
//  View Details Modal
// ─────────────────────────────────────────────────────────────────────────────

function DetailRow({ label, value }) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-start gap-1 py-2.5
                    border-b border-slate-100 last:border-0">
      <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide
                       sm:w-44 flex-shrink-0">{label}</span>
      <span className="text-sm text-slate-800">{value ?? "—"}</span>
    </div>
  );
}

function ViewDetailsModal({ patientId, onClose, onEdit, onDelete, fetchPatientDetails }) {
  const [details,       setDetails]       = useState(null);
  const [loadingDet,    setLoadingDet]    = useState(true);
  const [fetchError,    setFetchError]    = useState(null);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [deleting,      setDeleting]      = useState(false);

  // useRef prevents double-fetch in React StrictMode
  const fetched = useRef(false);
  useEffect(() => {
    if (fetched.current) return;
    fetched.current = true;
    fetchPatientDetails(patientId)
      .then(setDetails)
      .catch((err) => setFetchError(err.message))
      .finally(() => setLoadingDet(false));
  }, [patientId, fetchPatientDetails]);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await onDelete(patientId);
    } catch (err) {
      setDeleting(false);
      setConfirmDelete(false);
      alert(`Delete failed: ${err.message}`);
    }
  };

  const md = details?.metadata;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4 py-6 overflow-y-auto">
      {/* ↓ max-w-2xl makes the modal wider; max-h-[80vh] gives more room for visits */}
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl my-auto">

        {/* Header */}
        <div className="flex items-start justify-between px-6 py-4 border-b border-slate-100">
          <div>
            <h2 className="text-base font-bold text-slate-800">{md?.name ?? "Loading…"}</h2>
            <p className="text-xs text-slate-400 font-mono mt-0.5">ID: {patientId}</p>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0 ml-4">
            {details && (
              <>
                <button onClick={() => onEdit(details)}
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
              </>
            )}
            <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition ml-1">
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="px-6 py-4 max-h-[72vh] overflow-y-auto">
          {loadingDet ? (
            <div className="flex items-center gap-2 text-slate-400 py-10 justify-center">
              <Loader2 size={16} className="animate-spin" /> Loading details…
            </div>
          ) : fetchError ? (
            <div className="bg-rose-50 border border-rose-100 rounded-xl px-4 py-3 text-sm text-rose-600">
              {fetchError}
            </div>
          ) : details ? (
            <>
              {/* ── Patient metadata ── */}
              <DetailRow label="Patient ID"     value={md?.id} />
              <DetailRow label="Name"           value={md?.name} />
              <DetailRow label="Date of Birth"  value={fmtDOB(md?.dob)} />
              <DetailRow label="Contact Number" value={md?.number} />
              <DetailRow label="Condition"      value={md?.condition || "—"} />
              <DetailRow
                label="Active Status"
                value={
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full
                                    text-xs font-semibold
                    ${md?.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-600"}`}>
                    {md?.is_active ? "Active" : "Inactive"}
                  </span>
                }
              />

              {/* ── Visit history ── */}
              <VisitsSection visits={details.visits} />
            </>
          ) : (
            <p className="text-sm text-slate-400 py-8 text-center">
              Could not load patient details.
            </p>
          )}
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

function SortButton({ sortKey, sortDir, currentKey, label, onClick }) {
  const active = currentKey === sortKey;
  return (
    <button onClick={() => onClick(sortKey)}
      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold
        border transition whitespace-nowrap
        ${active
          ? "bg-indigo-600 text-white border-indigo-600"
          : "bg-white text-slate-600 border-slate-200 hover:border-indigo-300 hover:text-indigo-600"}`}>
      {active
        ? (sortDir === "asc" ? <ArrowUp size={12} /> : <ArrowDown size={12} />)
        : <ArrowUpDown size={12} className="text-slate-400" />}
      {label}
    </button>
  );
}

// ─── Filter Dropdown ──────────────────────────────────────────────────────────

function FilterDropdown({
  filterActive, setFilterActive,
  filterCondition, setFilterCondition,
  filterAge, setFilterAge,
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const activeCount =
    (filterActive    !== null ? 1 : 0) +
    (filterCondition !== null ? 1 : 0) +
    (filterAge       !== null ? 1 : 0);

  const clearAll = () => {
    setFilterActive(null);
    setFilterCondition(null);
    setFilterAge(null);
  };

  return (
    <div className="relative" ref={ref}>
      <button onClick={() => setOpen((o) => !o)}
        className={`flex items-center gap-2 px-3 py-2.5 text-sm font-semibold
          border rounded-xl transition whitespace-nowrap
          ${activeCount > 0
            ? "bg-indigo-600 text-white border-indigo-600"
            : "bg-white text-slate-600 border-slate-200 hover:border-indigo-300"}`}>
        <Filter size={14} />
        Filter
        {activeCount > 0 && (
          <span className="bg-white/30 text-white text-xs font-bold px-1.5 py-0.5 rounded-full">
            {activeCount}
          </span>
        )}
        <ChevronDown size={13} className={`transition-transform ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-1 z-20 bg-white border border-slate-200
                        rounded-xl shadow-lg p-4 w-60 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-700">Filters</span>
            {activeCount > 0 && (
              <button onClick={clearAll}
                className="text-xs text-indigo-600 hover:text-indigo-800 font-semibold">
                Clear all
              </button>
            )}
          </div>

          <div>
            <p className="text-xs font-semibold text-slate-500 mb-1.5">Status</p>
            <div className="flex gap-2">
              {[[null, "All"], [true, "Active"], [false, "Inactive"]].map(([val, lbl]) => (
                <button key={String(val)} onClick={() => setFilterActive(val)}
                  className={`flex-1 py-1.5 rounded-lg text-xs font-semibold border transition
                    ${filterActive === val
                      ? "bg-indigo-600 text-white border-indigo-600"
                      : "bg-white text-slate-600 border-slate-200 hover:border-indigo-300"}`}>
                  {lbl}
                </button>
              ))}
            </div>
          </div>

          <div>
            <p className="text-xs font-semibold text-slate-500 mb-1.5">Condition</p>
            <select
              value={filterCondition ?? ""}
              onChange={(e) => setFilterCondition(e.target.value || null)}
              className="w-full px-2 py-2 text-xs border border-slate-200 rounded-lg bg-white
                         text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-400
                         focus:border-transparent transition">
              <option value="">All conditions</option>
              {CONDITIONS.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>

          <div>
            <p className="text-xs font-semibold text-slate-500 mb-1.5">Age</p>
            <input
              type="number" min="0" max="120"
              value={filterAge ?? ""}
              onChange={(e) => setFilterAge(e.target.value === "" ? null : Number(e.target.value))}
              placeholder="Any age"
              className="w-full px-2 py-2 text-xs border border-slate-200 rounded-lg bg-white
                         text-slate-700 placeholder-slate-400 focus:outline-none
                         focus:ring-2 focus:ring-indigo-400 focus:border-transparent transition"
            />
          </div>
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
//  Page
// ─────────────────────────────────────────────────────────────────────────────

export default function Patients() {
  const {
    patients, loading, error,
    refreshPatients,
    generatePatientId,
    addPatient, updatePatient, deletePatient, fetchPatientDetails,
  } = useData();

  const [query,           setQuery]           = useState("");
  const [sortKey,         setSortKey]         = useState("name");
  const [sortDir,         setSortDir]         = useState("asc");
  const [filterActive,    setFilterActive]    = useState(null);
  const [filterCondition, setFilterCondition] = useState(null);
  const [filterAge,       setFilterAge]       = useState(null);
  const [page,            setPage]            = useState(0);
  const [modal,           setModal]           = useState(null);
  const [idFetching,      setIdFetching]      = useState(false);
  const [idFetchError,    setIdFetchError]    = useState(null);

  const handleSort = (key) => {
    if (sortKey === key) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else { setSortKey(key); setSortDir("asc"); }
  };

  const activeFilterCount =
    (filterActive    !== null ? 1 : 0) +
    (filterCondition !== null ? 1 : 0) +
    (filterAge       !== null ? 1 : 0);

  useEffect(() => {
    refreshPatients({
      size:      PAGE_SIZE,
      offset:    page * PAGE_SIZE,
      condition: filterCondition,
      active:    filterActive,
      age:       filterAge,
    });
  }, [refreshPatients, page, filterCondition, filterActive, filterAge]);

  const updateFilterActive    = (v) => { setFilterActive(v);    setPage(0); };
  const updateFilterCondition = (v) => { setFilterCondition(v); setPage(0); };
  const updateFilterAge       = (v) => { setFilterAge(v);       setPage(0); };

  const displayed = useMemo(() => {
    let list = [...(patients || [])];
    if (query.trim()) {
      const q = query.toLowerCase();
      list = list.filter((p) =>
        p.name.toLowerCase().includes(q) ||
        p.id.includes(q) ||
        (p.number || "").includes(q)
      );
    }
    list.sort((a, b) => {
      let av, bv;
      if (sortKey === "name") { av = a.name.toLowerCase();    bv = b.name.toLowerCase(); }
      if (sortKey === "id")   { av = parseInt(a.id, 10) || 0; bv = parseInt(b.id, 10) || 0; }
      if (sortKey === "dob")  { av = visitDateTs(a.dob);      bv = visitDateTs(b.dob); }
      if (av < bv) return sortDir === "asc" ? -1 :  1;
      if (av > bv) return sortDir === "asc" ?  1 : -1;
      return 0;
    });
    return list;
  }, [patients, query, sortKey, sortDir]);

  const openAddModal = async () => {
    setIdFetching(true);
    setIdFetchError(null);
    try {
      const generatedId = await generatePatientId();
      setModal({ type: "add", generatedId });
    } catch (err) {
      setIdFetchError("Could not generate a Patient ID. Try again.");
      console.error("generatePatientId failed:", err);
    } finally {
      setIdFetching(false);
    }
  };

  const handleAdd    = async (fd) => { await addPatient(fd);    setModal(null); };
  const handleEdit   = async (fd) => { await updatePatient(fd); setModal(null); };
  const handleDelete = async (id) => { await deletePatient(id); setModal(null); };

  const openEdit = (details) => {
    const md = details.metadata;
    setModal({
      type: "edit",
      initial: {
        id:        md.id,
        name:      md.name,
        // Convert DD-MM-YYYY (backend) → YYYY-MM-DD so the date input pre-fills
        dob:       toYYYYMMDD(md.dob),
        number:    md.number,
        condition: md.condition || "",
        is_active: String(md.is_active),
      },
    });
  };

  if (loading) {
    return (
      <div className="flex items-center gap-3 text-slate-400 py-16 justify-center">
        <Loader2 size={20} className="animate-spin" />
        <span className="text-sm">Loading patients…</span>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-slate-800 tracking-tight">Patients</h1>
        <p className="mt-1 text-slate-500">Manage all registered patients.</p>
      </div>

      {error && (
        <div className="mb-4 bg-rose-50 border border-rose-200 rounded-xl px-4 py-3 text-sm text-rose-700">
          <p className="font-semibold">Backend connection error</p>
          <p className="font-mono text-xs mt-0.5">{error}</p>
        </div>
      )}

      {idFetchError && (
        <div className="mb-4 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 text-sm
                        text-amber-700 flex items-start gap-2">
          <AlertCircle size={15} className="mt-0.5 flex-shrink-0" />
          <span>{idFetchError}</span>
        </div>
      )}

      {/* Toolbar */}
      <div className="flex flex-col gap-3 mb-5">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[200px]">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input type="text" placeholder="Search by name, ID or number…"
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
            <SortButton sortKey="name" currentKey={sortKey} sortDir={sortDir} label="Name"          onClick={handleSort} />
            <SortButton sortKey="id"   currentKey={sortKey} sortDir={sortDir} label="Patient ID"    onClick={handleSort} />
            <SortButton sortKey="dob"  currentKey={sortKey} sortDir={sortDir} label="Date of Birth" onClick={handleSort} />
          </div>

          <FilterDropdown
            filterActive={filterActive}       setFilterActive={updateFilterActive}
            filterCondition={filterCondition} setFilterCondition={updateFilterCondition}
            filterAge={filterAge}             setFilterAge={updateFilterAge}
          />

          <button onClick={openAddModal} disabled={idFetching}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700
                       disabled:bg-indigo-400 text-white text-sm font-semibold px-4 py-2.5
                       rounded-xl shadow-sm transition-colors whitespace-nowrap">
            {idFetching
              ? <><Loader2 size={15} className="animate-spin" /> Generating ID…</>
              : <><UserPlus size={15} /> Add Patient</>}
          </button>
        </div>

        {activeFilterCount > 0 && (
          <div className="flex flex-wrap gap-2">
            {filterActive !== null && (
              <span className="flex items-center gap-1.5 bg-green-50 text-green-700
                               text-xs font-semibold px-2.5 py-1 rounded-full">
                {filterActive ? "Active only" : "Inactive only"}
                <button onClick={() => updateFilterActive(null)} className="hover:text-green-900">
                  <X size={11} />
                </button>
              </span>
            )}
            {filterCondition !== null && (
              <span className="flex items-center gap-1.5 bg-rose-50 text-rose-700
                               text-xs font-semibold px-2.5 py-1 rounded-full">
                Condition: {filterCondition}
                <button onClick={() => updateFilterCondition(null)} className="hover:text-rose-900">
                  <X size={11} />
                </button>
              </span>
            )}
            {filterAge !== null && (
              <span className="flex items-center gap-1.5 bg-sky-50 text-sky-700
                               text-xs font-semibold px-2.5 py-1 rounded-full">
                Age: {filterAge}
                <button onClick={() => updateFilterAge(null)} className="hover:text-sky-900">
                  <X size={11} />
                </button>
              </span>
            )}
          </div>
        )}
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wide">
              <tr>
                <th className="px-5 py-3 font-semibold">Patient ID</th>
                <th className="px-5 py-3 font-semibold">Name</th>
                <th className="px-5 py-3 font-semibold">Contact</th>
                <th className="px-5 py-3 font-semibold">Date of Birth</th>
                <th className="px-5 py-3 font-semibold">Condition</th>
                <th className="px-5 py-3 font-semibold">Active</th>
                <th className="px-5 py-3 font-semibold">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {displayed.length > 0 ? (
                displayed.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-50 transition-colors duration-100">
                    <td className="px-5 py-3.5 font-mono text-slate-500 text-xs">{p.id}</td>
                    <td className="px-5 py-3.5 font-medium text-slate-800">{p.name}</td>
                    <td className="px-5 py-3.5 text-slate-600">{p.number || "—"}</td>
                    <td className="px-5 py-3.5 text-slate-600">{fmtDOB(p.dob)}</td>
                    <td className="px-5 py-3.5">
                      {p.condition ? <ConditionBadge condition={p.condition} /> : "—"}
                    </td>
                    <td className="px-5 py-3.5"><ActiveBadge active={p.is_active} /></td>
                    <td className="px-5 py-3.5">
                      <button
                        onClick={() => setModal({ type: "view", patientId: p.id })}
                        className="flex items-center gap-1.5 text-xs font-semibold text-indigo-600
                                   hover:text-indigo-800 hover:bg-indigo-50 px-2.5 py-1.5
                                   rounded-lg transition-colors">
                        <Eye size={13} /> View
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="px-5 py-12 text-center text-slate-400 text-sm">
                    {query || activeFilterCount > 0
                      ? "No patients match your search or filters."
                      : "No patients yet. Click 'Add Patient' to get started."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="px-5 py-3 border-t border-slate-100 bg-slate-50 text-xs text-slate-500
                        flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <span>Page {page + 1} · Showing {displayed.length} of up to {PAGE_SIZE} patients</span>
          <div className="flex items-center gap-2">
            <button onClick={() => setPage((p) => Math.max(0, p - 1))} disabled={page === 0}
              className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-600
                         font-semibold hover:border-indigo-300 disabled:opacity-50
                         disabled:cursor-not-allowed transition">
              Previous
            </button>
            <button onClick={() => setPage((p) => p + 1)}
              disabled={(patients || []).length < PAGE_SIZE}
              className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-600
                         font-semibold hover:border-indigo-300 disabled:opacity-50
                         disabled:cursor-not-allowed transition">
              Next
            </button>
          </div>
        </div>
      </div>

      {/* Modals */}
      {modal?.type === "add" && (
        <PatientForm title="Add New Patient"
          initial={{ ...EMPTY_FORM, id: modal.generatedId || "" }}
          isEdit={false} idIsGenerated={!!modal.generatedId}
          patients={patients || []} onSave={handleAdd} onClose={() => setModal(null)} />
      )}
      {modal?.type === "edit" && (
        <PatientForm title="Edit Patient" initial={modal.initial}
          isEdit={true} idIsGenerated={false}
          patients={patients || []} onSave={handleEdit} onClose={() => setModal(null)} />
      )}
      {modal?.type === "view" && (
        <ViewDetailsModal
          patientId={modal.patientId}
          fetchPatientDetails={fetchPatientDetails}
          onClose={() => setModal(null)}
          onEdit={(details) => { setModal(null); openEdit(details); }}
          onDelete={handleDelete}
        />
      )}
    </div>
  );
}