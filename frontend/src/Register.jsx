import { useState } from "react";
import axios from "axios";
import "./Login.css";
import "./Register.css";

function Register({ onSwitchToLogin }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("researcher");
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("error");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    setMessage("");
    setIsSubmitting(true);

    try {
      const response = await axios.post("http://127.0.0.1:8000/api/v1/auth/register", {
        name,
        email,
        password,
        role,
      });

      setMessage(`Registered successfully! You can now sign in.`);
      setMessageType("success");
    } catch (error) {
      if (error.response) {
        setMessage(error.response.data.detail || "Registration failed");
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
      {/* LEFT BRAND PANEL */}
      <div className="auth-brand">
        <div className="auth-brand-top">
          <div className="auth-logo">
            Research Funding &amp; <span className="highlight">Innovation Intelligence</span> Platform
          </div>
        </div>
        <div className="auth-brand-mid">
          <svg width="280" height="220" viewBox="0 0 280 220">
            <line className="link" x1="140" y1="40" x2="60" y2="100" />
            <line className="link" x1="140" y1="40" x2="220" y2="90" />
            <line className="link" x1="60" y1="100" x2="90" y2="170" />
            <line className="link" x1="220" y1="90" x2="190" y2="170" />
            <line className="link" x1="90" y1="170" x2="190" y2="170" />
            <line className="link" x1="140" y1="40" x2="140" y2="110" />
            <line className="link" x1="140" y1="110" x2="90" y2="170" />
            <line className="link" x1="140" y1="110" x2="190" y2="170" />

            <circle className="node" cx="140" cy="40" r="7" />
            <circle className="node amber" cx="60" cy="100" r="6" style={{ animationDelay: "0.4s" }} />
            <circle className="node" cx="220" cy="90" r="5" style={{ animationDelay: "0.8s" }} />
            <circle className="node" cx="140" cy="110" r="6" style={{ animationDelay: "1.2s" }} />
            <circle className="node amber" cx="90" cy="170" r="6" style={{ animationDelay: "1.6s" }} />
            <circle className="node" cx="190" cy="170" r="7" style={{ animationDelay: "2s" }} />
          </svg>
        </div>

        <div className="auth-brand-bottom">
          <div className="auth-tagline">Join the intelligence network.</div>
          <div className="auth-subtext">
            Create your profile as a researcher, startup founder, or innovation
            manager — and start discovering funding, trends and patents matched to you.
          </div>
        </div>
      </div>

      {/* RIGHT FORM PANEL */}
      <div className="auth-form-side">
        <div className="auth-card">
          <span className="auth-eyebrow">Get started</span>
          <h2 className="auth-title">Create your account</h2>
          <p className="auth-desc">
            Tell us who you are so we can tailor your dashboard.
          </p>

          <form className="auth-form" onSubmit={handleRegister}>
            <div className="field">
              <label>Full name</label>
              <input
                type="text"
                placeholder="Your name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
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
            <div className="field">
              <label>Password</label>
              <input
                type="password"
                placeholder="Create a password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label>I am a...</label>
              <select value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="researcher">Researcher</option>
                <option value="startup_founder">Startup Founder</option>
                <option value="innovation_manager">Innovation Manager</option>
              </select>
            </div>
            <button type="submit" className="auth-submit" disabled={isSubmitting}>
              {isSubmitting ? "Creating account..." : "Create Account"}
            </button>
          </form>

          <p className="auth-switch">
            Already have an account?{" "}
            <span onClick={onSwitchToLogin}>Login here</span>
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

export default Register;