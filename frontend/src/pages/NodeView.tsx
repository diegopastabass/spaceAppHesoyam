import React from 'react';
import { useNavigate } from 'react-router-dom';
import NodeVisualization from '../components/NodeVisualization';
import Navbar from '../components/Navbar';
import '../index.css';
import 'bootstrap/dist/css/bootstrap.min.css';

const NodeView: React.FC = () => {
  const navigate = useNavigate();

  const handleGoToChat = () => {
    navigate('/');
  };

  const handleNodeClick = (node: any) => {
    console.log('Nodo clickeado:', node);
  };

  return (
    <div className="container-fluid vh-100 d-flex flex-column">
      <Navbar />
      
      <div className="row flex-grow-1 mt-3">
        {/* Sidebar izquierda */}
        <aside className="col-12 col-md-3 col-lg-2 border-end bg-light p-3 d-flex flex-column">
          <h6 className="text-muted mb-3">Visualizaciones</h6>
          <div className="flex-grow-1 overflow-auto">
            <div className="p-2 mb-2 rounded bg-white shadow-sm small text-truncate border-primary">
              Consulta P1 - Misiones Biológicas
            </div>
            <div className="p-2 mb-2 rounded bg-white shadow-sm small text-truncate">
              Consulta P2 - Exploración Lunar
            </div>
            <div className="p-2 mb-2 rounded bg-white shadow-sm small text-truncate">
              Consulta P3 - Cultivos Espaciales
            </div>
          </div>
          <button 
            className="btn btn-dark mt-3"
            onClick={handleGoToChat}
          >
            ← Volver al Chat
          </button>
        </aside>

        {/* Área principal */}
        <main className="col-12 col-md-9 col-lg-10 d-flex flex-column p-3">
          <NodeVisualization 
            data={[]} 
            onNodeClick={handleNodeClick}
            onGoToChat={handleGoToChat}
          />
        </main>
      </div>
    </div>
  );
};

export default NodeView;
