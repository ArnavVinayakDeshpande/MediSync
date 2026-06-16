// src/pages/AddPatient.jsx

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
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

export default function AddPatient() {
  const navigate = useNavigate();
  const { generatePatientId, addPatient, patients } = useData();

  const [generatedId, setGeneratedId] = useState("");
  const [idFetching,  setIdFetching]  = useState(true);
  const [form, setForm] = useState({
    id: "", name: "", dob: "", number: "", condition: "", is_active: "",
  });
  const [errors,      setErrors]      = useState({});
  const [saving,      setSaving]      = useState(false);
  const [serverError, setServerError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const id = await generatePatientId();
        if (!cancelled) {
          setGeneratedId(id);
          setForm((p) => ({ ...p, id }));
        }
      } catch (err) {
        console.error("generatePatientId failed:", err);
      } finally {
        if (!cancelled) setIdFetching(false);
      }
    })();
    return () => { cancelled = true; };
  }, [generatePatientId]);

  const set = (key, val) => {
    setForm((p) => ({ ...p, [key]: val }));
    setErrors((p) => ({ ...p, [key]: "" }));
  };

  const idIsGenerated = !!generatedId;

  const validate = () => {
    const e = {};
    if (!idIsGenerated && form.id.trim() !== "") {
      if (!/^\d{6}$/.test(form.id.trim())) e.id = "Must be exactly 6 digits.";
      else if ((patients || []).some((p) => p.id === form.id.trim()))
        e.id = "This ID already exists.";
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
      await addPatient({
        ...form,
        dob: toDDMMYYYY(form.dob),
        is_active: form.is_active === "true" || form.is_active === true,
      });
      navigate("/patients");
    } catch (err) {
      setServerError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-lg mx-auto">
      <button onClick={() => navigate("/patients")}
        className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-indigo-600
                   font-semibold mb-4 transition">
        <ArrowLeft size={15} /> Back to Patients
      </button>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-100">
        <div className="px-6 py-4 border-b border-slate-100">
          <h1 className="text-lg font-bold text-slate-800">Add New Patient</h1>
        </div>

        <div className="px-6 py-5 space-y-4">
          {serverError && (
            <div className="bg-rose-50 border border-rose-200 rounded-xl px-4 py-3 text-xs text-rose-700 font-medium">
              {serverError}
            </div>
          )}

          <Field label="Patient ID" error={errors.id}
            hint={idIsGenerated ? "(auto-generated)" : "(auto-generated if blank)"}>
            <div className="relative">
              {idFetching ? (
                <div className="flex items-center gap-2 px-3 py-2 text-sm border border-slate-200
                                rounded-xl bg-slate-50 text-slate-400">
                  <Loader2 size={13} className="animate-spin" /> Generating…
                </div>
              ) : (
                <input type="text" inputMode="numeric" maxLength={6}
                  value={form.id}
                  onChange={(e) => set("id", e.target.value.replace(/\D/g, "").slice(0, 6))}
                  placeholder={idIsGenerated ? "" : "6-digit number"}
                  disabled={idIsGenerated}
                  className={`w-full px-3 py-2 text-sm border rounded-xl transition
                    focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent
                    ${idIsGenerated
                      ? "bg-slate-100 text-slate-500 border-slate-200 cursor-not-allowed font-mono"
                      : errors.id ? "border-rose-300 bg-rose-50 text-slate-700"
                      : "border-slate-200 bg-white text-slate-700"}`}
                />
              )}
              {idIsGenerated && !idFetching && (
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
          <button onClick={() => navigate("/patients")} disabled={saving}
            className="px-4 py-2 text-sm font-semibold text-slate-600 border border-slate-200
                       rounded-xl hover:bg-slate-50 transition disabled:opacity-50">
            Cancel
          </button>
          <button onClick={handleSubmit} disabled={saving}
            className="flex items-center gap-2 px-5 py-2 text-sm font-semibold text-white
                       bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow-sm transition disabled:opacity-50">
            {saving && <Loader2 size={13} className="animate-spin" />}
            Add Patient
          </button>
        </div>
      </div>
    </div>
  );
}
