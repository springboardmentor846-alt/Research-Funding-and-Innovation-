import { useState, useEffect } from "react";
import axios from "axios";
import "./Login.css";

function ResetPassword({ onSwitchToLogin }) {
  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("error");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const tokenFromUrl = params.get("token");
    if (tokenFromUrl) {
      setToken(tokenFromUrl);
    } else {
      setMessage("No reset token found. Please use the link from your email.");
      setMessageType("error");
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");

    if (newPassword !== confirmPassword) {
      setMessage("Passwords do not match");
      setMessageType("error");
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/v1/auth/reset-password",
        { token, new_password: newPassword }
      );
      setMessage(response.data.message);
      setMessageType("success");
      setSuccess(true);
    } catch (error) {
      if (error.response) {
        setMessage(error.response.data.detail || "Could not reset password");
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
        </div>
      </div>

      <div className="auth-form-side">
        <div className="auth-card">
          <span className="auth-eyebrow">Reset password</span>
          <h2 className="auth-title">Choose a new password</h2>

          {!success ? (
            <form className="auth-form" onSubmit={handleSubmit}>
              <div className="field">
                <label>New Password</label>
                <input
                  type="password"
                  placeholder="At least 6 characters"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                />
              </div>
              <div className="field">
                <label>Confirm Password</label>
                <input
                  type="password"
                  placeholder="Re-enter your new password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                />
              </div>
              <button type="submit" className="auth-submit" disabled={isSubmitting || !token}>
                {isSubmitting ? "Resetting..." : "Reset Password"}
              </button>
            </form>
          ) : (
            <p className="auth-switch">
              <span onClick={onSwitchToLogin}>Go to Sign In</span>
            </p>
          )}

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

export default ResetPassword;