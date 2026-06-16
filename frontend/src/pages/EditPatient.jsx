// src/pages/EditPatient.jsx

import { useState, useEffect, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { AlertCircle, Loader2, ArrowLeft } from "lucide-react";
import { useData } from "../context/DataContext";

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

function toDDMMYYYY(isoDate) {
  if (!isoDate) return "";
  const parts = isoDate.split("-");
  if (parts.length !== 3) return isoDate;
  const [y, m, d] = parts;
  return `${d}-${m}-${y}`;
}

function toYYYYMMDD(backendDate) {
  if (!backendDate) return "";
  const parts = backendDate.split("-");
  if (parts.length !== 3) return "";
  const [d, m, y] = parts;
  const fullYear = y.length === 2 ? `20${y}` : y;
  return `${fullYear}-${m}-${d}`;
}

function Field({ label, required, error, hint, children }) {
  return (
    <div>
      <label className="block text-xs font-semibold text-slate-600 mb-1">
        {label}
        {required && <span className="text-rose-500 ml-0.5">*</span>}
        {hint && <span className="ml-1 text-slate-400 font-normal">{hint}</span>}
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

export default function EditPatient() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { getPatient, updatePatient } = useData();

  const [loadingData, setLoadingData] = useState(true);
  const [loadError,   setLoadError]   = useState(null);
  const [form, setForm] = useState({
    id: "", name: "", dob: "", number: "", condition: "", is_active: "",
  });
  const [errors,      setErrors]      = useState({});
  const [saving,      setSaving]      = useState(false);
  const [serverError, setServerError] = useState(null);

  const fetched = useRef(false);
  useEffect(() => {
    if (fetched.current) return;
    fetched.current = true;
    (async () => {
      try {
        const patient = await getPatient(id);
        setForm({
          id:        patient.id,
          name:      patient.name,
          dob:       toYYYYMMDD(patient.dob),
          number:    patient.number,
          condition: patient.condition || "",
          is_active: String(patient.is_active),
        });
      } catch (err) {
        setLoadError(err.message);
      } finally {
        setLoadingData(false);
      }
    })();
  }, [id, getPatient]);

  const set = (key, val) => {
    setForm((p) => ({ ...p, [key]: val }));
    setErrors((p) => ({ ...p, [key]: "" }));
  };

  const validate = () => {
    const e = {};
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
      await updatePatient({
        ...form,
        dob: toDDMMYYYY(form.dob),
        is_active: form.is_active === "true" || form.is_active === true,
      });
      navigate(`/patients/${id}`);
    } catch (err) {
      setServerError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loadingData) {
    return (
      <div className="flex items-center gap-3 text-slate-400 py-16 justify-center">
        <Loader2 size={20} className="animate-spin" />
        <span className="text-sm">Loading patient…</span>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="max-w-lg mx-auto">
        <button onClick={() => navigate("/patients")}
          className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-indigo-600
                     font-semibold mb-4 transition">
          <ArrowLeft size={15} /> Back to Patients
        </button>
        <div className="bg-rose-50 border border-rose-200 rounded-xl px-4 py-3 text-sm text-rose-700">
          {loadError}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto">
      <button onClick={() => navigate(`/patients/${id}`)}
        className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-indigo-600
                   font-semibold mb-4 transition">
        <ArrowLeft size={15} /> Back to Details
      </button>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-100">
        <div className="px-6 py-4 border-b border-slate-100">
          <h1 className="text-lg font-bold text-slate-800">Edit Patient</h1>
          <p className="text-xs text-slate-400 font-mono mt-0.5">ID: {id}</p>
        </div>

        <div className="px-6 py-5 space-y-4">
          {serverError && (
            <div className="bg-rose-50 border border-rose-200 rounded-xl px-4 py-3 text-xs text-rose-700 font-medium">
              {serverError}
            </div>
          )}

          <Field label="Patient ID" hint="(cannot change)">
            <input type="text" value={form.id} disabled
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-xl
                         bg-slate-100 text-slate-500 cursor-not-allowed font-mono" />
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
                           focus:border-transparent transition" />
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
          <button onClick={() => navigate(`/patients/${id}`)} disabled={saving}
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
