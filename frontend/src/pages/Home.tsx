import "../index.css";
import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Loading from "./Loading";
import "bootstrap/dist/css/bootstrap.min.css";
// Navbar removed per design change (logo will be in sidebar)
import Card from "../components/Card";
import ReactMarkdown from "react-markdown";

interface ChatResponse {
  answer_md: string;
}

type MessageRole = "user" | "assistant";

interface ChatMessage {
  role: MessageRole;
  contentMd: string;
}

function Home() {
  const [loading, setLoading] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sending, setSending] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const messagesContainerRef = useRef<HTMLDivElement | null>(null);
  const navigate = useNavigate();

  // Split backend markdown into separate chat messages when it contains
  // multiple "Respuesta:" sections (e.g., out-of-domain notice + final answer)
  const splitAnswerSections = (markdown: string): string[] => {
    if (!markdown) return [];
    const chunks = markdown
      .split(/(?=^\s*Respuesta:\s*)/m)
      .map((s) => s.trim())
      .filter((s) => s.length > 0);
    return chunks.length > 0 ? chunks : [markdown];
  };

  useEffect(() => {
    setLoading(true);
    setTimeout(() => setLoading(false), 100);
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }, [messages]);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
    setInputValue(e.target.value);
  };

  const handleSend = async () => {
    const question = inputValue.trim();
    if (!question || sending) return;

    setSending(true);
    try {
      // 1) Agregar mensaje del usuario (derecha)
      setMessages((prev) => [
        ...prev,
        { role: "user", contentMd: question },
      ]);

      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      if (!res.ok) throw new Error("Error al comunicarse con el servicio RAG");

      const data: ChatResponse = await res.json();

      // 2) Agregar 1..n mensajes del asistente (izquierda)
      const sections = splitAnswerSections(data.answer_md);
      setMessages((prev) => [
        ...prev,
        ...sections.map((md) => ({ role: "assistant" as const, contentMd: md })),
      ]);
      setInputValue("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    } catch (err) {
      console.error(err);
      alert("Ocurrió un error al procesar tu pregunta.");
    } finally {
      setSending(false);
    }
  };

  // Permitir enviar con Enter y salto con Shift+Enter
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (loading) return <Loading />;

  return (
    <div className="container-fluid h-desktop-100vh overflow-hidden-desktop d-flex flex-column">

      <div className="row flex-grow-1 mt-3 min-h-0">
        {/* Sidebar izquierda */}
        <aside className="col-12 col-md-3 col-lg-2 border-end bg-light p-3 d-flex flex-column min-h-0">
          <div className="mb-3 d-flex justify-content-center">
            <img src="/src/assets/Logo.png" alt="HESOYAM" style={{ maxWidth: "140px", height: "auto" }} />
          </div>
          <h6 className="text-muted mb-3">Chats recientes</h6>
          <div className="flex-grow-1 overflow-auto">
            {["Exploración lunar", "IA en Marte", "Cultivos espaciales"].map(
              (chat, index) => (
                <div
                  key={index}
                  className="p-2 mb-2 rounded bg-white shadow-sm small text-truncate"
                  role="button"
                >
                  {chat}
                </div>
              )
            )}
          </div>
          <button className="btn btn-dark mt-3">+ Nuevo chat</button>
          <button
            className="btn btn-outline-primary mt-2"
            onClick={() => navigate("/nodes")}
          >
            📊 Ver Visualización
          </button>
        </aside>

        {/* Área principal */}
        <main className="col-12 col-md-9 col-lg-10 d-flex flex-column chat-container min-h-0">
          <div ref={messagesContainerRef} className="chat-messages p-3">
            {messages.length === 0 ? (
              <Card>
                <p className="text-muted mb-0">
                  Aquí aparecerán las respuestas...
                </p>
              </Card>
            ) : (
              messages.map((msg, index) => {
                const isUser = msg.role === "user";
                return (
                  <div key={index} className={`message-row ${isUser ? "user" : "assistant"}`}>
                    <div className={`message-bubble ${isUser ? "user" : "assistant"}`}>
                      {isUser ? (
                        <div className="markdown-body">
                          <ReactMarkdown>{msg.contentMd}</ReactMarkdown>
                        </div>
                      ) : (
                        <div className="markdown-body">
                          <ReactMarkdown>{msg.contentMd}</ReactMarkdown>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Área de texto (input) */}
          <div className="p-3 chat-input">
            <label
              htmlFor="exampleFormControlTextarea1"
              className="form-label text-muted mb-1"
            >
              Escribe tu pregunta...
            </label>
            <textarea
              ref={textareaRef}
              className="form-control"
              id="exampleFormControlTextarea1"
              value={inputValue}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Type your message here..."
              disabled={sending}
              style={{
                resize: "none",
                overflowY: "auto",
                maxHeight: "160px",
              }}
            />
            <div className="d-flex justify-content-end mt-2">
              <button
                className="btn btn-primary"
                onClick={handleSend}
                disabled={sending}
              >
                {sending ? "Enviando..." : "Enviar"}
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default Home;
