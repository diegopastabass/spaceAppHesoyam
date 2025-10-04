import "../index.css";
import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Loading from "./Loading";
import "bootstrap/dist/css/bootstrap.min.css";
import Navbar from "../components/Navbar";
import Card from "../components/Card";

function Home() {
  const [loading, setLoading] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    setLoading(true);
    setTimeout(() => setLoading(false), 1500);
  }, []);

  // Ajusta automáticamente la altura del textarea
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto"; // resetear altura
      textarea.style.height = `${textarea.scrollHeight}px`; // ajustar a contenido
    }
    setInputValue(e.target.value);
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
            onClick={() => navigate('/nodes')}
          >
            📊 Ver Visualización
          </button>
        </aside>

        {/* Área principal */}
        <main className="col-12 col-md-9 col-lg-10 d-flex flex-column">
          <div className="flex-grow-1 overflow-auto p-3">
            <Card>
              <p className="text-muted mb-0">
                Aquí aparecerán las respuestas...
              </p>
            </Card>
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
              placeholder="Type your message here..."
              style={{
                resize: "none",
                overflow: "hidden",
              }}
            />
          </div>
        </main>
      </div>
    </div>
  );
}

export default Home;
