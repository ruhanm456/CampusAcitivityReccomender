import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";

type Message = {
  id: number;
  role: "user" | "assistant";
  text: string;
};

const SUGGESTED_PROMPTS = [
  "What clubs are active this week?",
  "Find study groups for CS classes",
  "What events are happening tonight?",
];

const ASSISTANT_RESPONSE =
  "Thanks for the question! I can help you find campus activities.";

const RESPONSE_DELAY_MS = 600;

const ChatWindow: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isSending, setIsSending] = useState(false);
  const timeoutRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (timeoutRef.current !== null) {
        window.clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const queueAssistantReply = () => {
    if (timeoutRef.current !== null) {
      window.clearTimeout(timeoutRef.current);
    }
    timeoutRef.current = window.setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          role: "assistant",
          text: ASSISTANT_RESPONSE,
        },
      ]);
      setIsSending(false);
    }, RESPONSE_DELAY_MS);
  };

  const sendMessage = (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || isSending) return;

    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        role: "user",
        text: trimmed,
      },
    ]);
    setInputValue("");
    setIsSending(true);
    queueAssistantReply();
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage(inputValue);
    }
  };

  const showEmptyState = messages.length === 0 && !isSending;

  return (
    <div className="flex h-full flex-col">
      <header className="navbar bg-base-200 rounded-box px-4">
        <div className="flex-1">
          <Link to="/" className="btn btn-ghost btn-sm">
            Back
          </Link>
        </div>
        <div className="flex-1 justify-center">
          <h1 className="text-lg font-semibold">Campus Chat</h1>
        </div>
        <div className="flex-1 justify-end" />
      </header>

      <main
        className="flex-1 min-h-0 overflow-y-auto px-4 py-3"
        role="log"
        aria-live="polite"
      >
        {showEmptyState ? (
          <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
            <p className="text-base-content/70">Ask about campus life...</p>
            <div className="flex flex-wrap justify-center gap-2">
              {SUGGESTED_PROMPTS.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  className="btn btn-outline btn-sm"
                  onClick={() => setInputValue(prompt)}
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`chat ${
                  message.role === "user" ? "chat-end" : "chat-start"
                }`}
              >
                <div
                  className={`chat-bubble ${
                    message.role === "user" ? "chat-bubble-primary" : ""
                  }`}
                >
                  {message.text}
                </div>
              </div>
            ))}
            {isSending ? (
              <div className="chat chat-start">
                <div className="chat-bubble">Typing...</div>
              </div>
            ) : null}
          </div>
        )}
      </main>

      <footer className="border-t border-base-200 bg-base-100 px-4 py-3">
        <div className="flex gap-2">
          <label className="sr-only" htmlFor="chat-input">
            Message
          </label>
          <textarea
            id="chat-input"
            className="textarea textarea-bordered w-full"
            rows={2}
            placeholder="Type your message..."
            value={inputValue}
            onChange={(event) => setInputValue(event.target.value)}
            onKeyDown={handleKeyDown}
            aria-label="Message"
          />
          <button
            type="button"
            className="btn btn-primary"
            disabled={!inputValue.trim() || isSending}
            onClick={() => sendMessage(inputValue)}
          >
            Send
          </button>
        </div>
        <p className="mt-2 text-xs text-base-content/70">
          Press Enter to send, Shift+Enter for a new line.
        </p>
      </footer>
    </div>
  );
};

export default ChatWindow;
