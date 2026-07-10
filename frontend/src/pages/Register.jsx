import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axios";

function Register() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    full_name: "",
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

      await api.post(
        "/auth/register",
        formData
      );

      navigate("/login");
    } catch (error) {
      const detail = error.response?.data?.detail;

      if (Array.isArray(detail)) {
        setMessage(
          detail
            .map((item) => item.msg)
            .join(" ")
        );
      } else {
        setMessage(
          detail ||
            "Unable to create account. Please try again."
        );
      }
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
              RESEARCHER ONBOARDING
            </span>

            <h1>
              Build the foundation for
              <span> intelligent discovery.</span>
            </h1>

            <p>
              Create your workspace and begin structuring
              the research, technology, publication, patent,
              and institutional information needed for future
              innovation intelligence.
            </p>
          </div>

          <div className="auth-feature-list">
            <div className="auth-feature-item">
              <span className="auth-feature-number">
                01
              </span>

              <div>
                <strong>Structured Identity</strong>
                <p>
                  Build a consistent academic and professional
                  research profile.
                </p>
              </div>
            </div>

            <div className="auth-feature-item">
              <span className="auth-feature-number">
                02
              </span>

              <div>
                <strong>Research Portfolio</strong>
                <p>
                  Organize domains, keywords, publications,
                  patents, and technology expertise.
                </p>
              </div>
            </div>

            <div className="auth-feature-item">
              <span className="auth-feature-number">
                03
              </span>

              <div>
                <strong>Opportunity Readiness</strong>
                <p>
                  Prepare structured information for future
                  funding and collaboration workflows.
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
              CREATE WORKSPACE
            </span>

            <h2>Create your account</h2>

            <p>
              Start building your structured research and
              innovation profile.
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
              <label htmlFor="full_name">
                Full name
              </label>

              <div className="auth-input-wrapper">
                <span className="auth-input-symbol">
                  N
                </span>

                <input
                  id="full_name"
                  type="text"
                  name="full_name"
                  placeholder="Enter your full name"
                  value={formData.full_name}
                  onChange={handleChange}
                  autoComplete="name"
                  minLength="2"
                  required
                />
              </div>
            </div>

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
              <label htmlFor="password">
                Password
              </label>

              <div className="auth-input-wrapper">
                <span className="auth-input-symbol">
                  •
                </span>

                <input
                  id="password"
                  type="password"
                  name="password"
                  placeholder="Create a secure password"
                  value={formData.password}
                  onChange={handleChange}
                  autoComplete="new-password"
                  minLength="8"
                  required
                />
              </div>

              <span className="auth-field-help">
                Use at least 8 characters.
              </span>
            </div>

            <button
              type="submit"
              className="auth-submit-btn"
              disabled={loading}
            >
              <span>
                {loading
                  ? "Creating account..."
                  : "Create researcher account"}
              </span>

              {!loading && (
                <span className="auth-button-arrow">
                  →
                </span>
              )}
            </button>
          </form>

          <div className="auth-divider">
            <span>Already registered?</span>
          </div>

          <Link
            to="/login"
            className="auth-secondary-link"
          >
            Sign in to existing account
          </Link>

          <p className="auth-security-note">
            Your account provides protected access to your
            research and innovation workspace.
          </p>
        </div>
      </main>
    </div>
  );
}

export default Register;