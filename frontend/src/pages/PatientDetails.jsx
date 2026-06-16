// src/pages/PatientDetails.jsx

import { useState, useEffect, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  Pencil, Trash2, Loader2, ArrowLeft, ChevronDown, History,
} from "lucide-react";
import { useData } from "../context/DataContext";

// ─── Constants ────────────────────────────────────────────────────────────────

const PREGNANCY_CONDITIONS = new Set([
  "Normal Pregnancy", "High Risk Pregnancy", "Gestatational Diabetes",
  "Gestatational Hypertension", "Preeclamsia", "Placenta Previa",
  "Preterm Labour", "Multiple Pregnancy", "Intrauterine Growth Restriction",
  "Post Term Pregnancy", "HyperMesis Gravidarum",
]);

// ─── Helpers ──────────────────────────────────────────────────────────────────

function fmtDOB(str) {
  if (!str) return "—";
  return str.replace(/-/g, "/");
}

function visitDateTs(str) {
  if (!str) return 0;
  const parts = str.split("-");
  if (parts.length < 3) return 0;
  const [d, m, y] = parts;
  const year = y.length <= 2 ? 2000 + parseInt(y, 10) : parseInt(y, 10);
  return new Date(year, parseInt(m, 10) - 1, parseInt(d, 10)).getTime();
}

// ─── Small components ─────────────────────────────────────────────────────────

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

function ConditionBadge({ condition }) {
  const isPregnancy = PREGNANCY_CONDITIONS.has(condition);
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold
      ${isPregnancy ? "bg-rose-100 text-rose-700" : "bg-slate-100 text-slate-600"}`}>
      {condition || "—"}
    </span>
  );
}

// ─── Visit history ────────────────────────────────────────────────────────────

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

function VisitCard({ visit }) {
  const [open, setOpen] = useState(false);
  const hasPending = visit.fees_pending > 0;

  return (
    <div className={`border rounded-xl overflow-hidden
      ${hasPending ? "border-amber-200" : "border-slate-200"}`}>
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

function VisitsSection({ visits }) {
  const sorted = [...(visits || [])].sort(
    (a, b) => visitDateTs(b.visit_date) - visitDateTs(a.visit_date)
  );

  return (
    <div className="mt-6">
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

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function PatientDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { fetchPatientDetails, deletePatient } = useData();

  const [details,       setDetails]       = useState(null);
  const [loading,       setLoading]       = useState(true);
  const [fetchError,    setFetchError]    = useState(null);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [deleting,      setDeleting]      = useState(false);

  const fetched = useRef(false);
  useEffect(() => {
    if (fetched.current) return;
    fetched.current = true;
    fetchPatientDetails(id)
      .then(setDetails)
      .catch((err) => setFetchError(err.message))
      .finally(() => setLoading(false));
  }, [id, fetchPatientDetails]);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await deletePatient(id);
      navigate("/patients");
    } catch (err) {
      setDeleting(false);
      setConfirmDelete(false);
      alert(`Delete failed: ${err.message}`);
    }
  };

  const md = details?.metadata;

  if (loading) {
    return (
      <div className="flex items-center gap-3 text-slate-400 py-16 justify-center">
        <Loader2 size={20} className="animate-spin" />
        <span className="text-sm">Loading patient details…</span>
      </div>
    );
  }

  if (fetchError) {
    return (
      <div className="max-w-2xl mx-auto">
        <button onClick={() => navigate("/patients")}
          className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-indigo-600
                     font-semibold mb-4 transition">
          <ArrowLeft size={15} /> Back to Patients
        </button>
        <div className="bg-rose-50 border border-rose-200 rounded-xl px-4 py-3 text-sm text-rose-700">
          {fetchError}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <button onClick={() => navigate("/patients")}
        className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-indigo-600
                   font-semibold mb-4 transition">
        <ArrowLeft size={15} /> Back to Patients
      </button>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-100">
        {/* Header */}
        <div className="flex items-start justify-between px-6 py-4 border-b border-slate-100">
          <div>
            <h1 className="text-lg font-bold text-slate-800">{md?.name ?? "—"}</h1>
            <p className="text-xs text-slate-400 font-mono mt-0.5">ID: {id}</p>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0 ml-4">
            <button onClick={() => navigate(`/patients/${id}/edit`)}
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
          </div>
        </div>

        {/* Body */}
        <div className="px-6 py-4">
          {details ? (
            <>
              <DetailRow label="Patient ID"     value={md?.id} />
              <DetailRow label="Name"           value={md?.name} />
              <DetailRow label="Date of Birth"  value={fmtDOB(md?.dob)} />
              <DetailRow label="Contact Number" value={md?.number} />
              <DetailRow label="Condition"
                value={md?.condition ? <ConditionBadge condition={md.condition} /> : "—"} />
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

              <VisitsSection visits={details.visits} />
            </>
          ) : (
            <p className="text-sm text-slate-400 py-8 text-center">
              Could not load patient details.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
