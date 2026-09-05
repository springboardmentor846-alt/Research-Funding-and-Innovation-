import { useState } from "react";
import axios from "axios";
import "./Login.css";

function ForgotPassword({ onSwitchToLogin }) {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("error");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setIsSubmitting(true);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/v1/auth/forgot-password",
        { email }
      );
      setMessage(response.data.message);
      setMessageType("success");
    } catch (error) {
      if (error.response) {
        setMessage(error.response.data.detail || "Something went wrong");
      } else {
        setMessage("Could not connect to server");
      }
      setMessageType("error");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-brand">
        <div className="auth-brand-top">
          <div className="auth-logo">
            Research Funding &amp; <span className="highlight">Innovation Intelligence</span> Platform
          </div>
        </div>
        <div className="auth-brand-bottom">
          <div className="auth-tagline">Where research meets opportunity.</div>
          <div className="auth-subtext">
            Enter your email and we'll send you a link to reset your password.
          </div>
        </div>
      </div>

      <div className="auth-form-side">
        <div className="auth-card">
          <span className="auth-eyebrow">Forgot password</span>
          <h2 className="auth-title">Reset your password</h2>
          <p className="auth-desc">
            We'll email you a link to set a new password.
          </p>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="field">
              <label>Email</label>
              <input
                type="email"
                placeholder="you@organization.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="auth-submit" disabled={isSubmitting}>
              {isSubmitting ? "Sending..." : "Send Reset Link"}
            </button>
          </form>

          <p className="auth-switch">
            Remembered your password?{" "}
            <span onClick={onSwitchToLogin}>Back to Sign In</span>
          </p>

          {message && (
            <p className={`auth-message ${messageType === "success" ? "auth-message-success" : "auth-message-error"}`}>
              {message}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default ForgotPassword;