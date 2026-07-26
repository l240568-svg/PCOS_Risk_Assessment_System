import { CheckCircle2 } from "lucide-react";
import { Link } from "react-router-dom";

import Logo from "./Logo";

export default function AuthLayout({ eyebrow, title, description, children }) {
  return (
    <div className="auth-page">
      <aside className="auth-visual">
        <Link to="/" className="auth-back-brand">
          <Logo />
        </Link>
        <div className="auth-visual-content">
          <span className="eyebrow eyebrow-light">Designed for clinical focus</span>
          <h1>Clear risk insights, organized around every patient.</h1>
          <p>
            A calm, secure workspace for managing PCOS assessments and following patients over time.
          </p>
          <div className="auth-benefits">
            <span><CheckCircle2 size={18} /> Structured clinical assessments</span>
            <span><CheckCircle2 size={18} /> Patient history in one place</span>
            <span><CheckCircle2 size={18} /> Fast, responsive workflows</span>
          </div>
        </div>
        <p className="auth-disclaimer">Decision support only. Results do not replace clinical diagnosis.</p>
      </aside>

      <main className="auth-form-side">
        <div className="auth-mobile-brand"><Logo /></div>
        <div className="auth-form-wrap">
          <span className="eyebrow">{eyebrow}</span>
          <h2>{title}</h2>
          <p className="auth-description">{description}</p>
          {children}
        </div>
      </main>
    </div>
  );
}
