import { ArrowLeft, KeyRound, Mail, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { apiRequest } from "../services/api";
import AuthLayout from "../components/AuthLayout";
import { Field, Spinner } from "../components/ui";

export default function ForgotPasswordPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [resetToken, setResetToken] = useState("");
  const [passwords, setPasswords] = useState({ password: "", confirm: "" });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function submitEmail(event) {
    event.preventDefault();
    setSubmitting(true); setError("");
    try {
      const response = await apiRequest("/auth/forgot-password", { method: "POST", body: { email: email.trim() } });
      setMessage(response.message);
      setStep(2);
    } catch (requestError) { setError(requestError.message); }
    finally { setSubmitting(false); }
  }

  async function submitOtp(event) {
    event.preventDefault();
    setSubmitting(true); setError("");
    try {
      const response = await apiRequest("/auth/verify-otp", { method: "POST", body: { email: email.trim(), otp: otp } });
      setResetToken(response.reset_token);
      setStep(3);
    } catch (requestError) { setError(requestError.message); }
    finally { setSubmitting(false); }
  }

  async function submitPassword(event) {
    event.preventDefault();
    setError("");
    if (passwords.password !== passwords.confirm) {
      setError("Passwords do not match.");
      return;
    }
    setSubmitting(true);
    try {
      await apiRequest("/auth/reset-password", { method: "POST", body: { reset_token: resetToken, password: passwords.password } });
      navigate("/login", { replace: true, state: { passwordReset: true } });
    } catch (requestError) { setError(requestError.message); }
    finally { setSubmitting(false); }
  }

  const titles = ["Reset your password", "Enter the security code", "Choose a new password"];
  const descriptions = ["We will send a six-digit code to your account email.", `Enter the code sent to ${email}.`, "Use a strong password you have not used before."];

  return (
    <AuthLayout eyebrow={`Password recovery · Step ${step} of 3`} title={titles[step - 1]} description={descriptions[step - 1]}>
      <div className="step-dots" aria-label={`Step ${step} of 3`}>{[1, 2, 3].map((item) => <span key={item} className={item <= step ? "active" : ""} />)}</div>
      {message && step === 2 && <div className="form-notice info-notice">{message}</div>}
      {error && <div className="form-notice error-notice" role="alert">{error}</div>}

      {step === 1 && <form className="auth-form" onSubmit={submitEmail}><Field label="Account email" required>{(props) => <div className="input-with-icon"><Mail size={18} /><input {...props} type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" required /></div>}</Field><button className="button button-primary button-block button-large" disabled={submitting}>{submitting ? <Spinner label="Sending code" /> : "Send security code"}</button></form>}

      {step === 2 && <form className="auth-form" onSubmit={submitOtp}><Field label="Six-digit code" required>{(props) => <div className="input-with-icon"><ShieldCheck size={18} /><input {...props} className="otp-input" inputMode="numeric" pattern="[0-9]{6}" maxLength="6" value={otp} onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))} autoComplete="one-time-code" required /></div>}</Field><button className="button button-primary button-block button-large" disabled={submitting || otp.length !== 6}>{submitting ? <Spinner label="Verifying" /> : "Verify code"}</button><button className="button button-ghost button-block" type="button" onClick={() => setStep(1)}>Use a different email</button></form>}

      {step === 3 && <form className="auth-form" onSubmit={submitPassword}><Field label="New password" hint="At least 8 characters with uppercase, lowercase, and a special character." required>{(props) => <div className="input-with-icon"><KeyRound size={18} /><input {...props} type="password" minLength="8" value={passwords.password} onChange={(e) => setPasswords({ ...passwords, password: e.target.value })} autoComplete="new-password" required /></div>}</Field><Field label="Confirm new password" required>{(props) => <input {...props} type="password" minLength="8" value={passwords.confirm} onChange={(e) => setPasswords({ ...passwords, confirm: e.target.value })} autoComplete="new-password" required />}</Field><button className="button button-primary button-block button-large" disabled={submitting}>{submitting ? <Spinner label="Updating password" /> : "Update password"}</button></form>}

      <p className="auth-switch"><Link to="/login"><ArrowLeft size={15} /> Back to sign in</Link></p>
    </AuthLayout>
  );
}
