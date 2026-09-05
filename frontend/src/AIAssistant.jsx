import { useState, useRef, useEffect } from "react";
import axios from "axios";

function AIAssistant({ token }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hi! I'm your AI Assistant. Ask me anything about using this platform, your research profile, or funding opportunities." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    if (open) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, open]);

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
      const history = nextMessages.slice(-10).map((m) => ({ role: m.role, content: m.content }));
      const response = await axios.post(
        "http://127.0.0.1:8000/api/v1/chatbot/ask",
        { message: trimmed, history },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessages((prev) => [...prev, { role: "assistant", content: response.data.answer }]);
    } catch (err) {
      if (err.response?.status === 503) {
        setError("The AI Assistant isn't configured yet — a GEMINI_API_KEY is needed on the server.");
      } else {
        setError(err.response?.data?.detail || "Could not reach the AI Assistant. Please try again.");
      }
    }
    setLoading(false);
  };

  return (
    <>
      <button
        onClick={() => setOpen((v) => !v)}
        style={{
          position: "fixed",
          bottom: "24px",
          right: "24px",
          width: "56px",
          height: "56px",
          borderRadius: "50%",
          background: "#1C8C7A",
          color: "#fff",
          border: "none",
          fontSize: "22px",
          cursor: "pointer",
          boxShadow: "0 4px 14px rgba(0,0,0,0.25)",
          zIndex: 1000,
        }}
        aria-label="Open AI Assistant"
      >
        {open ? (
          <span style={{ fontSize: "22px", lineHeight: 1 }}>×</span>
        ) : (
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <rect x="4" y="7" width="16" height="12" rx="3" />
            <path d="M9 3v3M15 3v3" />
            <circle cx="9" cy="13" r="1.3" fill="currentColor" stroke="none" />
            <circle cx="15" cy="13" r="1.3" fill="currentColor" stroke="none" />
            <path d="M9.5 16.5c1.5 1 3.5 1 5 0" />
          </svg>
        )}
      </button>

      {open && (
        <div
          style={{
            position: "fixed",
            bottom: "90px",
            right: "24px",
            width: "340px",
            maxWidth: "90vw",
            height: "440px",
            background: "#fff",
            borderRadius: "12px",
            boxShadow: "0 8px 30px rgba(0,0,0,0.25)",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            zIndex: 1000,
          }}
        >
          <div style={{ background: "#0F1B2D", color: "#fff", padding: "12px 16px", fontWeight: 600, fontSize: "14px" }}>
            AI Assistant
          </div>

          <div style={{ flex: 1, overflowY: "auto", padding: "12px", display: "flex", flexDirection: "column", gap: "10px" }}>
            {messages.map((m, idx) => (
              <div
                key={idx}
                style={{
                  alignSelf: m.role === "user" ? "flex-end" : "flex-start",
                  background: m.role === "user" ? "#1C8C7A" : "#f1f3f5",
                  color: m.role === "user" ? "#fff" : "#1a1a1a",
                  padding: "8px 12px",
                  borderRadius: "10px",
                  fontSize: "13px",
                  maxWidth: "85%",
                  whiteSpace: "pre-wrap",
                }}
              >
                {m.content}
              </div>
            ))}
            {loading && (
              <div style={{ alignSelf: "flex-start", color: "#888", fontSize: "12.5px" }}>
                Thinking...
              </div>
            )}
            {error && (
              <div style={{ alignSelf: "flex-start", color: "#B3261E", fontSize: "12.5px" }}>
                {error}
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <form onSubmit={handleSend} style={{ display: "flex", borderTop: "1px solid #eee" }}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question..."
              style={{
                flex: 1,
                border: "none",
                padding: "10px 12px",
                fontSize: "13px",
                outline: "none",
              }}
            />
            <button
              type="submit"
              disabled={loading}
              style={{
                border: "none",
                background: "#1C8C7A",
                color: "#fff",
                padding: "0 16px",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              Send
            </button>
          </form>
        </div>
      )}
    </>
  );
}

export default AIAssistant;