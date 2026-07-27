import {
  ArrowRight,
  CalendarClock,
  ClipboardCheck,
  HeartPulse,
  Plus,
  ShieldAlert,
  UserRoundCheck,
  UsersRound,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { apiRequest } from "../services/api";
import { useAuth } from "../auth/auth-context";
import { EmptyState, ErrorState, PageLoader, RiskBadge } from "../components/ui";
import { formatDate, formatPercent, initials } from "../utils/formatters";

const summaryConfig = [
  { key: "total_patients", label: "Total patients", icon: UsersRound, tone: "teal" },
  { key: "total_assessments", label: "Assessments", icon: ClipboardCheck, tone: "green" },
  { key: "high_risk_patients", label: "Need attention", icon: ShieldAlert, tone: "coral" },
  { key: "unassessed_patients", label: "Not assessed", icon: CalendarClock, tone: "amber" },
];

function PatientRow({ item }) {
  const patient = item.patient;
  return (
    <Link className="patient-row" to={`/patients/${patient.patient_id}`}>
      <span className="avatar avatar-patient">{initials(patient.first_name, patient.last_name)}</span>
      <span className="patient-row-name">
        <strong>{patient.first_name} {patient.last_name}</strong>
        <small>Assessed {formatDate(item.assessment_date)}</small>
      </span>
      <RiskBadge value={item.prediction_class} />
      <strong className="probability-value">{formatPercent(item.prediction_probability)}</strong>
      <ArrowRight size={18} className="row-arrow" aria-hidden="true" />
    </Link>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setData(await apiRequest("/dashboard"));
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  if (loading) return <PageLoader label="Preparing your clinical overview" />;
  if (error) return <ErrorState message={error} onRetry={loadDashboard} />;

  const attention = data?.patients_needing_attention || [];
  const recent = data?.recently_assessed_patients || [];
  const summary = data?.summary || {};

  return (
    <div className="page-stack">
      <header className="page-header dashboard-heading">
        <div>
          <span className="eyebrow">Clinical overview</span>
          <h1>Good {new Date().getHours() < 12 ? "morning" : new Date().getHours() < 18 ? "afternoon" : "evening"}, Dr. {user?.first_name}.</h1>
          <p>Here is the latest picture across your patient list.</p>
        </div>
        <Link className="button button-primary" to="/patients?add=1"><Plus size={17} /> Add patient</Link>
      </header>

      <section className="summary-grid" aria-label="Patient summary">
        {summaryConfig.map(({ key, label, icon: Icon, tone }) => (
          <article className="summary-card" key={key}>
            <span className={`summary-icon summary-icon-${tone}`}><Icon size={21} /></span>
            <div><strong>{summary[key] ?? 0}</strong><span>{label}</span></div>
          </article>
        ))}
      </section>

      <section className="dashboard-grid">
        <div className="content-panel attention-panel">
          <div className="panel-header">
            <div><span className="panel-kicker"><HeartPulse size={15} /> Priority review</span><h2>Patients needing attention</h2></div>
          </div>
          {attention.length ? (
            <div className="patient-row-list">{attention.map((item) => <PatientRow item={item} key={item.assessment_id} />)}</div>
          ) : (
            <EmptyState title="No high-risk patients" message="High-risk results from each patient's latest assessment will appear here." />
          )}
        </div>

        <aside className="clinical-note-panel">
          <span className="clinical-note-icon"><UserRoundCheck size={23} /></span>
          <span className="eyebrow eyebrow-light">Today’s focus</span>
          <h2>{summary.unassessed_patients || 0} patients are waiting for a first assessment.</h2>
          <p>Complete an assessment to establish a baseline and include the patient in risk summaries.</p>
          <Link className="button button-light" to="/patients">Open patient list <ArrowRight size={17} /></Link>
        </aside>
      </section>

      <section className="content-panel">
        <div className="panel-header">
          <div><span className="panel-kicker"><ClipboardCheck size={15} /> Latest activity</span><h2>Recently assessed</h2></div>
        </div>
        {recent.length ? (
          <div className="patient-row-list">{recent.map((item) => <PatientRow item={item} key={item.assessment_id} />)}</div>
        ) : (
          <EmptyState
            title="No assessments yet"
            message="Add a patient and complete the first guided assessment to begin your overview."
            action={<Link className="button button-primary" to="/patients?add=1"><Plus size={17} /> Add first patient</Link>}
          />
        )}
      </section>
    </div>
  );
}
