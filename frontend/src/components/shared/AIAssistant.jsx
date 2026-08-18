import { useEffect, useRef, useState } from "react";
import { Bot, RotateCcw, Send, Sparkles, X } from "lucide-react";
import { askChatbot } from "../../api/chatbot";
import "../../styles/ai-assistant.css";

const WELCOME_MESSAGE = {
  role: "assistant",
  content:
    "Hi! I’m the InnovFund AI Assistant. Ask me how to use the platform, how to improve your profile, or any general question about research, innovation, startups, and funding.",
};

export default function AIAssistant() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([WELCOME_MESSAGE]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    inputRef.current?.focus();
  }, [messages, open]);

  async function sendMessage(event) {
    event?.preventDefault();

    const message = input.trim();
    if (!message || sending) return;

    const history = messages.slice(-10);
    const userMessage = { role: "user", content: message };

    setMessages((current) => [...current, userMessage]);
    setInput("");
    setError("");
    setSending(true);

    try {
      const answer = await askChatbot(message, history);
      setMessages((current) => [
        ...current,
        { role: "assistant", content: answer },
      ]);
    } catch (requestError) {
      const detail = requestError.response?.data?.detail;
      setError(
        detail ||
          "I couldn't reach the AI assistant right now. Please try again."
      );
    } finally {
      setSending(false);
    }
  }

  function clearConversation() {
    setMessages([WELCOME_MESSAGE]);
    setError("");
    setInput("");
  }

  return (
    <>
      {open && (
        <section className="ai-assistant-window" aria-label="InnovFund AI Assistant">
          <header className="ai-assistant-header">
            <div className="ai-assistant-title-wrap">
              <div className="ai-assistant-avatar">
                <Sparkles size={17} />
              </div>
              <div>
                <strong>InnovFund AI Assistant</strong>
                <span>Platform guidance &amp; general help</span>
              </div>
            </div>

            <div className="ai-assistant-header-actions">
              <button
                type="button"
                className="ai-assistant-icon-button"
                onClick={clearConversation}
                title="Clear conversation"
                aria-label="Clear conversation"
              >
                <RotateCcw size={16} />
              </button>
              <button
                type="button"
                className="ai-assistant-icon-button"
                onClick={() => setOpen(false)}
                title="Close assistant"
                aria-label="Close assistant"
              >
                <X size={18} />
              </button>
            </div>
          </header>

          <div className="ai-assistant-messages">
            {messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={`ai-assistant-message-row ${message.role}`}
              >
                {message.role === "assistant" && (
                  <span className="ai-assistant-message-avatar">
                    <Bot size={15} />
                  </span>
                )}
                <div className="ai-assistant-message-bubble">
                  {message.content}
                </div>
              </div>
            ))}

            {sending && (
              <div className="ai-assistant-message-row assistant">
                <span className="ai-assistant-message-avatar">
                  <Bot size={15} />
                </span>
                <div className="ai-assistant-message-bubble ai-assistant-typing">
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            )}

            {error && <div className="ai-assistant-error">{error}</div>}
            <div ref={messagesEndRef} />
          </div>

          <form className="ai-assistant-composer" onSubmit={sendMessage}>
            <input
              ref={inputRef}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask anything about InnovFund..."
              maxLength={4000}
              disabled={sending}
              aria-label="Ask the InnovFund AI Assistant"
            />
            <button
              type="submit"
              disabled={!input.trim() || sending}
              aria-label="Send message"
              title="Send message"
            >
              <Send size={17} />
            </button>
          </form>

          <div className="ai-assistant-footer">
            AI-generated guidance may be imperfect. Funding predictions are not guarantees.
          </div>
        </section>
      )}

      {!open && (
        <button
          type="button"
          className="ai-assistant-launcher"
          onClick={() => setOpen(true)}
          aria-label="Open InnovFund AI Assistant"
          title="Ask InnovFund AI Assistant"
        >
          <Sparkles size={21} />
          <span>AI Assistant</span>
        </button>
      )}
    </>
  );
}
