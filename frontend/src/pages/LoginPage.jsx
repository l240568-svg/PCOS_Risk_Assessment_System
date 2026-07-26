import { Eye, EyeOff, LockKeyhole, Mail } from "lucide-react";
import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/auth-context";
import AuthLayout from "../components/AuthLayout";
import { useToast } from "../components/ToastProvider";
import { Field, Spinner } from "../components/ui";

export default function LoginPage() {
  const { login } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "", password: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(form.email.trim(), form.password);
      showToast("Welcome back. Your workspace is ready.");
      navigate(location.state?.from?.pathname || "/dashboard", { replace: true });
    } catch (requestError) {
      setError(requestError.message || "Unable to sign in.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthLayout eyebrow="Welcome back" title="Sign in to your workspace" description="Use the email connected to your doctor account.">
      {location.state?.registered && <div className="form-notice success-notice">Account created successfully. You can now sign in.</div>}
      {location.state?.passwordReset && <div className="form-notice success-notice">Password updated successfully. Sign in with your new password.</div>}
      {error && <div className="form-notice error-notice" role="alert">{error}</div>}
      <form className="auth-form" onSubmit={handleSubmit}>
        <Field label="Email address" required>
          {(fieldProps) => (
            <div className="input-with-icon">
              <Mail size={18} />
              <input {...fieldProps} type="email" autoComplete="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} placeholder="doctor@hospital.com" required />
            </div>
          )}
        </Field>
        <Field label="Password" required>
          {(fieldProps) => (
            <div className="input-with-icon input-with-action">
              <LockKeyhole size={18} />
              <input {...fieldProps} type={showPassword ? "text" : "password"} autoComplete="current-password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} placeholder="Enter your password" required />
              <button type="button" className="input-action" onClick={() => setShowPassword((show) => !show)} aria-label={showPassword ? "Hide password" : "Show password"}>
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          )}
        </Field>
        <div className="form-link-row"><span /><Link to="/forgot-password">Forgot password?</Link></div>
        <button className="button button-primary button-block button-large" type="submit" disabled={submitting}>
          {submitting ? <Spinner label="Signing in" /> : "Sign in"}
        </button>
      </form>
      <p className="auth-switch">New to PCOS Care? <Link to="/register">Create a doctor account</Link></p>
    </AuthLayout>
  );
}
