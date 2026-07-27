import {
  Activity,
  ArrowLeft,
  CalendarDays,
  ChevronDown,
  ChevronUp,
  ClipboardPlus,
  Dna,
  Edit3,
  Mail,
  Plus,
  Ruler,
  Scale,
  Stethoscope,
  Trash2,
  UserRound,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { apiRequest } from "../services/api";
import { useToast } from "../components/ToastProvider";
import {
  ConfirmDialog,
  Drawer,
  EmptyState,
  ErrorState,
  Field,
  PageLoader,
  RiskBadge,
  Spinner,
  SwitchField,
} from "../components/ui";
import { calculateAge, formatDate, formatPercent, initials } from "../utils/formatters";

const emptyAssessment = {
  weight_kg: "",
  cycle_regular: true,
  cycle_length: "",
  fsh_miu_ml: "",
  lh_miu_ml: "",
  amh_ng_ml: "",
  weight_gain: false,
  hair_growth: false,
  skin_darkening: false,
  hair_loss: false,
  pimples: false,
  fast_food: false,
  regular_exercise: false,
  follicle_left: "",
  follicle_right: "",
};

function EditPatientDrawer({ patient, open, onClose, onUpdated }) {
  const { showToast } = useToast();
  const [form, setForm] = useState(patient || {});
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (open && patient) setForm({
      first_name: patient.first_name,
      last_name: patient.last_name,
      email: patient.email || "",
      date_of_birth: patient.date_of_birth,
      height_cm: patient.height_cm,
    });
  }, [open, patient]);

  const update = (field, value) => setForm((current) => ({ ...current, [field]: value }));

  async function submit(event) {
    event.preventDefault();
    setSubmitting(true); setError("");
    try {
      const updated = await apiRequest(`/patients/${patient.patient_id}`, {
        method: "PATCH",
        body: JSON.stringify({
          ...form,
          email: form.email.trim() || null,
          height_cm: Number(form.height_cm),
        }),
      });
      showToast("Patient information updated.");
      onUpdated(updated);
    } catch (requestError) { setError(requestError.message); }
    finally { setSubmitting(false); }
  }

  return (
    <Drawer open={open} onClose={onClose} title="Edit patient information" description="Changes will be reflected throughout this patient record.">
      {error && <div className="form-notice error-notice" role="alert">{error}</div>}
      <form className="drawer-form" onSubmit={submit}>
        <div className="form-grid form-grid-two"><Field label="First name" required>{(props) => <input {...props} value={form.first_name || ""} onChange={(e) => update("first_name", e.target.value)} required />}</Field><Field label="Last name" required>{(props) => <input {...props} value={form.last_name || ""} onChange={(e) => update("last_name", e.target.value)} required />}</Field></div>
        <Field label="Email address" hint="Optional">{(props) => <input {...props} type="email" value={form.email || ""} onChange={(e) => update("email", e.target.value)} />}</Field>
        <Field label="Date of birth" required>{(props) => <input {...props} type="date" max={new Date().toISOString().slice(0, 10)} value={form.date_of_birth || ""} onChange={(e) => update("date_of_birth", e.target.value)} required />}</Field>
        <Field label="Height (cm)" hint="Allowed range: 80–250 cm" required>{(props) => <input {...props} type="number" min="80" max="250" step="0.1" value={form.height_cm || ""} onChange={(e) => update("height_cm", e.target.value)} required />}</Field>
        <div className="drawer-actions"><button className="button button-secondary" type="button" onClick={onClose}>Cancel</button><button className="button button-primary" disabled={submitting}>{submitting ? <Spinner label="Saving" /> : "Save changes"}</button></div>
      </form>
    </Drawer>
  );
}

function AssessmentDrawer({ patient, open, onClose, onCreated }) {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState(emptyAssessment);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (open) { setStep(1); setForm(emptyAssessment); setError(""); }
  }, [open]);

  const update = (field, value) => setForm((current) => ({ ...current, [field]: value }));

  function continueStep(event) {
    event.preventDefault();
    const formElement = event.currentTarget;
    if (formElement.reportValidity()) setStep((current) => Math.min(current + 1, 3));
  }

  async function submit(event) {
    event.preventDefault();
    setSubmitting(true); setError("");
    try {
      const numeric = ["weight_kg", "cycle_length", "fsh_miu_ml", "lh_miu_ml", "follicle_left", "follicle_right"];
      const payload = { ...form };
      numeric.forEach((field) => { payload[field] = Number(payload[field]); });
      payload.amh_ng_ml = payload.amh_ng_ml === "" ? null : Number(payload.amh_ng_ml);
      payload.doctor_notes = null;
      onCreated(await apiRequest(`/patients/${patient.patient_id}/assessments`, {
        method: "POST",
        body: JSON.stringify(payload),
      }));
    } catch (requestError) { setError(requestError.message); }
    finally { setSubmitting(false); }
  }

  return (
    <Drawer
      open={open}
      onClose={submitting ? () => {} : onClose}
      title={submitting ? "Evaluating clinical risk" : `New assessment for ${patient?.first_name || "patient"}`}
      description={submitting ? "The assessment is being processed securely." : "Complete the three clinical sections. Values use the ranges accepted by your prediction API."}
      wide
    >
      {submitting ? (
        <div className="risk-evaluation-panel" role="status" aria-live="polite">
          <div className="risk-evaluation-orbit" aria-hidden="true">
            <span className="risk-evaluation-icon"><Activity size={32} /></span>
          </div>
          <span className="eyebrow">Clinical model processing</span>
          <h3>Evaluating PCOS risk</h3>
          <p>Reviewing measurements, symptoms, lifestyle indicators, and ultrasound findings.</p>
          <div className="risk-evaluation-progress" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>
          <small>Please keep this panel open while the result is prepared.</small>
        </div>
      ) : (
        <>
          <div className="assessment-stepper" aria-label={`Assessment step ${step} of 3`}>
            {["Measurements", "Symptoms", "Ultrasound"].map((label, index) => <div key={label} className={index + 1 <= step ? "active" : ""}><span>{index + 1}</span><strong>{label}</strong></div>)}
          </div>
          {error && <div className="form-notice error-notice" role="alert">{error}</div>}

      {step === 1 && <form className="drawer-form" onSubmit={continueStep}>
        <section className="form-section"><div className="form-section-heading"><span><Scale size={19} /></span><div><h3>Measurements and cycle</h3><p>Enter values from the current consultation.</p></div></div>
          <div className="form-grid form-grid-two"><Field label="Weight (kg)" hint="20–300 kg" required>{(props) => <input {...props} type="number" min="20" max="300" step="0.1" value={form.weight_kg} onChange={(e) => update("weight_kg", e.target.value)} required />}</Field><Field label="Cycle length (days)" hint="15–120 days" required>{(props) => <input {...props} type="number" min="15" max="120" value={form.cycle_length} onChange={(e) => update("cycle_length", e.target.value)} required />}</Field></div>
          <SwitchField label="Regular menstrual cycle" hint={form.cycle_regular ? "Cycle recorded as regular" : "Cycle recorded as irregular"} checked={form.cycle_regular} onChange={(value) => update("cycle_regular", value)} />
          <div className="form-grid form-grid-three"><Field label="FSH (mIU/mL)" hint="0–200" required>{(props) => <input {...props} type="number" min="0" max="200" step="0.01" value={form.fsh_miu_ml} onChange={(e) => update("fsh_miu_ml", e.target.value)} required />}</Field><Field label="LH (mIU/mL)" hint="0–200" required>{(props) => <input {...props} type="number" min="0" max="200" step="0.01" value={form.lh_miu_ml} onChange={(e) => update("lh_miu_ml", e.target.value)} required />}</Field><Field label="AMH (ng/mL)" hint="Optional · 0–50">{(props) => <input {...props} type="number" min="0" max="50" step="0.01" value={form.amh_ng_ml} onChange={(e) => update("amh_ng_ml", e.target.value)} />}</Field></div>
        </section>
        <div className="drawer-actions"><button className="button button-secondary" type="button" onClick={onClose}>Cancel</button><button className="button button-primary">Continue</button></div>
      </form>}

      {step === 2 && <form className="drawer-form" onSubmit={continueStep}>
        <section className="form-section"><div className="form-section-heading"><span><Activity size={19} /></span><div><h3>Symptoms</h3><p>Turn on every symptom currently reported or observed.</p></div></div><div className="switch-grid"><SwitchField label="Recent weight gain" checked={form.weight_gain} onChange={(v) => update("weight_gain", v)} /><SwitchField label="Increased hair growth" checked={form.hair_growth} onChange={(v) => update("hair_growth", v)} /><SwitchField label="Skin darkening" checked={form.skin_darkening} onChange={(v) => update("skin_darkening", v)} /><SwitchField label="Hair loss" checked={form.hair_loss} onChange={(v) => update("hair_loss", v)} /><SwitchField label="Pimples / acne" checked={form.pimples} onChange={(v) => update("pimples", v)} /></div></section>
        <section className="form-section"><div className="form-section-heading"><span><Dna size={19} /></span><div><h3>Lifestyle</h3><p>Record current lifestyle indicators.</p></div></div><div className="switch-grid"><SwitchField label="Frequent fast food" checked={form.fast_food} onChange={(v) => update("fast_food", v)} /><SwitchField label="Regular exercise" checked={form.regular_exercise} onChange={(v) => update("regular_exercise", v)} /></div></section>
        <div className="drawer-actions"><button className="button button-secondary" type="button" onClick={() => setStep(1)}>Back</button><button className="button button-primary">Continue</button></div>
      </form>}

      {step === 3 && <form className="drawer-form" onSubmit={submit}>
        <section className="form-section"><div className="form-section-heading"><span><Stethoscope size={19} /></span><div><h3>Ultrasound findings</h3><p>Enter the follicle count for each ovary.</p></div></div><div className="form-grid form-grid-two"><Field label="Left follicle count" hint="0–50" required>{(props) => <input {...props} type="number" min="0" max="50" value={form.follicle_left} onChange={(e) => update("follicle_left", e.target.value)} required />}</Field><Field label="Right follicle count" hint="0–50" required>{(props) => <input {...props} type="number" min="0" max="50" value={form.follicle_right} onChange={(e) => update("follicle_right", e.target.value)} required />}</Field></div></section>
        <div className="clinical-warning"><strong>Clinical reminder</strong><p>The generated probability is decision support and should be interpreted with the full clinical picture.</p></div>
        <div className="drawer-actions"><button className="button button-secondary" type="button" onClick={() => setStep(2)}>Back</button><button className="button button-primary">Evaluate risk</button></div>
      </form>}
        </>
      )}
    </Drawer>
  );
}

function ResultDrawer({ patientId, result, open, onFinish }) {
  const [notes, setNotes] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (open) {
      setNotes(result?.doctor_notes || "");
      setError("");
      setSaving(false);
    }
  }, [open, result]);

  async function saveNotes() {
    setSaving(true);
    setError("");

    try {
      const updated = await apiRequest(`/patients/${patientId}/assessments/${result.assessment_id}`, {
        method: "PATCH",
        body: JSON.stringify({ doctor_notes: notes.trim() || null }),
      });
      showToast("Doctor notes saved.");
      onFinish(updated, true);
    } catch (requestError) {
      setError(requestError.message);
      setSaving(false);
    }
  }

  return (
    <Drawer
      open={open}
      onClose={saving ? () => {} : () => onFinish(result, false)}
      title="Risk evaluation complete"
      description="Review the result, add your clinical notes, then return to the assessment history."
    >
      {result && <div className={`result-summary ${result.prediction_class === "High Risk" ? "result-high" : "result-low"}`}><span className="result-icon"><Activity size={26} /></span><RiskBadge value={result.prediction_class} /><strong>{formatPercent(result.prediction_probability)}</strong><p>Predicted PCOS risk probability</p></div>}
      <div className="clinical-warning"><strong>Interpret in context</strong><p>This model output supports, but does not replace, clinical evaluation and diagnosis.</p></div>
      <section className="result-notes-panel">
        <div className="result-notes-heading">
          <span><ClipboardPlus size={19} /></span>
          <div>
            <h3>Add doctor notes</h3>
            <p>Record your clinical interpretation after reviewing the result.</p>
          </div>
        </div>
        {error && <div className="form-notice error-notice" role="alert">{error}</div>}
        <Field label="Clinical notes" hint={`${notes.length}/5,000 characters`}>
          {(props) => (
            <textarea
              {...props}
              rows="6"
              maxLength="5000"
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
              placeholder="Add clinical context, follow-up considerations, or observations..."
            />
          )}
        </Field>
      </section>
      <div className="result-actions">
        <button className="button button-secondary" type="button" onClick={() => onFinish(result, false)} disabled={saving}>Skip for now</button>
        <button className="button button-primary" type="button" onClick={saveNotes} disabled={saving || !notes.trim()}>
          {saving ? <Spinner label="Saving notes" /> : "Save notes & return"}
        </button>
      </div>
    </Drawer>
  );
}

function AssessmentItem({ assessment, onDelete }) {
  const [expanded, setExpanded] = useState(false);
  const symptoms = [
    ["Weight gain", assessment.weight_gain], ["Hair growth", assessment.hair_growth],
    ["Skin darkening", assessment.skin_darkening], ["Hair loss", assessment.hair_loss],
    ["Pimples", assessment.pimples], ["Frequent fast food", assessment.fast_food],
    ["Regular exercise", assessment.regular_exercise],
  ];
  return (
    <article className="assessment-item">
      <button className="assessment-summary" type="button" onClick={() => setExpanded((value) => !value)} aria-expanded={expanded}>
        <span className="assessment-date"><CalendarDays size={18} /><span><strong>{formatDate(assessment.assessment_date)}</strong><small>Assessment #{assessment.assessment_id}</small></span></span>
        <RiskBadge value={assessment.prediction_class} />
        <strong className="probability-value">{formatPercent(assessment.prediction_probability)}</strong>
        {expanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
      </button>
      {expanded && <div className="assessment-details">
        <dl className="details-grid"><div><dt>Weight</dt><dd>{assessment.weight_kg} kg</dd></div><div><dt>Cycle</dt><dd>{assessment.cycle_regular ? "Regular" : "Irregular"}, {assessment.cycle_length} days</dd></div><div><dt>FSH / LH</dt><dd>{assessment.fsh_miu_ml} / {assessment.lh_miu_ml}</dd></div><div><dt>FSH/LH ratio</dt><dd>{assessment.fsh_lh_ratio ?? "Not available"}</dd></div><div><dt>AMH</dt><dd>{assessment.amh_ng_ml ? `${assessment.amh_ng_ml} ng/mL` : "Not recorded"}</dd></div><div><dt>Follicles</dt><dd>{assessment.follicle_left} left · {assessment.follicle_right} right</dd></div></dl>
        <div className="symptom-tags">{symptoms.map(([label, value]) => <span className={value ? "active" : ""} key={label}>{label}: {value ? "Yes" : "No"}</span>)}</div>
        {assessment.doctor_notes && <div className="doctor-note"><strong>Doctor notes</strong><p>{assessment.doctor_notes}</p></div>}
        <div className="assessment-actions"><button className="button button-danger-subtle" type="button" onClick={() => onDelete(assessment)}><Trash2 size={16} /> Delete assessment</button></div>
      </div>}
    </article>
  );
}

export default function PatientProfilePage() {
  const { patientId } = useParams();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [patient, setPatient] = useState(null);
  const [assessments, setAssessments] = useState([]);
  const [activeTab, setActiveTab] = useState("overview");
  const [editOpen, setEditOpen] = useState(false);
  const [assessmentOpen, setAssessmentOpen] = useState(false);
  const [result, setResult] = useState(null);
  const [confirm, setConfirm] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const [patientData, assessmentData] = await Promise.all([apiRequest(`/patients/${patientId}`, { method: "GET" }), apiRequest(`/patients/${patientId}/assessments`, { method: "GET" })]);
      setPatient(patientData); setAssessments(assessmentData);
    } catch (requestError) { setError(requestError.message); }
    finally { setLoading(false); }
  }, [patientId]);

  useEffect(() => { load(); }, [load]);

  async function handleDelete() {
    setDeleting(true);
    try {
      if (confirm.type === "patient") {
        await apiRequest(`/patients/${patientId}`, { method: "DELETE" });
        showToast("Patient record deleted.", "info");
        navigate("/patients", { replace: true });
      } else {
        await apiRequest(`/patients/${patientId}/assessments/${confirm.id}`, { method: "DELETE" });
        setAssessments((current) => current.filter((item) => item.assessment_id !== confirm.id));
        showToast("Assessment deleted.", "info");
        setConfirm(null);
      }
    } catch (requestError) { showToast(requestError.message, "error"); }
    finally { setDeleting(false); }
  }
  
  // Sort assessments by assessment_date descending
  const sortedAssessments = useMemo(() => {
    return [...assessments].sort((a, b) => new Date(b.assessment_date) - new Date(a.assessment_date));
  }, [assessments]);
  const latest = sortedAssessments[0];
  const bmi = useMemo(() => latest && patient ? (Number(latest.weight_kg) / ((Number(patient.height_cm) / 100) ** 2)).toFixed(1) : null, [latest, patient]);

  if (loading) return <PageLoader label="Loading patient record" />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  return (
    <div className="page-stack">
      <Link className="back-link" to="/patients"><ArrowLeft size={17} /> Back to patients</Link>
      <header className="patient-profile-header">
        <div className="patient-identity"><span className="avatar avatar-large">{initials(patient.first_name, patient.last_name)}</span><div><div className="patient-title-line"><h1>{patient.first_name} {patient.last_name}</h1><RiskBadge value={latest?.prediction_class} /></div><p>Patient ID #{patient.patient_id} · {calculateAge(patient.date_of_birth)} years old</p></div></div>
        <div className="header-actions"><button className="button button-secondary" type="button" onClick={() => setEditOpen(true)}><Edit3 size={16} /> Edit</button><button className="button button-primary" type="button" onClick={() => setAssessmentOpen(true)}><Plus size={17} /> Add assessment</button></div>
      </header>

      <nav className="tab-bar" aria-label="Patient record sections"><button type="button" className={activeTab === "overview" ? "active" : ""} onClick={() => setActiveTab("overview")}>Personal information</button><button type="button" className={activeTab === "assessments" ? "active" : ""} onClick={() => setActiveTab("assessments")}>Assessments <span>{assessments.length}</span></button></nav>

      {activeTab === "overview" && <div className="profile-grid">
        <section className="content-panel"><div className="panel-header"><div><span className="panel-kicker"><UserRound size={15} /> Patient record</span><h2>Personal information</h2></div><button className="icon-button" type="button" onClick={() => setEditOpen(true)} aria-label="Edit patient"><Edit3 size={17} /></button></div><dl className="info-list"><div><dt><Mail size={17} /> Email</dt><dd>{patient.email || "Not recorded"}</dd></div><div><dt><CalendarDays size={17} /> Date of birth</dt><dd>{formatDate(patient.date_of_birth)} ({calculateAge(patient.date_of_birth)} years)</dd></div><div><dt><Ruler size={17} /> Height</dt><dd>{patient.height_cm} cm</dd></div><div><dt><ClipboardPlus size={17} /> Added</dt><dd>{formatDate(patient.created_at)}</dd></div></dl></section>
        <section className="content-panel latest-assessment-panel"><div className="panel-header"><div><span className="panel-kicker"><Activity size={15} /> Latest result</span><h2>Clinical risk summary</h2></div></div>{latest ? <><div className="risk-result-line"><RiskBadge value={latest.prediction_class} /><strong>{formatPercent(latest.prediction_probability)}</strong><span>predicted probability</span></div><dl className="compact-metrics"><div><dt>Assessment date</dt><dd>{formatDate(latest.assessment_date)}</dd></div><div><dt>Current BMI</dt><dd>{bmi}</dd></div><div><dt>Cycle</dt><dd>{latest.cycle_regular ? "Regular" : "Irregular"}</dd></div></dl><button className="button button-secondary button-block" type="button" onClick={() => setActiveTab("assessments")}>View assessment details</button></> : <EmptyState title="No assessment completed" message="Complete the first assessment to calculate a PCOS risk result." action={<button className="button button-primary" type="button" onClick={() => setAssessmentOpen(true)}><Plus size={17} /> Add assessment</button>} />}</section>
        <section className="danger-zone"><div><strong>Delete patient record</strong><p>This permanently removes the patient and all associated assessments.</p></div><button className="button button-danger-subtle" type="button" onClick={() => setConfirm({ type: "patient" })}><Trash2 size={16} /> Delete patient</button></section>
      </div>}

      {activeTab === "assessments" && <section className="content-panel"><div className="panel-header"><div><span className="panel-kicker"><Stethoscope size={15} /> Clinical history</span><h2>Assessment history</h2></div><button className="button button-primary" type="button" onClick={() => setAssessmentOpen(true)}><Plus size={16} /> New assessment</button></div>{assessments.length ? <div className="assessment-list">{assessments.map((assessment) => <AssessmentItem assessment={assessment} onDelete={(item) => setConfirm({ type: "assessment", id: item.assessment_id })} key={assessment.assessment_id} />)}</div> : <EmptyState title="No assessments yet" message="Add the first clinical assessment to create a risk result and patient history." action={<button className="button button-primary" type="button" onClick={() => setAssessmentOpen(true)}><Plus size={17} /> Add assessment</button>} />}</section>}

      <EditPatientDrawer patient={patient} open={editOpen} onClose={() => setEditOpen(false)} onUpdated={(updated) => { setPatient(updated); setEditOpen(false); }} />
      <AssessmentDrawer patient={patient} open={assessmentOpen} onClose={() => setAssessmentOpen(false)} onCreated={(created) => { setAssessments((current) => [created, ...current]); setAssessmentOpen(false); setResult(created); showToast("Risk evaluation complete."); }} />
      <ResultDrawer
        patientId={patient.patient_id}
        result={result}
        open={Boolean(result)}
        onFinish={(updated, notesSaved) => {
          if (updated) {
            setAssessments((current) => current.map((item) => (
              item.assessment_id === updated.assessment_id ? updated : item
            )));
          }
          setResult(null);
          setActiveTab("assessments");
          showToast(
            notesSaved ? "Doctor notes saved." : "Assessment saved without notes.",
            notesSaved ? "success" : "info",
          );
        }}
      />
      <ConfirmDialog open={Boolean(confirm)} title={confirm?.type === "patient" ? "Delete this patient?" : "Delete this assessment?"} message={confirm?.type === "patient" ? "This will permanently delete the patient and every assessment in the record. This cannot be undone." : "This assessment and its risk result will be permanently removed."} loading={deleting} onCancel={() => setConfirm(null)} onConfirm={handleDelete} />
    </div>
  );
}
