import React, { useState, useRef } from "react";

const MCP_ENDPOINT = "http://localhost:8080/mcp/stream";

function App() {
  const [messages, setMessages] = useState([
    { sender: "agent", text: "Hello! How can I help you with your finances today?" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const agentMsgRef = useRef(null);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = { sender: "user", text: input };
    setMessages((msgs) => [...msgs, userMsg]);
    setInput("");
    setLoading(true);

    // Prepare request body
    const body = JSON.stringify({
      session_id: "test-session",
      input,
    });

    // Start streaming response
    let agentMsg = "";
    setMessages((msgs) => [...msgs, { sender: "agent", text: "" }]);
    try {
      const response = await fetch(MCP_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
      });
      if (!response.body) throw new Error("No response body");
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        if (value) {
          agentMsg += decoder.decode(value);
          setMessages((msgs) => {
            // Update last agent message
            const updated = [...msgs];
            updated[updated.length - 1] = { sender: "agent", text: agentMsg };
            return updated;
          });
        }
      }
    } catch (err) {
      setMessages((msgs) => [...msgs, { sender: "agent", text: "[Error: " + err.message + "]" }]);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded shadow p-4">
        <div className="mb-4 h-96 overflow-y-auto border rounded p-2 bg-gray-100">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={
                msg.sender === "user"
                  ? "text-right mb-2"
                  : "text-left mb-2"
              }
            >
              <span
                className={
                  msg.sender === "user"
                    ? "inline-block bg-blue-200 text-blue-900 px-3 py-2 rounded-lg"
                    : "inline-block bg-green-200 text-green-900 px-3 py-2 rounded-lg"
                }
              >
                {msg.text}
              </span>
            </div>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            className="flex-1 border rounded px-3 py-2"
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !loading) handleSend();
            }}
            placeholder="Type your message..."
            disabled={loading}
          />
          <button
            className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
            onClick={handleSend}
            disabled={loading}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
