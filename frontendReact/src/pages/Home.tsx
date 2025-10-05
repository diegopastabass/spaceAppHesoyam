import "../index.css";
import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Loading from "./Loading";
import "bootstrap/dist/css/bootstrap.min.css";
import Navbar from "../components/Navbar";
import Card from "../components/Card";

interface RelatedDoc {
  title: string;
  score: number;
}

interface RagResponse {
  response: string;
  related_with: RelatedDoc[];
}

function Home() {
  const [loading, setLoading] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState<RagResponse[]>([]);
  const [sending, setSending] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    setLoading(true);
    setTimeout(() => setLoading(false), 100);
  }, []);

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
      const res = await fetch("http://localhost:8000/rag/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      if (!res.ok) throw new Error("Error al comunicarse con el servicio RAG");

      const data: RagResponse = await res.json();

      // Guardamos el mensaje recibido
      setMessages((prev) => [...prev, data]);
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
    <div className="container-fluid vh-100 d-flex flex-column">
      <Navbar />

      <div className="row flex-grow-1 mt-3">
        {/* Sidebar izquierda */}
        <aside className="col-12 col-md-3 col-lg-2 border-end bg-light p-3 d-flex flex-column">
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
        <main className="col-12 col-md-9 col-lg-10 d-flex flex-column">
          <div className="flex-grow-1 overflow-auto p-3">
            {messages.length === 0 ? (
              <Card>
                <p className="text-muted mb-0">
                  Aquí aparecerán las respuestas...
                </p>
              </Card>
            ) : (
              messages.map((msg, index) => (
                <Card key={index}>
                  <p className="fw-bold text-primary">Respuesta:</p>
                  <p>{msg.response}</p>
                  {msg.related_with?.length > 0 && (
                    <>
                      <hr />
                      <p className="fw-bold small text-muted mb-2">
                        Relacionado con:
                      </p>
                      <ul className="list-unstyled small">
                        {msg.related_with.map((doc, i) => (
                          <li key={i}>
                            📄 {doc.title}{" "}
                            <span className="text-muted">
                              ({(doc.score * 100).toFixed(1)}%)
                            </span>
                          </li>
                        ))}
                      </ul>
                    </>
                  )}
                </Card>
              ))
            )}
          </div>

          {/* Área de texto (input) */}
          <div className="p-3 border-top bg-white">
            <label
              htmlFor="exampleFormControlTextarea1"
              className="form-label text-muted mb-1"
            >
              Ask Something...
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
                overflow: "hidden",
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
