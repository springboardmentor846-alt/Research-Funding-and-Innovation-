import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  getStartupProfile,
  createStartupProfile,
  updateStartupProfile,
} from "../../api/startup/profile";

function StartupProfile() {

  const [profileExists, setProfileExists] =
    useState(false);

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [message, setMessage] =
    useState("");

  const [formData, setFormData] =
    useState({

      startup_name: "",
      tagline: "",

      industry: "",
      stage: "Idea",

      founded_year: "",

      funding_stage: "Bootstrapped",

      startup_email: "",
      phone_number: "",

      website: "",
      linkedin_url: "",

      location: "",

      description: "",

      technology_stack: "",
      research_interests: "",



      team_size: 1,

    });

  useEffect(() => {
    fetchProfile();
  }, []);

  async function fetchProfile() {

    try {

      const response =
        await getStartupProfile();

      setFormData(response);

      setProfileExists(true);

    }

    catch {

      setProfileExists(false);

    }

    finally {

      setLoading(false);

    }

  }

  function handleChange(event) {

    setFormData({

      ...formData,

      [event.target.name]:
      event.target.value,

    });

  }

  async function handleSubmit(event) {

    event.preventDefault();

    try {

      setSaving(true);

      setMessage("");

      if (profileExists) {

        await updateStartupProfile(
          formData
        );

        setMessage(
          "Startup profile updated successfully."
        );

      }

      else {

        await createStartupProfile(
          formData
        );

        setProfileExists(true);

        setMessage(
          "Startup profile created successfully."
        );

      }

    }

    catch {

      setMessage(
        "Failed to save startup profile."
      );

    }

    finally {

      setSaving(false);

    }

  }

  if (loading) {

    return (

      <div className="module-loading">

        <div className="spinner-border text-primary" />

        <span>

          Loading startup profile...

        </span>

      </div>

    );

  }

  return (

    <div className="module-page">

      <div className="module-page-header">

        <div>

          <span className="module-eyebrow">

            STARTUP MANAGEMENT

          </span>

          <h1>

            Startup Profile

          </h1>

          <p>

            Build your startup identity, discover
            researchers and connect with funding
            opportunities.

          </p>

        </div>

        <div
          className={`record-status ${
            profileExists
              ? "complete"
              : "incomplete"
          }`}
        >

          <span className="record-status-dot"></span>

          {
            profileExists
              ? "Profile Created"
              : "Profile Not Created"
          }

        </div>

      </div>

      {

        message &&

        <div className="module-alert">

          {message}

        </div>

      }

      {/* Quick Cards */}

      <div className="module-content-grid mb-4">

        <Link
          to="/startup/researchers"
          className="module-card"
        >

          <div className="module-icon">

            👨‍🔬

          </div>

          <div className="module-card-content">

            <h3>

              Find Researchers

            </h3>

            <p>

              Discover researchers suitable
              for your startup.

            </p>

          </div>

        </Link>

        <Link
          to="/startup/requests"
          className="module-card"
        >

          <div className="module-icon">

            🤝

          </div>

          <div className="module-card-content">

            <h3>

              Collaboration Requests

            </h3>

            <p>

              Manage collaboration invitations.

            </p>

          </div>

        </Link>

        <Link
          to="/startup/funding"
          className="module-card"
        >

          <div className="module-icon">

            💰

          </div>

          <div className="module-card-content">

            <h3>

              Funding Opportunities

            </h3>

            <p>

              Explore grants and startup funding.

            </p>

          </div>

        </Link>

        <Link
          to="/startup/innovation-score"
          className="module-card"
        >

          <div className="module-icon">

            ⭐

          </div>

          <div className="module-card-content">

            <h3>

              Innovation Score

            </h3>

            <p>

              View AI-powered innovation insights.

            </p>

          </div>

        </Link>

      </div>

      <div className="module-content-grid">

        <div className="professional-form-card">

          <div className="form-card-header">

            <div>

              <h2>

                Startup Information

              </h2>

              <p>

                Maintain your startup identity
                and organization details.

              </p>

            </div>

          </div>

          <form onSubmit={handleSubmit}>
            <div className="form-section">

  <div className="form-section-title">

    Startup Details

  </div>

  <div className="professional-form-grid">

    <div className="professional-field">

      <label>

        Startup Name

      </label>

      <input
        type="text"
        name="startup_name"
        placeholder="Example: InnovAI Labs"
        value={formData.startup_name}
        onChange={handleChange}
      />

    </div>

    <div className="professional-field">

      <label>

        Tagline

      </label>

      <input
        type="text"
        name="tagline"
        placeholder="One line about your startup"
        value={formData.tagline}
        onChange={handleChange}
      />

    </div>

    <div className="professional-field">

      <label>

        Industry

      </label>

      <input
        type="text"
        name="industry"
        placeholder="AI, Healthcare, FinTech..."
        value={formData.industry}
        onChange={handleChange}
      />

    </div>

    <div className="professional-field">

      <label>

        Startup Stage

      </label>

      <select
        name="stage"
        value={formData.stage}
        onChange={handleChange}
      >

        <option>Idea</option>
        <option>MVP</option>
        <option>Prototype</option>
        <option>Seed</option>
        <option>Series A</option>
        <option>Growth</option>

      </select>

    </div>

    <div className="professional-field">

      <label>

        Founded Year

      </label>

      <input
        type="number"
        name="founded_year"
        placeholder="2025"
        value={formData.founded_year}
        onChange={handleChange}
      />

    </div>

    <div className="professional-field">

      <label>

        Funding Stage

      </label>

      <select
        name="funding_stage"
        value={formData.funding_stage}
        onChange={handleChange}
      >

        <option>Bootstrapped</option>
        <option>Angel</option>
        <option>Seed</option>
        <option>Series A</option>
        <option>Series B</option>

      </select>

    </div>

  </div>

</div>

<div className="form-section">

  <div className="form-section-title">

    Contact Information

  </div>

  <div className="professional-form-grid">

    <div className="professional-field">

      <label>Email</label>

      <input
        type="email"
        name="startup_email"
        value={formData.startup_email}
        onChange={handleChange}
      />

    </div>

    <div className="professional-field">

      <label>Phone</label>

      <input
        type="text"
        name="phone_number"
        value={formData.phone_number}
        onChange={handleChange}
      />

    </div>

    <div className="professional-field">

      <label>Website</label>

      <input
        type="text"
        name="website"
        value={formData.website}
        onChange={handleChange}
      />

    </div>

    <div className="professional-field">

      <label>LinkedIn</label>

      <input
        type="text"
        name="linkedin_url"
        value={formData.linkedin_url}
        onChange={handleChange}
      />

    </div>

    <div className="professional-field professional-field-full">

      <label>Location</label>

      <input
        type="text"
        name="location"
        value={formData.location}
        onChange={handleChange}
      />

    </div>

  </div>

</div>

<div className="form-section">

  <div className="professional-field">

    <label>

      Startup Description

    </label>

    <textarea
      rows="6"
      name="description"
      placeholder="Describe your startup, problem statement, solution and vision..."
      value={formData.description}
      onChange={handleChange}
    />

    <span className="field-help">

      Briefly explain what your startup does.

    </span>

  </div>

</div>

<div className="form-section">

  <div className="form-section-title">

    Innovation & Collaboration

  </div>

  <div className="professional-form-grid">

    <div className="professional-field">

      <label>

        Technology Stack

      </label>

      <input
        type="text"
        name="technology_stack"
        value={formData.technology_stack}
        onChange={handleChange}
      />

    </div>

    <div className="professional-field">

      <label>

        Innovation Area

      </label>

      <input
        type="text"
        name="research_interests"
        value={formData.research_interests}
        onChange={handleChange}
      />

    </div>

    <div className="professional-field">

      <label>

        Team Size

      </label>

      <input
        type="number"
        name="team_size"
        value={formData.team_size}
        onChange={handleChange}
      />

    </div>


  </div>

</div>
            <div className="professional-form-actions">

              <button
                type="submit"
                className="primary-action-btn"
                disabled={saving}
              >

                {
                  saving
                    ? "Saving..."
                    : profileExists
                      ? "Save Changes"
                      : "Create Profile"
                }

              </button>

            </div>

          </form>

        </div>

        <aside className="profile-guidance-card">

          <div className="guidance-icon">

            🚀

          </div>

          <h3>

            Why complete your startup profile?

          </h3>

          <p>

            A complete startup profile improves collaboration,
            researcher recommendations, funding opportunities
            and AI-powered innovation analysis.

          </p>

          <div className="guidance-list">

            <div>

              <span>01</span>

              Find researchers matching your technology.

            </div>

            <div>

              <span>02</span>

              Receive relevant funding recommendations.

            </div>

            <div>

              <span>03</span>

              Improve collaboration opportunities.

            </div>

            <div>

              <span>04</span>

              Generate your Innovation Score.

            </div>

          </div>

        </aside>

      </div>

    </div>

  );

}

export default StartupProfile;