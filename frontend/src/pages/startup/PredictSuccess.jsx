import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  Sparkles,
  Target,
  TrendingUp,
} from "lucide-react";
import { predictStartupSuccess } from "../../api/startup";

export default function PredictSuccess() {
  const { fundingId } = useParams();
  const navigate = useNavigate();
  const [prediction, setPrediction] = useState(null);
  const [predicting, setPredicting] = useState(false);
  const [message, setMessage] = useState("");

  // Prediction is only meaningful after the user selects an opportunity
  // from the Funding Opportunities page. Do not load/show opportunities here.
  useEffect(() => {
    if (!fundingId) {
      navigate("/startup/funding", { replace: true });
    }
  }, [fundingId, navigate]);

  useEffect(() => {
    if (!fundingId) return;

    let mounted = true;
    setPredicting(true);
    setPrediction(null);
    setMessage("");

    predictStartupSuccess(decodeURIComponent(fundingId))
      .then((data) => {
        if (mounted) setPrediction(data);
      })
      .catch((error) => {
        if (mounted) {
          setPrediction(null);
          setMessage(
            error.response?.data?.detail ||
              "Unable to generate the startup funding estimate."
          );
        }
      })
      .finally(() => {
        if (mounted) setPredicting(false);
      });

    return () => {
      mounted = false;
    };
  }, [fundingId]);

  if (!fundingId) return null;

  return (
    <div className="startup-page">
      <div className="startup-page-header">
        <span className="startup-eyebrow">AI INSIGHTS</span>
        <h1>Predict Funding Success</h1>
        <p>
          Match your startup profile with the selected funding opportunity and
          assess your current readiness before applying.
        </p>
      </div>

      {message && <div className="startup-alert">{message}</div>}

      <PredictionResult
        prediction={prediction}
        predicting={predicting}
      />
    </div>
  );
}

function PredictionResult({ prediction, predicting }) {
  if (predicting) {
    return (
      <section className="startup-panel startup-prediction-panel">
        <div className="startup-loading">
          Analyzing startup and funding fit...
        </div>
      </section>
    );
  }

  if (!prediction) return null;

  return (
    <>
      <section className="startup-panel startup-prediction-panel">
        <Link to="/startup/funding" className="startup-back-link">
          <ArrowLeft size={16} />
          Back to funding opportunities
        </Link>

        <div className="startup-prediction-header">
          <div>
            <span className="startup-eyebrow">AI FUNDING ASSESSMENT</span>
            <h2>{prediction.funding}</h2>
            <p>
              Startup-to-opportunity matching and funding readiness estimate
            </p>
          </div>

          <div className="startup-score-circle">
            <strong>{prediction.success_estimate}%</strong>
            <span>estimated fit</span>
          </div>
        </div>

        <div className="startup-prediction-grid">
          <Metric
            icon={Target}
            title="Profile Match"
            value={`${prediction.match_score}%`}
          />
          <Metric
            icon={TrendingUp}
            title="Readiness"
            value={`${prediction.readiness_score}%`}
          />
          <Metric
            icon={CheckCircle2}
            title="Profile Completion"
            value={`${prediction.profile_completion}%`}
          />
        </div>

        <div className="startup-prediction-note">
          <Sparkles size={18} />
          <span>{prediction.summary}</span>
        </div>
      </section>

      <div className="startup-prediction-columns">
        <section className="startup-panel startup-prediction-list-panel">
          <div className="startup-panel-heading">
            <span className="startup-eyebrow">WHAT IS WORKING</span>
            <h2>Strengths</h2>
          </div>
          <div className="startup-prediction-list">
            {(prediction.strengths || []).length ? (
              prediction.strengths.map((item, index) => (
                <div className="startup-prediction-list-item" key={index}>
                  <CheckCircle2 size={18} />
                  <span>{item}</span>
                </div>
              ))
            ) : (
              <div className="startup-prediction-list-item">
                <span>No strengths identified yet.</span>
              </div>
            )}
          </div>
        </section>

        <section className="startup-panel startup-prediction-list-panel">
          <div className="startup-panel-heading">
            <span className="startup-eyebrow">NEXT STEPS</span>
            <h2>Areas to improve</h2>
          </div>
          <div className="startup-prediction-list">
            {(prediction.improvements || []).length ? (
              prediction.improvements.map((item, index) => (
                <div
                  className="startup-prediction-list-item improvement"
                  key={index}
                >
                  <AlertCircle size={18} />
                  <span>{item}</span>
                </div>
              ))
            ) : (
              <div className="startup-prediction-list-item">
                <span>No major improvement areas identified.</span>
              </div>
            )}
          </div>
        </section>
      </div>

      <p className="startup-disclaimer startup-prediction-disclaimer">
        This is a decision-support estimate based on your current startup
        profile and the selected opportunity. It is not a guarantee of funding
        success.
      </p>
    </>
  );
}

function Metric({ icon: Icon, title, value }) {
  return (
    <div className="startup-metric">
      <Icon size={22} />
      <span>{title}</span>
      <strong>{value}</strong>
    </div>
  );
}
