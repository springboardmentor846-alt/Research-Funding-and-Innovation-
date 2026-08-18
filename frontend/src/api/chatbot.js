import api from "./axios";

export async function askChatbot(message, history = []) {
  const response = await api.post("/api/chatbot/ask", {
    message,
    history: history.slice(-10).map((item) => ({
      role: item.role === "assistant" ? "assistant" : "user",
      content: item.content,
    })),
  });

  return response.data.answer;
}
