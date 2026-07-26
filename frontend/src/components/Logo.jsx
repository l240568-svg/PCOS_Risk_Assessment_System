import { Activity } from "lucide-react";
import { Link } from "react-router-dom";

export default function Logo({ to = "/", compact = false }) {
  return (
    <Link className="brand" to={to} aria-label="PCOS Care home">
      <span className="brand-mark" aria-hidden="true">
        <Activity size={20} strokeWidth={2.25} />
      </span>
      {!compact && (
        <span>
          <strong>PCOS Care</strong>
          <small>Clinical workspace</small>
        </span>
      )}
    </Link>
  );
}
