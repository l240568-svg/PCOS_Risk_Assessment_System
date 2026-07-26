import { Eye, EyeOff } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/auth-context";
import AuthLayout from "../components/AuthLayout";
import { Field, Spinner } from "../components/ui";

const initialForm = {
  first_name: "",
  last_name: "",
  email: "",
  specialization: "Gynecologist",
  hospital: "",
  clinic_address: "",
  license_number: "",
  password: "",
  confirmPassword: "",
};

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(initialForm);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setSubmitting(true);
    try {
      await register({
        first_name: form.first_name,
        last_name: form.last_name,
        email: form.email.trim(),
        specialization: form.specialization,
        hospital: form.hospital.trim() || null,
        clinic_address: form.clinic_address.trim() || null,
        license_number: form.license_number,
        password: form.password,
      });
      navigate("/login", { replace: true, state: { registered: true } });
    } catch (requestError) {
      setError(requestError.message || "Unable to create account.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthLayout eyebrow="Doctor registration" title="Create your clinical workspace" description="Enter your professional details exactly as they should appear in your profile.">
      {error && <div className="form-notice error-notice" role="alert">{error}</div>}
      <form className="auth-form" onSubmit={handleSubmit}>
        <div className="form-grid form-grid-two">
          <Field label="First name" required>{(props) => <input {...props} value={form.first_name} onChange={(e) => update("first_name", e.target.value)} autoComplete="given-name" required />}</Field>
          <Field label="Last name" required>{(props) => <input {...props} value={form.last_name} onChange={(e) => update("last_name", e.target.value)} autoComplete="family-name" required />}</Field>
        </div>
        <Field label="Professional email" required>{(props) => <input {...props} type="email" value={form.email} onChange={(e) => update("email", e.target.value)} autoComplete="email" placeholder="doctor@hospital.com" required />}</Field>
        <div className="form-grid form-grid-two">
          <Field label="Specialization" required>{(props) => <select {...props} value={form.specialization} onChange={(e) => update("specialization", e.target.value)}><option>Gynecologist</option><option>Endocrinologist</option></select>}</Field>
          <Field label="License number" required>{(props) => <input {...props} value={form.license_number} onChange={(e) => update("license_number", e.target.value)} required />}</Field>
        </div>
        <Field label="Hospital or clinic">{(props) => <input {...props} value={form.hospital} onChange={(e) => update("hospital", e.target.value)} autoComplete="organization" />}</Field>
        <Field label="Clinic address">{(props) => <input {...props} value={form.clinic_address} onChange={(e) => update("clinic_address", e.target.value)} autoComplete="street-address" />}</Field>
        <Field label="Password" hint="At least 8 characters with uppercase, lowercase, and a special character." required>
          {(props) => <div className="input-with-action"><input {...props} type={showPassword ? "text" : "password"} value={form.password} onChange={(e) => update("password", e.target.value)} autoComplete="new-password" minLength="8" required /><button type="button" className="input-action" onClick={() => setShowPassword((show) => !show)} aria-label={showPassword ? "Hide password" : "Show password"}>{showPassword ? <EyeOff size={18} /> : <Eye size={18} />}</button></div>}
        </Field>
        <Field label="Confirm password" required>{(props) => <input {...props} type={showPassword ? "text" : "password"} value={form.confirmPassword} onChange={(e) => update("confirmPassword", e.target.value)} autoComplete="new-password" minLength="8" required />}</Field>
        <button className="button button-primary button-block button-large" type="submit" disabled={submitting}>{submitting ? <Spinner label="Creating account" /> : "Create doctor account"}</button>
      </form>
      <p className="auth-switch">Already have an account? <Link to="/login">Sign in</Link></p>
    </AuthLayout>
  );
}
