import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axios";

function Login() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value,
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      setLoading(true);
      setMessage("");

      const response = await api.post(
        "/auth/login",
        formData
      );

      localStorage.setItem(
        "access_token",
        response.data.access_token
      );

      navigate("/dashboard");
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Unable to sign in. Please check your credentials."
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
              INNOVATION INTELLIGENCE
            </span>

            <h1>
              Turn research potential into
              <span> meaningful opportunity.</span>
            </h1>

            <p>
              Build a structured research identity, organize
              scholarly outputs, and prepare for intelligent
              funding discovery workflows.
            </p>
          </div>

          <div className="auth-feature-list">
            <div className="auth-feature-item">
              <span className="auth-feature-number">
                01
              </span>

              <div>
                <strong>Research Intelligence</strong>
                <p>
                  Structure domains, keywords and technical
                  expertise in one workspace.
                </p>
              </div>
            </div>

            <div className="auth-feature-item">
              <span className="auth-feature-number">
                02
              </span>

              <div>
                <strong>Innovation Records</strong>
                <p>
                  Maintain publications, patents and
                  institutional research information.
                </p>
              </div>
            </div>

            <div className="auth-feature-item">
              <span className="auth-feature-number">
                03
              </span>

              <div>
                <strong>Funding Readiness</strong>
                <p>
                  Build structured data for future opportunity
                  matching and recommendations.
                </p>
              </div>
            </div>
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
              SECURE WORKSPACE
            </span>

            <h2>Welcome back</h2>

            <p>
              Sign in to continue to your researcher workspace.
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
                  name="email"
                  placeholder="name@organization.com"
                  value={formData.email}
                  onChange={handleChange}
                  autoComplete="email"
                  required
                />
              </div>
            </div>

            <div className="auth-field">
              <div className="auth-label-row">
                <label htmlFor="password">
                  Password
                </label>
              </div>

              <div className="auth-input-wrapper">
                <span className="auth-input-symbol">
                  •
                </span>

                <input
                  id="password"
                  type="password"
                  name="password"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={handleChange}
                  autoComplete="current-password"
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
                {loading
                  ? "Signing in..."
                  : "Sign in to workspace"}
              </span>

              {!loading && (
                <span className="auth-button-arrow">
                  →
                </span>
              )}
            </button>
          </form>

          <div className="auth-divider">
            <span>New to the platform?</span>
          </div>

          <Link
            to="/register"
            className="auth-secondary-link"
          >
            Create researcher account
          </Link>

          <p className="auth-security-note">
            Protected access to your research and innovation
            workspace.
          </p>
        </div>
      </main>
    </div>
  );
}

export default Login;