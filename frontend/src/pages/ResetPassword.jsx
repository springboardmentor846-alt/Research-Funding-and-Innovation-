import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import api from "../api/axios";

function ResetPassword() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const token = searchParams.get("token");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!token) {
      setMessage("This password reset link is invalid.");
      return;
    }

    if (password !== confirmPassword) {
      setMessage("Passwords do not match.");
      return;
    }

    try {
      setLoading(true);
      setMessage("");

      await api.post("/auth/reset-password", {
        token,
        new_password: password,
      });

      navigate("/login", {
        replace: true,
        state: {
          message: "Password reset successfully. You can now sign in.",
        },
      });

    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
        "Unable to reset your password."
      );
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
            <span className="auth-eyebrow">
              SECURE ACCOUNT RECOVERY
            </span>

            <h1>
              Create a new<span> password.</span>
            </h1>

            <p>
              Choose a secure password to protect your research and
              innovation workspace.
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
            <div className="auth-mobile-logo">
              RF
            </div>

            <div>
              <strong>Research Funding</strong>
              <span>Innovation Platform</span>
            </div>
          </div>

          <div className="auth-form-heading">
            <span className="auth-form-eyebrow">
              RESET PASSWORD
            </span>

            <h2>Create new password</h2>

            <p>
              Enter your new password below.
            </p>
          </div>

          {message && (
            <div className="auth-message">
              <span>!</span>
              {message}
            </div>
          )}

          <form
            onSubmit={handleSubmit}
            className="auth-professional-form"
          >

            <div className="auth-field">
              <label htmlFor="new-password">
                New password
              </label>

              <div className="auth-input-wrapper">
                <span className="auth-input-symbol">
                  •
                </span>

                <input
                  id="new-password"
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  minLength="8"
                  autoComplete="new-password"
                  placeholder="Create a new password"
                  required
                />
              </div>
            </div>

            <div className="auth-field">
              <label htmlFor="confirm-password">
                Confirm password
              </label>

              <div className="auth-input-wrapper">
                <span className="auth-input-symbol">
                  •
                </span>

                <input
                  id="confirm-password"
                  type="password"
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  minLength="8"
                  autoComplete="new-password"
                  placeholder="Enter the password again"
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
                {loading ? "Resetting..." : "Reset password"}
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

export default ResetPassword;