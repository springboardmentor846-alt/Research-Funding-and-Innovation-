import { useState } from "react";
import axios from "axios";
import "./Login.css";

function Login({ onLoginSuccess, onSwitchToRegister }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [token, setToken] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setMessage("");

    try {
      const response = await axios.post("http://127.0.0.1:8000/api/v1/auth/login", {
        email: email,
        password: password,
      });

      setToken(response.data.access_token);
      setMessage("Login successful!");
      onLoginSuccess(response.data.access_token);
    } catch (error) {
      if (error.response) {
        setMessage(error.response.data.detail || "Login failed");
      } else {
        setMessage("Could not connect to server");
      }
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
          <div className="auth-tagline">Where research meets opportunity.</div>
          <div className="auth-subtext">
            Built for researchers, startups, universities and innovation teams —
            discover funding, analyze research trends, evaluate patent landscapes,
            and get AI-powered commercialization recommendations.
          </div>
        </div>
      </div>

      {/* RIGHT FORM PANEL */}
      <div className="auth-form-side">
        <div className="auth-card">
          <span className="auth-eyebrow">Welcome back</span>
          <h2 className="auth-title">Sign in to your dashboard</h2>
          <p className="auth-desc">
            Funding recommendations, research trends and patent insights — tailored to your role.
          </p>

          <form className="auth-form" onSubmit={handleLogin}>
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
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="auth-submit">
              Sign In
            </button>
          </form>

          <p className="auth-switch">
            Don't have an account?{" "}
            <span onClick={onSwitchToRegister}>Register here</span>
          </p>

          {message && <p className="auth-message">{message}</p>}

          {token && (
            <div className="auth-token">
              <strong>Token:</strong> {token}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Login;
