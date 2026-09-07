import { useState, useRef, useEffect } from "react";
import axios from "axios";

function VaniIcon({ size = 26 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 48 48" fill="none">
      <circle cx="24" cy="24" r="22" fill="none" />
      <rect x="10" y="14" width="28" height="22" rx="9" fill="#fff" />
      <circle cx="24" cy="8" r="3" fill="#fff" />
      <line x1="24" y1="11" x2="24" y2="14" stroke="#fff" strokeWidth="2" />
      <circle cx="18" cy="24" r="2.6" fill="#131B34" />
      <circle cx="30" cy="24" r="2.6" fill="#131B34" />
      <path d="M18 30c2.5 1.8 9.5 1.8 12 0" stroke="#131B34" strokeWidth="2" strokeLinecap="round" fill="none" />
    </svg>
  );
}

function MicIcon({ active }) {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={active ? "#fff" : "currentColor"} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="9" y="2" width="6" height="12" rx="3" />
      <path d="M5 10v1a7 7 0 0 0 14 0v-1" />
      <line x1="12" y1="18" x2="12" y2="22" />
      <line x1="8" y1="22" x2="16" y2="22" />
    </svg>
  );
}

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const voiceSupported = !!SpeechRecognition;
const ttsSupported = "speechSynthesis" in window;

function AIAssistant({ token }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hi, I'm Vani — your research assistant. Ask me anything about this platform, your profile, or funding opportunities." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [listening, setListening] = useState(false);
  const [speakEnabled, setSpeakEnabled] = useState(true);
  const [wasVoiceInput, setWasVoiceInput] = useState(false);
  const bottomRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    if (open) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, open]);

  useEffect(() => {
    if (!voiceSupported) return;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput((prev) => (prev ? prev + " " + transcript : transcript));
      setWasVoiceInput(true);
    };
    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);

    recognitionRef.current = recognition;
  }, []);

  const toggleListening = () => {
    if (!voiceSupported) return;
    if (listening) {
      recognitionRef.current.stop();
      setListening(false);
    } else {
      recognitionRef.current.start();
      setListening(true);
    }
  };

  const speak = (text) => {
    if (!ttsSupported || !speakEnabled) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1;
    utterance.pitch = 1.05;

    const voices = window.speechSynthesis.getVoices();
    const femaleVoice =
      voices.find((v) => v.lang.startsWith("en") && /female|zira|samantha|susan|karen|victoria/i.test(v.name)) ||
      voices.find((v) => v.lang.startsWith("en"));
    if (femaleVoice) utterance.voice = femaleVoice;

    window.speechSynthesis.speak(utterance);
  };

  const handleSend = async (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    const nextMessages = [...messages, { role: "user", content: trimmed }];
    setMessages(nextMessages);
    setInput("");
    setError("");
    setLoading(true);

    try {
      const history = nextMessages.slice(-4).map((m) => ({ role: m.role, content: m.content }));
      const response = await axios.post(
        "http://127.0.0.1:8000/api/v1/chatbot/ask",
        { message: trimmed, history },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessages((prev) => [...prev, { role: "assistant", content: response.data.answer }]);
      if (wasVoiceInput) {
        speak(response.data.answer);
      }
      setWasVoiceInput(false);
    } catch (err) {
      if (err.response?.status === 503) {
        setError("Vani isn't configured yet — a GEMINI_API_KEY is needed on the server.");
      } else {
        setError(err.response?.data?.detail || "Could not reach Vani. Please try again.");
      }
    }
    setLoading(false);
  };

  return (
    <>
      <button className="ai-fab" onClick={() => setOpen((v) => !v)} aria-label="Open Vani, your AI assistant">
        {open ? <span className="ai-fab-close">×</span> : <VaniIcon />}
      </button>

      {open && (
        <div className="ai-panel">
          <div className="ai-panel-header">
            <div className="ai-panel-avatar">
              <VaniIcon size={18} />
            </div>
            <div style={{ flex: 1 }}>
              <div className="ai-panel-title">Vani</div>
              <div className="ai-panel-subtitle">Research Assistant</div>
            </div>
            {ttsSupported && (
              <button
                type="button"
                onClick={() => setSpeakEnabled((v) => !v)}
                className="ai-mute-btn"
                aria-label={speakEnabled ? "Mute Vani's voice" : "Unmute Vani's voice"}
                title={speakEnabled ? "Voice on" : "Voice off"}
              >
                {speakEnabled ? "🔊" : "🔇"}
              </button>
            )}
          </div>

          <div className="ai-messages">
            {messages.map((m, idx) => (
              <div key={idx} className={`ai-bubble ${m.role === "user" ? "ai-bubble-user" : "ai-bubble-assistant"}`}>
                {m.content}
              </div>
            ))}
            {loading && (
              <div className="ai-bubble ai-bubble-assistant ai-typing">
                <span className="ai-dot"></span>
                <span className="ai-dot"></span>
                <span className="ai-dot"></span>
              </div>
            )}
            {error && <div className="ai-status ai-status-error">{error}</div>}
            <div ref={bottomRef} />
          </div>

          <form onSubmit={handleSend} className="ai-form">
            {voiceSupported && (
              <button
                type="button"
                onClick={toggleListening}
                className={`ai-mic-btn ${listening ? "ai-mic-btn-active" : ""}`}
                aria-label={listening ? "Stop listening" : "Speak your question"}
                title={listening ? "Listening... click to stop" : "Click to speak"}
              >
                <MicIcon active={listening} />
              </button>
            )}
            <input
              type="text"
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                setWasVoiceInput(false);
              }}
              placeholder={listening ? "Listening..." : "Ask Vani a question..."}
              className="ai-input"
            />
            <button type="submit" disabled={loading} className="ai-send-btn">
              Send
            </button>
          </form>
        </div>
      )}
    </>
  );
}

export default AIAssistant;