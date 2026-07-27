import {
  ArrowRight,
  CalendarDays,
  Filter,
  Mail,
  Plus,
  Ruler,
  Search,
  UserRound,
  UsersRound,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { apiRequest } from "../services/api";
import { useToast } from "../components/ToastProvider";
import { Drawer, EmptyState, ErrorState, Field, PageLoader, RiskBadge, Spinner } from "../components/ui";
import { calculateAge, formatDate, formatPercent, initials } from "../utils/formatters";

const emptyPatient = {
  first_name: "",
  last_name: "",
  email: "",
  date_of_birth: "",
  height_cm: "",
};

function PatientTable({ patients, latest }) {
  return (
    <div className="patient-table-wrap">
      <table className="data-table patient-table">
        <thead><tr><th>Patient</th><th>Age</th><th>Latest risk</th><th>Added</th><th><span className="sr-only">Open</span></th></tr></thead>
        <tbody>
          {patients.map((patient) => {
            const result = latest[patient.patient_id];
            return (
              <tr key={patient.patient_id}>
                <td><Link className="table-patient" to={`/patients/${patient.patient_id}`}><span className="avatar avatar-patient">{initials(patient.first_name, patient.last_name)}</span><span><strong>{patient.first_name} {patient.last_name}</strong><small>{patient.email || "No email recorded"}</small></span></Link></td>
                <td>{calculateAge(patient.date_of_birth)} years</td>
                <td><div className="risk-cell"><RiskBadge value={result?.prediction_class} />{result && <small>{formatPercent(result.prediction_probability)}</small>}</div></td>
                <td>{formatDate(patient.created_at)}</td>
                <td><Link className="icon-button" to={`/patients/${patient.patient_id}`} aria-label={`Open ${patient.first_name} ${patient.last_name}`}><ArrowRight size={18} /></Link></td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function PatientCards({ patients, latest }) {
  return (
    <div className="patient-card-list">
      {patients.map((patient) => {
        const result = latest[patient.patient_id];
        return (
          <Link className="patient-mobile-card" to={`/patients/${patient.patient_id}`} key={patient.patient_id}>
            <div className="patient-card-head"><span className="avatar avatar-patient">{initials(patient.first_name, patient.last_name)}</span><span><strong>{patient.first_name} {patient.last_name}</strong><small>{calculateAge(patient.date_of_birth)} years</small></span><ArrowRight size={18} /></div>
            <div className="patient-card-meta"><RiskBadge value={result?.prediction_class} /><span>{result ? formatPercent(result.prediction_probability) : "No assessment"}</span></div>
          </Link>
        );
      })}
    </div>
  );
}

function AddPatientDrawer({ open, onClose, onCreated }) {
  const { showToast } = useToast();
  const [form, setForm] = useState(emptyPatient);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const update = (field, value) => setForm((current) => ({ ...current, [field]: value }));

  function resetAndClose() {
    setForm(emptyPatient);
    setError("");
    onClose();
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true); setError("");
    try {
      const patient = await apiRequest("/patients/", {
        method: "POST",
        body: JSON.stringify({
          ...form,
          email: form.email.trim() || null,
          height_cm: Number(form.height_cm),
        }),
      });
      showToast(`${patient.first_name} ${patient.last_name} was added.`);
      setForm(emptyPatient);
      setError("");
      onCreated(patient);
    } catch (requestError) { setError(requestError.message); }
    finally { setSubmitting(false); }
  }

  return (
    <Drawer open={open} onClose={resetAndClose} title="Add a new patient" description="Start with the essential personal information. An assessment can be added next.">
      {error && <div className="form-notice error-notice" role="alert">{error}</div>}
      <form className="drawer-form" onSubmit={handleSubmit}>
        <section className="form-section"><div className="form-section-heading"><span><UserRound size={19} /></span><div><h3>Personal information</h3><p>Fields marked with an asterisk are required.</p></div></div>
          <div className="form-grid form-grid-two"><Field label="First name" required>{(props) => <input {...props} value={form.first_name} onChange={(e) => update("first_name", e.target.value)} autoComplete="given-name" required />}</Field><Field label="Last name" required>{(props) => <input {...props} value={form.last_name} onChange={(e) => update("last_name", e.target.value)} autoComplete="family-name" required />}</Field></div>
          <Field label="Email address" hint="Optional">{(props) => <div className="input-with-icon"><Mail size={18} /><input {...props} type="email" value={form.email} onChange={(e) => update("email", e.target.value)} autoComplete="email" placeholder="patient@example.com" /></div>}</Field>
        </section>
        <section className="form-section"><div className="form-section-heading"><span><CalendarDays size={19} /></span><div><h3>Clinical basics</h3><p>Used to calculate age and body measurements during assessment.</p></div></div>
          <Field label="Date of birth" required>{(props) => <input {...props} type="date" max={new Date().toISOString().slice(0, 10)} value={form.date_of_birth} onChange={(e) => update("date_of_birth", e.target.value)} required />}</Field>
          <Field label="Height" hint="Allowed range: 80–250 cm" required>{(props) => <div className="input-with-suffix"><Ruler size={18} /><input {...props} type="number" min="80" max="250" step="0.1" value={form.height_cm} onChange={(e) => update("height_cm", e.target.value)} required /><span>cm</span></div>}</Field>
        </section>
        <div className="drawer-actions"><button className="button button-secondary" type="button" onClick={resetAndClose}>Cancel</button><button className="button button-primary" type="submit" disabled={submitting}>{submitting ? <Spinner label="Adding patient" /> : "Add patient"}</button></div>
      </form>
    </Drawer>
  );
}

export default function PatientsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [patients, setPatients] = useState([]);
  const [latest, setLatest] = useState({});
  const [search, setSearch] = useState(searchParams.get("name") || "");
  const [risk, setRisk] = useState(searchParams.get("risk") || "");
  const drawerOpen = searchParams.get("add") === "1";
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadPatients = useCallback(async (name = search, predictionClass = risk) => {
    setLoading(true); setError("");
    try {
      const query = new URLSearchParams();
      if (name.trim()) query.set("name", name.trim());
      if (predictionClass) query.set("prediction_class", predictionClass);

      const list = await apiRequest(
        query.toString() ? `/patients/search?${query}` : "/patients/",
      );
      setPatients(list);

      const assessmentResponses = await Promise.allSettled(
        list.map((patient) =>
          apiRequest(`/patients/${patient.patient_id}/assessments/?limit=1`),
        ),
      );
      const nextLatest = {};
      assessmentResponses.forEach((response, index) => {
        if (response.status === "fulfilled" && response.value[0]) {
          nextLatest[list[index].patient_id] = response.value[0];
        }
      });
      setLatest(nextLatest);
    } catch (requestError) { setError(requestError.message); }
    finally { setLoading(false); }
  }, [search, risk]);

  useEffect(() => {
    const timer = window.setTimeout(() => loadPatients(search, risk), 350);
    return () => window.clearTimeout(timer);
  }, [search, risk]); // eslint-disable-line react-hooks/exhaustive-deps

  function closeDrawer() {
    const next = new URLSearchParams(searchParams);
    next.delete("add");
    setSearchParams(next, { replace: true });
  }

  function openDrawer() {
    const next = new URLSearchParams(searchParams);
    next.set("add", "1");
    setSearchParams(next, { replace: true });
  }

  const resultsLabel = useMemo(() => `${patients.length} patient${patients.length === 1 ? "" : "s"}`, [patients.length]);

  return (
    <div className="page-stack">
      <header className="page-header"><div><span className="eyebrow">Patient management</span><h1>Patients</h1><p>Search records, review risk history, or begin a new assessment.</p></div><button className="button button-primary" type="button" onClick={openDrawer}><Plus size={17} /> Add patient</button></header>

      <section className="filter-bar" aria-label="Patient filters">
        <label className="search-control"><Search size={19} /><span className="sr-only">Search patients</span><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search by patient name" /></label>
        <label className="select-control"><Filter size={18} /><span className="sr-only">Filter by risk</span><select value={risk} onChange={(event) => setRisk(event.target.value)}><option value="">All risk levels</option><option value="High Risk">High Risk</option><option value="Low Risk">Low Risk</option></select></label>
        <span className="result-count">{loading ? "Searching…" : resultsLabel}</span>
      </section>

      {loading ? <PageLoader label="Loading patient records" /> : error ? <ErrorState message={error} onRetry={() => loadPatients()} /> : patients.length ? (
        <section className="content-panel patient-directory" aria-label="Patient directory"><div className="directory-heading"><div><UsersRound size={19} /><strong>Patient directory</strong></div><span>{resultsLabel}</span></div><PatientTable patients={patients} latest={latest} /><PatientCards patients={patients} latest={latest} /></section>
      ) : (
        <section className="content-panel"><EmptyState title={search || risk ? "No patients match these filters" : "No patients added yet"} message={search || risk ? "Try a different name or risk level." : "Create the first patient record to begin an assessment."} action={!search && !risk ? <button className="button button-primary" type="button" onClick={openDrawer}><Plus size={17} /> Add first patient</button> : null} /></section>
      )}

      <AddPatientDrawer open={drawerOpen} onClose={closeDrawer} onCreated={(patient) => { closeDrawer(); setPatients((current) => [patient, ...current]); }} />
    </div>
  );
}
