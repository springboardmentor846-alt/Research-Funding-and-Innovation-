import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  ArrowLeft,
  CheckCircle2,
  CircleGauge,
  FileText,
  Lightbulb,
  Target,
  TrendingUp,
} from "lucide-react";
import { getGrantPrediction } from "../../api/researcher/grantPrediction";

function GrantPrediction() {
  const { fundingId } = useParams();
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadPrediction() {
      setLoading(true);
      setError("");

      try {
        const data = await getGrantPrediction(fundingId);
        if (active) setPrediction(data);
      } catch (err) {
        console.error(err);
        if (active) {
          setPrediction(null);
          setError(
            err.response?.data?.detail ||
              "Unable to generate the grant prediction. Please try again."
          );
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    if (fundingId) {
      loadPrediction();
    } else {
      setLoading(false);
      setError("No funding opportunity was selected.");
    }

    return () => {
      active = false;
    };
  }, [fundingId]);

  if (loading) {
    return (
      <div className="research-prediction-page">
        <div className="research-prediction-header">
          <span className="research-prediction-eyebrow">AI INSIGHTS</span>
          <h1>Predict Grant Success</h1>
          <p>
            Match your research profile with funding opportunities and assess
            your current grant readiness before applying.
          </p>
        </div>

        <section className="research-prediction-panel research-prediction-loading">
          <div className="research-prediction-spinner" />
          <strong>Analyzing your research profile...</strong>
          <span>Calculating grant fit, innovation and profile signals.</span>
        </section>
      </div>
    );
  }

  if (!prediction) {
    return (
      <div className="research-prediction-page">
        <div className="research-prediction-header">
          <span className="research-prediction-eyebrow">AI INSIGHTS</span>
          <h1>Predict Grant Success</h1>
          <p>
            Match your research profile with funding opportunities and assess
            your current grant readiness before applying.
          </p>
        </div>
        <div className="research-prediction-alert">{error || "No prediction available."}</div>
      </div>
    );
  }

  const probability = Number(prediction.grant_probability ?? 0);
  const innovation = prediction.innovation_score ?? "—";
  const confidence = prediction.confidence ?? "—";
  const strengths = Array.isArray(prediction.strengths) ? prediction.strengths : [];
  const improvements = Array.isArray(prediction.improvements)
    ? prediction.improvements
    : [];
  const features = prediction.features || {};

  return (
    <div className="research-prediction-page">
      <div className="research-prediction-header">
        <span className="research-prediction-eyebrow">AI INSIGHTS</span>
        <h1>Predict Grant Success</h1>
        <p>
          Match your research profile with funding opportunities and assess
          your current grant readiness before applying.
        </p>
      </div>

      <section className="research-prediction-panel research-prediction-main-card">
        <Link to="/funding" className="research-prediction-back-link">
          <ArrowLeft size={16} />
          Back to funding matches
        </Link>

        <div className="research-prediction-title-row">
          <div>
            <span className="research-prediction-eyebrow">AI GRANT ASSESSMENT</span>
            <h2>{prediction.funding || "Selected funding opportunity"}</h2>
            <p>Research-to-opportunity matching and grant readiness estimate</p>
          </div>

          <div className="research-prediction-score-circle">
            <strong>{probability.toFixed(1)}%</strong>
            <span>estimated fit</span>
          </div>
        </div>

        <div className="research-prediction-metrics">
          <PredictionMetric
            icon={Target}
            title="Grant Probability"
            value={`${probability.toFixed(1)}%`}
          />
          <PredictionMetric
            icon={Lightbulb}
            title="Innovation Score"
            value={innovation}
          />
          <PredictionMetric
            icon={CheckCircle2}
            title="Confidence"
            value={confidence}
          />
        </div>

        <div className="research-prediction-note">
          <CircleGauge size={18} />
          <span>
            This estimate combines your research profile, innovation signals
            and funding fit. It is a decision-support estimate, not a
            guarantee of grant success.
          </span>
        </div>
      </section>

      <div className="research-prediction-two-column">
        <section className="research-prediction-panel research-prediction-list-card">
          <div className="research-prediction-card-heading">
            <div>
              <span className="research-prediction-eyebrow">WHAT IS WORKING</span>
              <h3>Strengths</h3>
            </div>
          </div>

          <div className="research-prediction-list">
            {strengths.length ? (
              strengths.map((item, index) => (
                <div className="research-prediction-list-item" key={index}>
                  <CheckCircle2 size={16} />
                  <span>{item}</span>
                </div>
              ))
            ) : (
              <div className="research-prediction-empty-item">
                No specific strengths were returned for this prediction.
              </div>
            )}
          </div>
        </section>

        <section className="research-prediction-panel research-prediction-list-card">
          <div className="research-prediction-card-heading">
            <div>
              <span className="research-prediction-eyebrow">NEXT STEPS</span>
              <h3>Areas to improve</h3>
            </div>
          </div>

          <div className="research-prediction-list">
            {improvements.length ? (
              improvements.map((item, index) => (
                <div className="research-prediction-list-item improvement" key={index}>
                  <TrendingUp size={16} />
                  <span>{item}</span>
                </div>
              ))
            ) : (
              <div className="research-prediction-empty-item">
                No specific improvements were returned for this prediction.
              </div>
            )}
          </div>
        </section>
      </div>

      <section className="research-prediction-panel research-prediction-features-card">
        <div className="research-prediction-card-heading">
          <div>
            <span className="research-prediction-eyebrow">PROFILE SIGNALS</span>
            <h3>Research Profile Used</h3>
            <p>Key profile features considered in this prediction.</p>
          </div>
        </div>

        <div className="research-prediction-feature-grid">
          <Feature icon={FileText} label="Publications" value={features.publications ?? 0} />
          <Feature icon={FileText} label="Patents" value={features.patents ?? 0} />
          <Feature icon={Target} label="Research Domains" value={features.domains ?? 0} />
          <Feature icon={Lightbulb} label="Keywords" value={features.keywords ?? 0} />
          <Feature icon={TrendingUp} label="Technology Areas" value={features.technology_areas ?? 0} />
        </div>
      </section>

      <p className="research-prediction-disclaimer">
        This prediction is based on your current research profile and the
        selected funding opportunity. It is intended to support funding
        decisions and does not guarantee grant approval.
      </p>
    </div>
  );
}

function PredictionMetric({ icon: Icon, title, value }) {
  return (
    <div className="research-prediction-metric">
      <Icon size={20} />
      <span>{title}</span>
      <strong>{value}</strong>
    </div>
  );
}

function Feature({ icon: Icon, label, value }) {
  return (
    <div className="research-prediction-feature">
      <Icon size={20} />
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export default GrantPrediction;
