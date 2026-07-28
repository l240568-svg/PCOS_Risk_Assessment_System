import { ArrowLeft, Clock3, KeyRound, Mail, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { apiRequest } from "../services/api";
import AuthLayout from "../components/AuthLayout";
import { Field, Spinner } from "../components/ui";

const OTP_EXPIRATION_SECONDS = 60;

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
  const [otpExpiresAt, setOtpExpiresAt] = useState(null);
  const [secondsRemaining, setSecondsRemaining] = useState(0);

  useEffect(() => {
    if (step !== 2 || !otpExpiresAt) return undefined;

    const countdown = window.setInterval(() => {
      const remaining = Math.max(
        0,
        Math.ceil((otpExpiresAt - Date.now()) / 1000),
      );

      setSecondsRemaining(remaining);

      if (remaining === 0) {
        window.clearInterval(countdown);
      }
    }, 250);

    return () => window.clearInterval(countdown);
  }, [step, otpExpiresAt]);

  function startOtpCountdown() {
    setOtpExpiresAt(
      Date.now() + OTP_EXPIRATION_SECONDS * 1000,
    );
    setSecondsRemaining(OTP_EXPIRATION_SECONDS);
  }

  async function submitEmail(event) {
    event.preventDefault();
    setSubmitting(true); setError("");
    try {
      const response = await apiRequest("/auth/forgot-password", { method: "POST", body: { email: email.trim() } });
      setMessage(response.message);
      setOtp("");
      startOtpCountdown();
      setStep(2);
    } catch (requestError) { setError(requestError.message); }
    finally { setSubmitting(false); }
  }

  async function resendOtp() {
    setSubmitting(true);
    setError("");

    try {
      const response = await apiRequest(
        "/auth/forgot-password",
        {
          method: "POST",
          body: { email: email.trim() },
        },
      );

      setMessage(response.message);
      setOtp("");
      startOtpCountdown();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSubmitting(false);
    }
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
      await apiRequest("/auth/reset-password", { method: "PATCH", body: { reset_token: resetToken, new_password: passwords.password } });
      navigate("/login", { replace: true, state: { passwordReset: true } });
    } catch (requestError) { setError(requestError.message); }
    finally { setSubmitting(false); }
  }

  const titles = ["Reset your password", "Enter the security code", "Choose a new password"];
  const descriptions = ["We will send a six-digit code to your account email.", `Enter the code sent to ${email}.`, "Use a strong password you have not used before."];
  const otpExpired = step === 2 && secondsRemaining === 0;
  const countdownMinutes = Math.floor(secondsRemaining / 60);
  const countdownSeconds = secondsRemaining % 60;
  const formattedCountdown = [
    countdownMinutes,
    countdownSeconds,
  ]
    .map((value) => String(value).padStart(2, "0"))
    .join(":");

  return (
    <AuthLayout eyebrow={`Password recovery · Step ${step} of 3`} title={titles[step - 1]} description={descriptions[step - 1]}>
      <div className="step-dots" aria-label={`Step ${step} of 3`}>{[1, 2, 3].map((item) => <span key={item} className={item <= step ? "active" : ""} />)}</div>
      {message && step === 2 && <div className="form-notice info-notice">{message}</div>}
      {error && <div className="form-notice error-notice" role="alert">{error}</div>}

      {step === 1 && <form className="auth-form" onSubmit={submitEmail}><Field label="Account email" required>{(props) => <div className="input-with-icon"><Mail size={18} /><input {...props} type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" required /></div>}</Field><button className="button button-primary button-block button-large" disabled={submitting}>{submitting ? <Spinner label="Sending code" /> : "Send security code"}</button></form>}

      {step === 2 && (
        <form className="auth-form" onSubmit={submitOtp}>
          <div
            className={`otp-timer${otpExpired ? " is-expired" : ""}`}
            role="timer"
            aria-live="polite"
          >
            <Clock3 size={17} />

            {otpExpired ? (
              <span>This security code has expired.</span>
            ) : (
              <span>
                Code expires in{" "}
                <strong>{formattedCountdown}</strong>
              </span>
            )}

            {otpExpired && (
              <button
                className="otp-resend-button"
                type="button"
                onClick={resendOtp}
                disabled={submitting}
              >
                {submitting ? "Sending..." : "Resend code"}
              </button>
            )}
          </div>

          <Field label="Six-digit code" required>
            {(props) => (
              <div className="input-with-icon">
                <ShieldCheck size={18} />
                <input
                  {...props}
                  className="otp-input"
                  inputMode="numeric"
                  pattern="[0-9]{6}"
                  maxLength="6"
                  value={otp}
                  onChange={(e) =>
                    setOtp(e.target.value.replace(/\D/g, ""))
                  }
                  autoComplete="one-time-code"
                  disabled={otpExpired || submitting}
                  required
                />
              </div>
            )}
          </Field>

          <button
            className="button button-primary button-block button-large"
            disabled={
              submitting ||
              otpExpired ||
              otp.length !== 6
            }
          >
            {submitting && !otpExpired ? (
              <Spinner label="Verifying" />
            ) : (
              "Verify code"
            )}
          </button>

          <button
            className="button button-ghost button-block"
            type="button"
            onClick={() => {
              setStep(1);
              setOtp("");
              setOtpExpiresAt(null);
              setSecondsRemaining(0);
              setMessage("");
              setError("");
            }}
          >
            Use a different email
          </button>
        </form>
      )}

      {step === 3 && <form className="auth-form" onSubmit={submitPassword}><Field label="New password" hint="At least 8 characters with uppercase, lowercase, and a special character." required>{(props) => <div className="input-with-icon"><KeyRound size={18} /><input {...props} type="password" minLength="8" value={passwords.password} onChange={(e) => setPasswords({ ...passwords, password: e.target.value })} autoComplete="new-password" required /></div>}</Field><Field label="Confirm new password" required>{(props) => <input {...props} type="password" minLength="8" value={passwords.confirm} onChange={(e) => setPasswords({ ...passwords, confirm: e.target.value })} autoComplete="new-password" required />}</Field><button className="button button-primary button-block button-large" disabled={submitting}>{submitting ? <Spinner label="Updating password" /> : "Update password"}</button></form>}

      <p className="auth-switch"><Link to="/login"><ArrowLeft size={15} /> Back to sign in</Link></p>
    </AuthLayout>
  );
}
