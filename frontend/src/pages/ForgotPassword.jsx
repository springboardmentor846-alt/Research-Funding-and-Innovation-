import { useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios";

function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      setLoading(true);
      setMessage("");
      setSuccess(false);

      const response = await api.post("/auth/forgot-password", { email });

      setMessage(response.data.message);
      setSuccess(true);
    } catch (error) {
      const detail = error.response?.data?.detail;

      setMessage(
        detail || "Unable to process the request. Please try again later."
      );
      setSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <section className="auth-brand-panel">
        <div className="auth-brand-content">
          <div className="auth-brand-mark">
            <span>RF</span>
            <div>
              <strong>Research Funding</strong>
              <small>Innovation Platform</small>
            </div>
          </div>

          <div className="auth-hero-content">
            <span className="auth-eyebrow">ACCOUNT RECOVERY</span>

            <h1>
              Get back to your<span> workspace.</span>
            </h1>

            <p>
              Enter your registered email address and we will send you a
              secure password reset link.
            </p>
          </div>
        </div>

        <div className="auth-brand-footer">
          Research Funding Innovation Platform
        </div>
      </section>

      <main className="auth-form-panel">
        <div className="auth-form-wrapper">

          <div className="auth-mobile-brand">
            <div className="auth-mobile-logo">RF</div>
            <div>
              <strong>Research Funding</strong>
              <span>Innovation Platform</span>
            </div>
          </div>

          <div className="auth-form-heading">
            <span className="auth-form-eyebrow">
              PASSWORD RECOVERY
            </span>

            <h2>Forgot your password?</h2>

            <p>
              Enter your email address to receive a password reset link.
            </p>
          </div>

          {message && (
            <div className={success ? "auth-message auth-success" : "auth-message"}>
              <span>{success ? "✓" : "!"}</span>
              {message}
            </div>
          )}

          <form
            onSubmit={handleSubmit}
            className="auth-professional-form"
          >
            <div className="auth-field">
              <label htmlFor="email">
                Email address
              </label>

              <div className="auth-input-wrapper">
                <span className="auth-input-symbol">
                  @
                </span>

                <input
                  id="email"
                  type="email"
                  placeholder="name@organization.com"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  autoComplete="email"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className="auth-submit-btn"
              disabled={loading}
            >
              <span>
                {loading ? "Sending..." : "Send reset link"}
              </span>

              {!loading && (
                <span className="auth-button-arrow">
                  →
                </span>
              )}
            </button>
          </form>

          <br />

          <Link
            to="/login"
            className="auth-secondary-link"
          >
            Back to sign in
          </Link>

        </div>
      </main>
    </div>
  );
}

export default ForgotPassword;